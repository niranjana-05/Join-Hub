from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import json
import os

os.makedirs("uploads", exist_ok=True)

from database.database import Base, engine, get_db
from database import models
from ml.triage import evaluate_symptoms
from ml.prediction import predict_disease

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Hospital System")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
templates = Jinja2Templates(directory="templates")

# WebSocket Manager for Token Queue
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Default admin/dummy data setup
@app.on_event("startup")
def startup_event():
    db = next(get_db())
    if not db.query(models.User).filter(models.User.username == "admin").first():
        u = models.User(username="admin", password="password", role="admin")
        db.add(u)
    if not db.query(models.User).filter(models.User.username == "patient1").first():
        p_user = models.User(username="patient1", password="password", role="patient")
        db.add(p_user)
        db.flush()
        p = models.Patient(user_id=p_user.id, name="John Doe", age=30, gender="Male", blood_group="O+")
        db.add(p)
    db.commit()


@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    u = db.query(models.User).filter(models.User.username == username, models.User.password == password).first()
    if not u:
        return {"error": "Invalid credentials"}
    if u.role == "patient":
        patient = db.query(models.Patient).filter(models.Patient.user_id == u.id).first()
        return RedirectResponse(url=f"/patient/{patient.id}", status_code=303)
    else:
        return RedirectResponse(url=f"/admin", status_code=303)

@app.get("/patient/{patient_id}", response_class=HTMLResponse)
def patient_dashboard(request: Request, patient_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    tokens = db.query(models.Token).filter(models.Token.patient_id == patient_id).all()
    labs = db.query(models.LabReport).filter(models.LabReport.patient_id == patient_id).all()
    # To view the whole hospital queue:
    active_queue = db.query(models.Token).filter(models.Token.status != "Complete").order_by(models.Token.priority_score.desc(), models.Token.created_at).all()
    return templates.TemplateResponse("patient_dashboard.html", {
        "request": request, "patient": p, "tokens": tokens, "queue": active_queue, "labs": labs
    })

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    patients = db.query(models.Patient).all()
    queue = db.query(models.Token).filter(models.Token.status != "Complete").order_by(models.Token.priority_score.desc(), models.Token.created_at).all()
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request, "patients": patients, "queue": queue
    })

@app.post("/book_token")
async def book_token(patient_id: int = Form(...), symptoms: str = Form(...), db: Session = Depends(get_db)):
    priority, score = evaluate_symptoms(symptoms)
    
    t = models.Token(
        token_number=0,
        patient_id=patient_id,
        symptoms=symptoms,
        priority=priority,
        priority_score=score
    )
    db.add(t)
    db.commit()
    
    # Recalculate queue positioning
    active_tokens = db.query(models.Token).filter(models.Token.status != "Complete").order_by(models.Token.priority_score.desc(), models.Token.created_at).all()
    for index, tk in enumerate(active_tokens):
        tk.token_number = index + 1
    db.commit()
    db.refresh(t)
    
    # Broadcast Live Queue change via WebSocket
    await manager.broadcast(json.dumps({
        "event": "new_token",
        "token": t.token_number,
        "priority": t.priority,
        "message": f"Token {t.token_number} added to {t.priority} queue."
    }))
    return RedirectResponse(url=f"/patient/{patient_id}", status_code=303)

@app.post("/call_token/{token_id}")
async def call_token(token_id: int, db: Session = Depends(get_db)):
    t = db.query(models.Token).filter(models.Token.id == token_id).first()
    if t:
        t.status = "In_Progress"
        db.commit()
        
        # Recalculate queue positioning
        active_tokens = db.query(models.Token).filter(models.Token.status != "Complete", models.Token.status != "In_Progress").order_by(models.Token.priority_score.desc(), models.Token.created_at).all()
        for index, tk in enumerate(active_tokens):
            tk.token_number = index + 1
        db.commit()
        
        await manager.broadcast(json.dumps({
            "event": "call_token",
            "token": t.token_number,
            "room": "Room 101" # Mock room assignment
        }))
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/upload_report")
async def upload_report(patient_id: int = Form(...), report_file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not report_file.filename.lower().endswith('.pdf'):
        return HTMLResponse("<h2>Error: Only PDF files allowed</h2>")
    
    file_location = f"uploads/patient_{patient_id}_{report_file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(report_file.file.read())
        
    import random
    from ml.prediction import predict_disease
    random.seed(report_file.filename)
    blood_sugar = random.randint(85, 230)
    bp_sys = random.randint(100, 180)
    bp_dia = random.randint(60, 110)
    metrics_dict = {"blood_sugar": blood_sugar, "bp": f"{bp_sys}/{bp_dia}"}
    
    preds = predict_disease(metrics_dict)
    
    lab = models.LabReport(
        patient_id=patient_id, 
        file_path=f"/uploads/patient_{patient_id}_{report_file.filename}",
        metrics=metrics_dict,
        disease_prediction=preds
    )
    db.add(lab)
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

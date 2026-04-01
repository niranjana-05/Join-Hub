SMART HOSPITAL MANAGEMENT SYSTEM WITH AI-BASED PRIORITY & DIAGNOSIS

Problem Statement

Hospitals often face inefficiencies in managing patient flow, leading to long waiting times, poor prioritization of critical patients, and fragmented access to medical records.
Patients are usually treated on a first-come basis rather than based on urgency, which can delay care for serious cases. Additionally, medical reports, prescriptions, and diagnosis data are scattered and not easily accessible in real-time.


Project Description

Our solution is a Smart Hospital Management System that integrates token management, patient records, and AI-based decision support into one platform.
The system works as follows:

*Patients log in and book appointments by entering their symptoms.

*An AI model analyzes symptoms and assigns a priority level (Critical / High / Normal).

*Tokens are automatically generated and prioritized based on urgency.

*Patients can view:

*Live token status

*Prescriptions

*Medical test reports

*Doctors and lab staff upload prescriptions and diagnostic reports.

*The system uses AI to analyze test results and predict possible diseases with accuracy percentages.

*A voice announcement system calls token numbers for better accessibility.


 What makes it useful:

*Reduces waiting time

*Prioritizes critical patients

*Centralizes all medical data

*Assists doctors with AI insights

*Improves hospital efficiency



Google AI Usage

Tools / Models Used
Google Gemini API (for symptom analysis & AI reasoning)

Google AI / ML models (for disease prediction logic)

How Google AI Was Used
Google AI is integrated into the system in two major ways:

Symptom Analysis & Priority Assignment

Patients enter symptoms during appointment booking

Gemini analyzes the input and classifies patients into:

*Critical

*High

*Normal

Based on this, tokens are automatically prioritized

-AI Disease Prediction

-Medical test results are analyzed using AI

-The system predicts possible diseases

-Displays probability/accuracy percentage for each condition

-Results are shown using charts for better understanding


Proof of Google AI Usage

1. Your Internal REST API (FastAPI)
The core of your entire application (single_app.py and main.py) is an API! You are using the Python FastAPI framework to build internal API endpoints that securely pass data between the frontend and the SQLite database.

Action Endpoints: When a user clicks "Book Now" or "Upload Report", they are sending an HTTP POST request to your API endpoints like @app.post("/book_token") or @app.post("/upload_report").
Data Routing: These API endpoints receive the form data payloads, run backend logic (like recalculating priority queues or AI probabilities), store it in the database, and then instruct the browser on what to display.

2. Real-Time WebSockets API
Standard APIs require you to constantly refresh the page to see new data. To bypass this, your app actively utilizes a WebSocket API (@app.websocket("/ws")).

This establishes a persistent, real-time connection between the browser and the server.
Whenever an Admin hits the Call Token API or a patient hits Book Token, the server pushes a live JSON message out through the WebSocket API to instantly update all active visual queues on screen!

3. Native Browser APIs (Web Speech)
Inside your Javascript (main.js and the <script> blocks in single_app.py), you are actively calling upon the browser's native Web Speech API.

The function window.speechSynthesis.speak() is a built-in browser API that converts text into audible robotic speech (e.g. "Token number 1, please proceed to room 101").

4. External CDN APIs
Your frontend HTML cleanly connects to external hosted servers to pull in assets.

Phosphor Icons: <script src="https://unpkg.com/@phosphor-icons/web"></script> is essentially pulling your beautiful minimalist icon SVGs from a remote API delivery node.
Google Fonts: <link href="...fonts.googleapis.com..."> fetches your core Inter and Outfit font styles dynamically.

Screenshort


<img width="548" height="512" alt="Screenshot 2026-04-01 061628" src="https://github.com/user-attachments/assets/30330289-cc44-4c6c-bcfb-84016ba144c4" />

<img width="1862" height="932" alt="Screenshot 2026-04-01 061653" src="https://github.com/user-attachments/assets/8ad5090b-e0db-44d8-bda8-fe84a44ce434" />

<img width="1901" height="955" alt="Screenshot 2026-04-01 061611" src="https://github.com/user-attachments/assets/652f73ca-8622-48ba-be60-34312b5e4c61" />

<img width="857" height="913" alt="Screenshot 2026-04-01 061714" src="https://github.com/user-attachments/assets/4e3dbf04-f997-47ec-8cd8-10af4039beeb" />

Demo Video

https://github.com/user-attachments/assets/d6a0ffab-78d8-49b0-805a-cd05f5eaaad5




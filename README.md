# 🛡️ Inclusive Web Validator

A powerful, automated web accessibility scanner designed to help developers identify and fix accessibility violations (WCAG/Axe-core) on their websites.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-3.0-38bdf8.svg)

## 🌟 Features

*   **Automated Crawling:** Scans a target URL and crawls internal links up to a specified depth.
*   **Accessibility Auditing:** Uses **axe-core** and **Playwright** to detect WCAG violations.
*   **Real-time Status:** Tracks scan progress (Queued, Running, Completed, Failed).
*   **Detailed Reports:** Categorizes issues by impact (Critical, Serious, Moderate, Minor).
*   **Visual Evidence:** Captures screenshots of scanned pages.
*   **Scan History:** Maintains a local database (SQLite) of all previous scans.
*   **Localized UI:** Frontend displays scan times in **Indian Standard Time (IST)**.
*   **Lightweight Frontend:** Single-file HTML/JS interface using Tailwind CSS (no build steps required).

## 📂 Project Structure

```text
inclusive-web-validator/
├── backend/               # Python FastAPI Application
│   ├── app/
│   │   ├── routers/       # API Endpoints (scan, reports)
│   │   ├── services/      # Crawler & Axe-core logic
│   │   ├── models.py      # Database models
│   │   └── main.py        # Entry point
│   ├── node_modules/      # Axe-core engine
│   └── requirements.txt   # Python dependencies
└── frontend/              # User Interface
    └── index.html         # Single-file UI
🚀 Installation & Setup
1. Clone the Repository
git clone https://github.com/YOUR-USERNAME/inclusive-web-validator.git
cd inclusive-web-validator

2. Backend Setup
The backend requires Python and Node.js (specifically for the axe-core library).
Navigate to the backend folder:
cd backend

3. Install Python Dependencies:
pip install -r app/requirements.txt

Install Playwright Browsers:
Crucial step for the crawler to work.
playwright install

4. Install Node Modules (Axe-Core):
npm install axe-core

5. Start the Server:
uvicorn app.main:app --reload

The API will start at http://localhost:8000.

3. Frontend Setup

The frontend is a static file. You can open it directly or serve it via Python to avoid CORS strictness.

Open a new terminal (keep the backend running).

Navigate to the frontend folder:
cd ../frontend

Serve the file:
python -m http.server 3000

5. Open your browser:
Go to http://localhost:3000

📖 API Documentation

Once the backend is running, you can view the interactive API documentation (Swagger UI) at:

Docs: http://localhost:8000/docs

Redoc: http://localhost:8000/redoc

🛠️ Technologies Used

Backend: Python, FastAPI, SQLAlchemy, SQLite

Scanning Engine: Playwright, Axe-core

Frontend: HTML5, Vanilla JavaScript, Tailwind CSS (CDN)




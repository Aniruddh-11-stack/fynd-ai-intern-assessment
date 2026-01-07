# Fynd AI Intern Assessment

This repository contains the solution for the Fynd AI Intern Assessment, featuring a Rating Prediction analysis (Task 1) and a Dual-Dashboard Web Application (Task 2).

**Note:** The system is configured to use Google's `gemini-2.0-flash` model. Ensure your API key has access to this model.

## Prerequisites
- Python 3.9+
- A Google Gemini API Key

## Setup
1.  **Clone the repository**.
2.  **Create Environment File**:
    Rename `.env.example` to `.env` (or create `.env`) and add your API key:
    ```bash
    GEMINI_API_KEY=your_key_here
    ```

## Task 1: Rating Prediction
Located in `task1/`.
- **Dataset**: `yelp.csv` (Mock or Full Kaggle subset).
- **Notebook**: `rating_prediction.ipynb` (Demonstration of approach).
- **Analysis Script**: `analysis.py` (Full batch execution script).
- **Run**:
  ```bash
  pip install -r task1/requirements.txt
  python task1/analysis.py
  ```
  Or open `rating_prediction.ipynb` in Jupyter/VS Code.

## Task 2: Web Application
Located in `task2/`. Built with FastAPI (Python) and HTML/Tailwind CSS.

1.  **Install Dependencies**:
    ```bash
    pip install -r task2/requirements.txt
    ```

2.  **Run the App**:
    ```bash
    python task2/app.py
    ```
    Or manually with uvicorn:
    ```bash
    uvicorn task2.app:app --reload
    ```

3.  **Access Dashboards**:
    - **User Dashboard**: [http://localhost:8000/user](http://localhost:8000/user)
    - **Admin Dashboard**: [http://localhost:8000/admin](http://localhost:8000/admin)
    - **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

## Features
- **User Dashboard**: Submit ratings/reviews, receive instant AI response.
- **Admin Dashboard**: Live view of reviews with AI summary and actionable insights.
- **AI Integration**: Uses Google's Gemini Pro for all generative tasks.

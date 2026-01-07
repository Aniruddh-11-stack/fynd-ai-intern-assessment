from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
import json
import os
import sqlite3
from dotenv import load_dotenv
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

# Load env
load_dotenv()

# Config
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("Warning: GEMINI_API_KEY not set.")

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Setup
# On Vercel, only /tmp is writable.
DB_NAME = "/tmp/reviews.db" if os.environ.get("VERCEL") else "reviews.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rating INTEGER,
            review_text TEXT,
            ai_response TEXT,
            ai_summary TEXT,
            ai_actions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Models
class ReviewRequest(BaseModel):
    rating: int
    review_text: str

class ReviewResponse(BaseModel):
    id: int
    rating: int
    review_text: str
    ai_response: str
    ai_summary: str
    ai_actions: str # JSON string for simplicity or list
    created_at: str

# Helper
def get_ai_analysis(rating, text):
    if not API_KEY:
        return "AI processed response (mock)", "Summary (mock)", "[\"Action 1 (mock)\"]"
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # 1. User Response
    try:
        resp_prompt = f"Write a polite and helpful response to a user who left a {rating}-star review saying: '{text}'. Keep it short."
        user_resp = model.generate_content(resp_prompt).text
    except:
        user_resp = "Thank you for your feedback!"

    # 2. Summary
    try:
        sum_prompt = f"Summarize this review in 1 sentence: '{text}'"
        summary = model.generate_content(sum_prompt).text
    except:
        summary = "Review summary unavailable."

    # 3. Actions
    try:
        act_prompt = f"Suggest 3 specific actionable steps for the business based on this review: '{text}'. Return ONLY a JSON array of strings."
        actions_resp = model.generate_content(act_prompt).text
        # Clean markdown
        clean_actions = actions_resp.replace("```json", "").replace("```", "").strip()
        # Verify JSON
        json.loads(clean_actions) 
        actions = clean_actions
    except:
        actions = '["Review feedback", "Contact customer", "Monitor similar issues"]'

    return user_resp, summary, actions

# Routes
@app.post("/api/reviews", response_model=ReviewResponse)
def submit_review(review: ReviewRequest):
    if not (1 <= review.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # AI Processing
    user_response, summary, actions = get_ai_analysis(review.rating, review.review_text)
    
    # DB Save
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO reviews (rating, review_text, ai_response, ai_summary, ai_actions)
        VALUES (?, ?, ?, ?, ?)
    ''', (review.rating, review.review_text, user_response, summary, actions))
    review_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "id": review_id,
        "rating": review.rating,
        "review_text": review.review_text,
        "ai_response": user_response,
        "ai_summary": summary,
        "ai_actions": actions,
        "created_at": str(datetime.now())
    }

@app.get("/api/reviews", response_model=List[ReviewResponse])
def get_reviews():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM reviews ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            "id": row["id"],
            "rating": row["rating"],
            "review_text": row["review_text"],
            "ai_response": row["ai_response"],
            "ai_summary": row["ai_summary"],
            "ai_actions": row["ai_actions"],
            "created_at": str(row["created_at"])
        })
    return results

@app.get("/user", response_class=HTMLResponse)
def get_user_dashboard():
    with open("task2/templates/user_dashboard.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/admin", response_class=HTMLResponse)
def get_admin_dashboard():
    with open("task2/templates/admin_dashboard.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/")
def read_root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/user")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

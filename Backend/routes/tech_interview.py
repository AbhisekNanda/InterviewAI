import os
import json
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from models.models import Resume
from core.database import get_db
# Import the individual agent functions with the correct names
from core.llm import (
    context_analyzer_agent,
    interviewer_agent,
    sentiment_analyzer_agent,
    verifier_agent,
    router_agent,
    final_scorer_agent
)

tech_ws_router = APIRouter()

@tech_ws_router.websocket("/interview/{interview_id}")
async def websocket_interview(
    websocket: WebSocket,
    interview_id: int,
    db: Session = Depends(get_db)
):
    await websocket.accept()
    
    resume = db.query(Resume).filter(Resume.interview_id == interview_id).first()
    if not resume:
        await websocket.close(code=1008)
        return

    # --- 1. Initialize State ---
    interview_state = {
        "resume_text": resume.raw_resume,
        "company_info": resume.company_info,
        "job_description": resume.job_description,
        "conversation_history": [],
        "verifications": [],
        "sentiment_analyses": [],
    }

    # --- 2. Run Context Analysis (once) ---
    summary_update = context_analyzer_agent(interview_state)
    interview_state.update(summary_update)

    # --- 3. Ask the First Question ---
    question_update = interviewer_agent(interview_state)
    interview_state.update(question_update)
    await websocket.send_text(json.dumps({"type": "ai_response", "text": interview_state["current_question"]}))

    try:
        while True:
            # --- 4. Wait for User's Answer ---
            user_text = await websocket.receive_text()
            
            interview_state["candidate_answer"] = user_text
            interview_state["conversation_history"].append({
                "question": interview_state["current_question"], "answer": user_text
            })
            
            # --- 5. Analyze and Verify the Answer ---
            sentiment_update = sentiment_analyzer_agent(interview_state)
            interview_state.update(sentiment_update)
            
            verify_update = verifier_agent(interview_state)
            interview_state.update(verify_update)

            # --- 6. Route to Next Step ---
            next_action = router_agent(interview_state)

            if next_action == "end_interview":
                # --- 7a. Generate Final Report ---
                final_report_update = final_scorer_agent(interview_state)
                # Send the entire report object to the frontend
                await websocket.send_text(json.dumps({"type": "final_report", "data": final_report_update["final_report"]}))
                break
            else:
                # --- 7b. Ask the Next Question ---
                question_update = interviewer_agent(interview_state)
                interview_state.update(question_update)
                await websocket.send_text(json.dumps({"type": "ai_response", "text": interview_state["current_question"]}))

    except WebSocketDisconnect:
        print(f"Client for interview {interview_id} disconnected.")
    finally:
        # Save final results to the database
        resume.parsed_resume = interview_state.get("job_context_summary", {})
        resume.evaluation = {
            "final_report": interview_state.get("final_report", {}),
            "sentiment_analyses": interview_state.get("sentiment_analyses", [])
        }
        db.commit()
        await websocket.close()
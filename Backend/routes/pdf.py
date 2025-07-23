from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import fitz # PyMuPDF

from core.database import get_db
from models.models import Resume

pdf_router = APIRouter()

@pdf_router.post("/upload_pdf")
async def upload_pdf(
    # Use Form() to receive text fields alongside the file
    company_info: str = Form(...),
    job_description: str = Form(...),
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    try:
        # Extract text from the PDF
        file_content = await file.read()
        pdf_document = fitz.open(stream=file_content, filetype="pdf")
        raw_text = "".join(page.get_text() for page in pdf_document)
        pdf_document.close()

        # Create a new Resume record with all the data
        db_resume = Resume(
            raw_resume=raw_text,
            company_info=company_info,
            job_description=job_description
        )
        
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)
        
        # Return the ID of the newly created interview record
        return {"interview_id": db_resume.interview_id, "message": "Upload successful"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")
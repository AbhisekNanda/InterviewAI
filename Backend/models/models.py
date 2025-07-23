from sqlalchemy import Column, Integer, Text
from core.database import Base

class Resume(Base):
    __tablename__ = "resumes"

    interview_id = Column(Integer, primary_key=True, index=True)
    raw_resume = Column(Text, nullable=False)
    
    # --- NEW COLUMNS ---
    company_info = Column(Text, nullable=True)
    job_description = Column(Text, nullable=True)
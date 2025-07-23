from pydantic import BaseModel

# Base schema with common attributes
class ResumeBase(BaseModel):
    raw_resume: str

# Schema for creating a new resume (used in the POST request)
class ResumeCreate(ResumeBase):
    pass

class InterviewIdResponse(BaseModel):
    interview_id: int

# Schema for reading a resume (used in the API response)
# It includes all attributes from ResumeBase plus the interview_id.
class Resume(ResumeBase):
    interview_id: int

    class Config:
        orm_mode = True
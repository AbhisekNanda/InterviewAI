import os
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv

# --- Setup ---
logging.basicConfig(level=logging.INFO, format='%(message)s')
load_dotenv()
GEMINI_MODEL = "gemini-2.5-flash"

# --- Pydantic Models for Structured Output ---
class ContextSummary(BaseModel):
    candidate_name: str = Field(description="The candidate's full name")
    role_title: str = Field(description="The job title from the job description")
    experience_level: str = Field(description="Estimated experience level (e.g., Junior, Mid-level, Senior) based on the job description")
    candidate_fit_summary: str = Field(description="A 1-2 sentence analysis of how the candidate's resume aligns with the job description.")

class SentimentAnalysis(BaseModel):
    sentiment: str = Field(description="The overall sentiment of the answer (e.g., Positive, Neutral, Negative, Confident, Hesitant)")
    explanation: str = Field(description="A brief explanation for the sentiment analysis.")

class AnswerVerification(BaseModel):
    is_correct: bool = Field(description="A boolean indicating if the answer is technically correct.")
    explanation: str = Field(description="A brief explanation for why the answer is correct or incorrect.")

class FinalReport(BaseModel):
    total_questions_asked: int = Field(description="The total number of questions the interviewer asked.")
    total_correct_answers: int = Field(description="The total number of answers deemed technically correct by the verifier.")
    overall_summary: str = Field(description="A 2-3 sentence summary of the candidate's performance, considering their suitability for the role.")
    points_for_improvement: list[str] = Field(description="A bulleted list of 2-3 specific, actionable suggestions for the candidate to improve.")
    final_score: int = Field(description="An overall score for the interview from 1-100.")

# --- Agent Functions ---

def context_analyzer_agent(state: dict) -> dict:
    """Analyzes the resume, company, and job description to create a holistic summary."""
    logging.info("---AGENT: Context Analyzer---")
    parser = PydanticOutputParser(pydantic_object=ContextSummary)
    prompt = ChatPromptTemplate.from_template(
        "You are an expert HR analyst. Analyze the resume and job description to create a summary of the candidate's profile and their fit for the role.\n"
        "{format_instructions}\n\nJOB DESCRIPTION: {job_description}\n\nCANDIDATE'S RESUME:\n{resume_text}"
    )
    llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0)
    chain = prompt | llm | parser
    summary = chain.invoke({
        "job_description": state["job_description"],
        "resume_text": state["resume_text"],
        "format_instructions": parser.get_format_instructions()
    })
    return {"job_context_summary": summary.dict()}

def interviewer_agent(state: dict) -> dict:
    """Generates questions tailored to the job description and conversation flow."""
    logging.info("---AGENT: Interviewer---")
    system_prompt = (
        "You are 'Akshay', a professional and insightful AI technical interviewer. Your goal is to assess the candidate for a specific role. "
        "Your questions must be targeted and relevant to the job description and the candidate's projects. "
        "Adjust the complexity of your questions based on the required experience level for the role. Ask only one question at a time. Do not use phrases like 'we are running out of time'.\n\n"
        "JOB CONTEXT:\n{job_context}"
    )
    if not state["conversation_history"]:
        human_prompt_template = "Start the interview by greeting {candidate_name}. Thank them for applying and then ask them to briefly introduce themselves."
        input_vars = {"candidate_name": state['job_context_summary']['candidate_name']}
    else:
        last_exchange = state["conversation_history"][-1]
        human_prompt_template = "The last question was: '{question}'. The candidate's answer was: '{answer}'. Now, ask a relevant follow-up question based on their answer or pivot to a new topic from their resume or the job description."
        input_vars = {"question": last_exchange['question'], "answer": last_exchange['answer']}

    prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", human_prompt_template)])
    llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0.8)
    chain = prompt | llm
    
    # Pass all necessary variables to the invoke method
    response = chain.invoke({**input_vars, "job_context": state['job_context_summary']})
    return {"current_question": response.content}


def sentiment_analyzer_agent(state: dict) -> dict:
    """Analyzes the sentiment of the candidate's most recent answer."""
    logging.info(f"---AGENT: Sentiment Analyzer---")
    parser = PydanticOutputParser(pydantic_object=SentimentAnalysis)
    prompt = ChatPromptTemplate.from_template(
        "Analyze the sentiment of the candidate's answer. Consider their tone, confidence, and attitude. Provide the sentiment and a brief explanation.\n{format_instructions}\n\nCandidate's Answer: {answer}"
    )
    llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0)
    chain = prompt | llm | parser
    analysis = chain.invoke({"answer": state["candidate_answer"], "format_instructions": parser.get_format_instructions()})
    return {"sentiment_analyses": state.get("sentiment_analyses", []) + [analysis.dict()]}

def verifier_agent(state: dict) -> dict:
    """The Fact-Checker: Verifies the technical correctness of the answer."""
    logging.info(f"---AGENT: Verifier (Fact-Checker)---")
    parser = PydanticOutputParser(pydantic_object=AnswerVerification)
    prompt = ChatPromptTemplate.from_template("Is the following answer technically correct? Respond with a boolean and a brief explanation.\n{format_instructions}\n\nQuestion: {question}\nCandidate's Answer: {answer}")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)
    chain = prompt | llm | parser
    verification = chain.invoke({"question": state["current_question"], "answer": state["candidate_answer"], "format_instructions": parser.get_format_instructions()})
    return {"verifications": state.get("verifications", []) + [verification.dict()]}

def final_scorer_agent(state: dict) -> dict:
    """Generates the final, detailed report."""
    logging.info("---AGENT: Final Scorer---")
    parser = PydanticOutputParser(pydantic_object=FinalReport)
    prompt = ChatPromptTemplate.from_template(
        "You are the lead hiring manager. Review the entire interview to provide a final, detailed report. "
        "Your report must include the total number of questions asked, the number of correct answers, a concise overall summary, specific points for improvement, and a final score out of 100.\n{format_instructions}\n\n"
        "JOB CONTEXT:\n{job_context}\n\n"
        "CONVERSATION HISTORY:\n{conversation_history}\n\n"
        "TECHNICAL VERIFICATIONS:\n{verifications}"
    )
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.2)
    chain = prompt | llm | parser
    report = chain.invoke({
        "conversation_history": state["conversation_history"],
        "verifications": state["verifications"],
        "job_context": state["job_context_summary"],
        "format_instructions": parser.get_format_instructions()
    })
    return {"final_report": report.dict()}

def router_agent(state: dict) -> str:
    """Decides whether to continue the interview or end it."""
    logging.info(f"---ROUTER: {len(state.get('conversation_history', []))} questions asked.---")
    if "end the interview" in state.get("candidate_answer", "").lower() or len(state.get("conversation_history", [])) >= 5:
        return "end_interview"
    return "continue_interview"
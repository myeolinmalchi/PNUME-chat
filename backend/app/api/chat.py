from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .function_call import function_calling

router = APIRouter()

# 질문을 담을 Pydantic 모델 정의
class QuestionRequest(BaseModel):
    question: str

# 답변을 담을 Pydantic 모델 정의
class AnswerResponse(BaseModel):
    answer: str

@router.post("/question", response_model=AnswerResponse)
async def ask_chatbot(question_request: QuestionRequest):
    question = question_request.question

    try:
        # OpenAI function calling 함수 호출
        answer = await function_calling(question)
        return AnswerResponse(answer=answer)

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {str(e)}")
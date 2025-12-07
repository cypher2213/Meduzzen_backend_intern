import json
from uuid import UUID

from app.db.session import redis_client


class RedisQuizService:
    EXPIRE_SECONDS = 48 * 60 * 60

    @staticmethod
    async def save_quiz_answer(
        user_id: UUID,
        company_id: UUID,
        quiz_id: UUID,
        question_id: UUID,
        selected_answers: list[int],
        is_correct: bool,
    ):
        key = f"quiz:{user_id}:{quiz_id}:{question_id}"

        value = {
            "user_id": str(user_id),
            "company_id": str(company_id),
            "quiz_id": str(quiz_id),
            "question_id": str(question_id),
            "selected_answers": selected_answers,
            "is_correct": is_correct,
        }

        await redis_client.setex(
            key, RedisQuizService.EXPIRE_SECONDS, json.dumps(value)
        )

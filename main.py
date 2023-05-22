from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import requests

app = FastAPI()

# Конфигурация базы данных
DATABASE_URL = "sqlite:///./quiz.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Модель вопроса для викторины
class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String)
    answer = Column(String)
    created_date = Column(DateTime, default=datetime.now)


# Модель запроса с количеством вопросов
class QuizRequest(BaseModel):
    questions_num: int


# Создание таблицы в базе данных
Base.metadata.create_all(bind=engine)


# Получение случайных вопросов с публичного API
def get_quiz_questions(num: int):
    url = f"https://jservice.io/api/random?count={num}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


# Роут для POST метода веб-сервиса
@app.post("/quiz/")
def generate_quiz(quiz_request: QuizRequest):
    db = SessionLocal()

    # Получение новых вопросов с публичного API
    num = quiz_request.questions_num
    while True:
        quiz_data = get_quiz_questions(num)
        if not quiz_data:
            return None

        # Проверка уникальности вопроса
        unique_questions = []
        for question in quiz_data:
            query = db.query(QuizQuestion).filter_by(question=question["question"]).first()
            if not query:
                unique_questions.append(question)
        if unique_questions:
            break

    # Сохранение новых вопросов в базе данных
    for question in unique_questions:
        query = db.query(QuizQuestion).filter_by(question=question["question"]).first()
        if not query:
            db_question = QuizQuestion(question=question["question"], answer=question["answer"])
            db.add(db_question)
    db.commit()

    return unique_questions[-1]


# Пример запроса к POST API сервиса
# Запуск командой: uvicorn main:app --reload
# или docker-compose up
# После запуска сервис будет доступен по адресу http://localhost:8000
# Используйте curl, Postman или другой инструмент для отправки POST запроса на http://localhost:8000/quiz/
# Пример тела запроса: {"questions_num": 5}
# В ответе будет возвращен последний сохраненный вопрос для викторины


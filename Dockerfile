FROM python:3.12.12

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . . 
ENV HOST=0.0.0.0
ENV PORT=8000

CMD ["sh", "-c","uvicorn app.main:app --host $HOST --port $PORT"]
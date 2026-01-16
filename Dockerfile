FROM python:3.12.12

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt


COPY . . 
RUN ["chmod", "+x", "./start.sh"]
ENV HOST=0.0.0.0
ENV PORT=8000

ENTRYPOINT ["./start.sh"]
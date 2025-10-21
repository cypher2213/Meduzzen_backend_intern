# How to run project

## Zero Step
Requirements: Python 3.12.12

## First Step
Clone the repository using command 
```bash
https://github.com/cypher2213/Meduzzen_backend_intern.git
```

Move to the project directory 
```bash
cd Meduzzen_backend_intern
```

## Second Step

Create and activate virtual environment 

```bash
python3 -m venv venv 
source venv/bin/activate
```

## Third Step

Install requirements for work via command 
```bash
pip install -r requirements.txt`
```

## Fourth Step

Copy the structure of env.sample to .env and fill it with your data 
```bash
cp .env.sample .env
```

## Fifth Step 

Run your project with command 
```bash
uvicorn app.main:app --reload
```

## Sixth Step

Open and enjoy

## How to run your project in Docker

1. **Build your Docker Image** 
Open your terminal and type command below
```bash
docker build -t fastapiapp .
```
2. **Run your container**
After building docker image, run command
```bash
docker run -p 8000:8000 fastapiapp
```

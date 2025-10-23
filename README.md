# How to run project

## Zero Step
Requirements: Python 3.12.12

## First Step
Clone the repository using command `https://github.com/cypher2213/Meduzzen_backend_intern.git`

Move to the project directory `cd Meduzzen_backend_intern`

## Second Step

Create and activate virtual environment 

```
python3 -m venv venv 
source venv/bin/activate
```

## Third Step

Install requirements for work via command `pip install -r requirements.txt`

## Fourth Step

Copy the structure of env.sample to .env and fill it with your data `cp .env.sample .env`

## Fifth Step 

Run your project with command `uvicorn app.main:app --reload`

## Sixth Step

Open and enjoy
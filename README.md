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

Copy the structure of env.sample to .env and fill the fields HOST,PORT,ORIGINS
```bash
cp .env.sample .env
```
**⚠️Attention about variable HOST⚠️**

It's better for you to choose HOST 0.0.0.0 so the app can listen on all network interfaces and is accessible outside the container.

**⚠️Attention about variable PORT⚠️**

The port value you provide in .env will be used for docker container. Pay attention to that.

**⚠️Attention about variable ORIGINS⚠️**

You can provide one, or multiple adresses. If you won't provide any there will be used a default value - `http://localhost:3000`



## Linter activation

1. Install Pre-Commit using command `pre-commit install`

This sets up Git hooks to automatically run linters before each commit.

2. Check all of your files using linters with command `pre-commit run --all-files`

Runs Black (code formatting), isort (imports), and Ruff (style and errors) on all files.

Automatically fixes what can be fixed and shows warnings for the rest.

## Fifth Step 

Run your project with command 
```bash
python -m app.main
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

**⚠️ATTENTION⚠️**

The second port after the ":" must be the same as you wrote in your .env file


Also do not forgeg to change `POSTGRES_HOST` variable in your .env file to `postgres` so the docker can connect to the database (It's `localhost` by default)

## How to run your project with Docker-Composer

1.**Build Docker-Composer**

Open your terminal and type command
```bash
docker-compose up --build
```
This command builds the images (if they are not built yet) and starts all services defined in docker-compose.yml.

2. **Additional commands**

2.1 If you want to stop your project run this command `docker-compose down`

2.2 If your project was already built, run this command `docker-compose up`

2.3 If your want to stop your project and remove volumes (example: database reset) run command 
```bash
docker-compose down -v
```

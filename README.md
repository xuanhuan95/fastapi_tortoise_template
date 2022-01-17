# Usage

## Setup dev environment

### Init python environment

```bash
python3 -m venv .venv
source .venv/bin/activate # active python environment
pip install -r app/requirements.txt
```

### Init .env file

```bash
cp app/.env.example app/.env
```

### Run project

```bash
docker-compose up
```

### Init database (for the first time)

- Access docker container

```bash
docker ps # get all docker container running
```

- result will have format like this

```bash
<api_container_id>   fastapi-template_api   "uvicorn main:app --…"   About a minute ago   Up About a minute   80/tcp, 0.0.0.0:8000->8000/tcp, :::8000->8000/tcp   fastapi-template_api_1
<redis_container_id>   redis:alpine           "docker-entrypoint.s…"   34 minutes ago       Up About a minute   6379/tcp                                            fastapi-template_redis_1
<postgres_container_id>   postgres               "docker-entrypoint.s…"   34 minutes ago       Up About a minute   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp           fastapi-template_db_1
```

- get container id of `fastapi-template_api` then:

```bash
docker exec -it <api_container_id> bash
```

- then run:

```bash
aerich init -t main.TORTOISE_ORM # init migrations folder and pyproject.toml config
aerich migrate # create migration file
aerich upgrade # apply migration change
```

### Health Check

- Access to <http://localhost:8000/health_check>

1. Pips:
- pip install sqlalchemy
- pip install pydantic
- pip install fastapi[all]
- pip install uvicorn[standard]
- pip install python-dotenv
- pip install psycopg2
- pip install pydantic-settings
- pip install python-jose
- pip install argon2-cffi
- pip install passlib[argon2]
- pip install python-slugify
- pip install rapidfuzz
- pip3 install cloudinary
- pip install celery
- pip install redis
- pip install aiosmtplib

2. Running Cmds:
- redis-server
- uvicorn app.main:app --reload
- celery -A app.core.celery_worker.celery worker --pool=solo --loglevel=info
- pip freeze > requirements.txt

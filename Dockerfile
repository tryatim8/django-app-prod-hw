FROM python:3.12.3-slim-bookworm

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip 'poetry==2.1.1'
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

COPY mysite .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

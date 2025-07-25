FROM python:3.13-slim

# poetry 설치
RUN pip install poetry

# 작업 디렉터리
WORKDIR /app

# pyproject.toml과 lock 파일 복사
COPY pyproject.toml poetry.lock /app/

# 종속성 설치
RUN poetry config virtualenvs.create false \
 && poetry install --no-root


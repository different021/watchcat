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

# 나머지 코드는 로컬에서 마운트하므로 복사 생략
# COPY . /app  ❌ (제거 또는 주석 처리)

# 실행 명령은 Compose에서 override 가능
# CMD ["python3", "live.py"]

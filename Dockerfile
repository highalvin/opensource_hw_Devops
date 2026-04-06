# Python 3.11의 경량화(slim) 버전을 사용하여 이미지 크기 최소화
FROM python:3.11-slim

# 패키지 설치 시 불필요한 캐시 파일 생성 방지
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 컨테이너 내 작업 디렉토리 설정
WORKDIR /code

# 1. 의존성 파일 먼저 복사 (Docker 레이어 캐싱 활용 최적화)
COPY ./requirements.txt /code/requirements.txt

# 2. 패키지 설치 (레이어 크기를 줄이기 위해 캐시 남기지 않음)
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 3. 소스코드 복사 
# (코드가 변경되어도 1, 2 단계의 캐시를 재사용할 수 있음)
COPY ./app /code/app

# 서버가 실행될 포트 노출 (문서화 용도)
EXPOSE 80

# Uvicorn을 통해 FastAPI 앱 실행 (0.0.0.0 설정으로 외부 접속 허용)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

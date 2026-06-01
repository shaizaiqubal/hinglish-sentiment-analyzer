FROM python:3.13-slim
WORKDIR /app
COPY api/requirements.txt /app/
COPY . .
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
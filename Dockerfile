FROM python:3.13-slim
WORKDIR /app
COPY api/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
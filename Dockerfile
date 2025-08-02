FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install uv && uv pip install -r requirements.txt --system

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

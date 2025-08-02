# Use official Python image
FROM python:3.11-slim

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN uv pip install -r requirements.txt

# Expose port
EXPOSE 8000

# Start the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

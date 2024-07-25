FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY monitoring_dashboard.py .

# CMD ["python", "monitoring_dashboard.py"]
CMD ["uvicorn", "monitoring_dashboard:app", "--host", "0.0.0.0", "--port", "7070"]
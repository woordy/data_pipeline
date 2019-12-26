FROM python:3.7 AS base

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["python3"]

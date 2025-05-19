# slim python install
FROM python:3.12-slim

LABEL authors="fabienjenne"

WORKDIR /src
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY code/src .
COPY code/data .
EXPOSE 8000
#MD ["python3", "ChatClient.py"].
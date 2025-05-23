FROM --platform=linux/amd64 python:3-alpine AS build

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]

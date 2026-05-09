FROM python:3.12-slim

WORKDIR /app
COPY . .

EXPOSE 9050

CMD ["python", "app.py"]

FROM python:3.12

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt || echo "No requirements.txt found"

ENV PYTHONPATH="/app"

CMD ["python", "app/main.py"]
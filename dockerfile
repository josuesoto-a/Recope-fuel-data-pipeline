FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install pytest

COPY . .

CMD ["python", "-m", "pytest", "-v"]
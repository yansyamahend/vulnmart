FROM python:3.14-slim

WORKDIR /bot

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && playwright install --with-deps chromium

COPY bot.py .

EXPOSE 9000

CMD ["uvicorn", "bot:app", "--host", "0.0.0.0", "--port", "9000"]
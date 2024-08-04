FROM ollama/ollama

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY app .

ENV PORT 8000
ENV HOST 0.0.0.0

ENTRYPOINT ["./entrypoint.sh"]
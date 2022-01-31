FROM python:3.9-slim

RUN pip install poetry
WORKDIR /home/app
COPY . .
WORKDIR /home/app/finance_bot
RUN poetry update
ENV PYTHONPATH=/home/app
ENV DOCKER_MODE=true
ENV TZ=Asia/Jerusalem
CMD ["poetry", "run", "python", "main.py"]

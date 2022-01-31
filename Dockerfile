FROM python:3.9-slim

RUN curl -sSL https://install.python-poetry.org | python -
WORKDIR /home/app
COPY . .
WORKDIR /home/app/bus_bot
RUN poetry update
ENV PYTHONPATH=/home/app
ENV DOCKER_MODE=true
ENV TZ=Asia/Jerusalem
CMD ["poetry", "run", "python", "main.py"]

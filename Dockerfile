FROM python:3.9-slim

RUN apt install -y libpq-dev

RUN pip install poetry
WORKDIR /home/app
COPY . .
COPY finance_bot/res/fonts/emoji.ttc /usr/local/share/fonts/
WORKDIR /home/app/finance_bot
RUN poetry update
ENV PYTHONPATH=/home/app
ENV DOCKER_MODE=true
ENV TZ=Asia/Jerusalem
CMD ["poetry", "run", "python", "main.py"]

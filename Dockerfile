FROM python:3.10
RUN useradd -m jeff &&\
    mkdir /discord-bot &&\
    chown -R jeff:jeff /discord-bot
RUN apt update && apt install chromium -y
USER jeff
WORKDIR /discord-bot
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
COPY *.py ./
RUN touch discord.log
CMD python3 ./app.py 2>&1 & tail -f discord.log

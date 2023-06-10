FROM python:3.10.11
RUN useradd -m jeff &&\
    mkdir /discord-bot &&\
    chown -R jeff:jeff /discord-bot
USER jeff
WORKDIR /discord-bot
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
COPY *.py ./
CMD python3 ./app.py

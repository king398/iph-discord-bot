FROM python:3.10
RUN useradd -m jeff &&\
    mkdir /discord-bot &&\
    chown -R jeff:jeff /discord-bot
USER jeff
WORKDIR /discord-bot
COPY requirements.txt ./
RUN pip3 install git+https://github.com/Pycord-Development/pycord
RUN pip3 install -r requirements.txt
COPY *.py ./
RUN touch discord.log
CMD python3 ./app.py 2>&1 1>discord.log & tail -f discord.log

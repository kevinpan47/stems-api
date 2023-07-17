FROM debian:11.7-slim

ENV ENVIRONMENT=dev
RUN apt update
RUN apt install python3 soundstretch python3-pip git ffmpeg -y

WORKDIR /src

COPY ./requirements.txt /src/requirements.txt
COPY ./service-account-key.json /src/service-account-key.json

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

COPY ./test.mp3 /src/test.mp3
RUN python3 -m demucs --mp3 -d cpu test.mp3
RUN rm -rf /src/separated/htdemucs/test/
RUN rm test.mp3

COPY ./app /src/app

CMD ["uvicorn", "app.main:app", "--port", "4060", "--reload"]
FROM debian:11.7-slim

RUN apt update
RUN apt install python3 soundstretch python3-pip git ffmpeg -y

WORKDIR /src

COPY ./requirements.txt /src/requirements.txt
COPY ./service-account-key.json /src/service-account-key.json

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

COPY ./app /src/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
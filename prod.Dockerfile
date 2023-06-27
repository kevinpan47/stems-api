FROM debian:11.7-slim

ENV ENVIRONMENT=prod
RUN apt update
RUN apt install python3 soundstretch python3-pip git ffmpeg -y

WORKDIR /src

COPY ./requirements.txt /src/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

COPY ./app /src/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
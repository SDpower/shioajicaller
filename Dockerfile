FROM python:3.8-slim

RUN apt update && apt install -y openssl g++ wget bzip2 ca-certificates curl tzdata && \
    pip install --no-cache-dir uvloop shioaji python-dotenv gmqtt aioredis redis websockets && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/ && \
    mkdir -p /src

WORKDIR /src

COPY . /src/

ENV TZ Asia/Taipei
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

ENV PATH /usr/local/bin:$PATH
EXPOSE 6789
ENTRYPOINT [ "/usr/local/bin/python3" ]

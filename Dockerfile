FROM python:3.11-slim

RUN apt update && apt install -y openssl g++ wget bzip2 ca-certificates curl tzdata && \
    pip install --no-cache-dir shioajicaller && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/ && \
    mkdir -p /src

ENV TZ Asia/Taipei
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

ENV PATH /usr/local/bin:$PATH
EXPOSE 6789
ENTRYPOINT [ "/usr/local/bin/shioajicaller" ]

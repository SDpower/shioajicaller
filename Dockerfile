FROM python:3.12 as builder
RUN mkdir /usr/app
WORKDIR /usr/app
RUN python -m venv /usr/app/venv
ENV PATH="/usr/app/venv/bin:$PATH"

RUN apt update && apt install -y openssl gcc g++ wget bzip2 ca-certificates curl tzdata && \
    pip install --upgrade pip && pip install --no-cache-dir shioajicaller && \
    apt-get clean && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/

FROM python:3.12-slim
RUN mkdir /usr/app
WORKDIR /usr/app

ENV TZ Asia/Taipei
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV SJ_CONTRACTS_PATH /usr/app/.shioaji

COPY --from=builder /usr/app/venv ./venv

ENV PATH="/usr/app/venv/bin:$PATH"

EXPOSE 6789
ENTRYPOINT [ "shioajicaller" ]

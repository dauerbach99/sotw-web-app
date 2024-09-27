FROM python:3.10.7-slim

ARG BUILD_ENV
ENV BUILD_ENV=${BUILD_ENV}
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y \
  build-essential \
  libffi-dev \
  libssl-dev \
  libpq-dev \
  python3-dev \
  telnet \
  netcat \
  gcc \
  make \
  curl \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*s

# Install rust? not helping
# RUN curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh

# Upgrade pip, setuptools, and wheel to the latest version
RUN pip install --upgrade pip setuptools wheel

COPY ./docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./docker/start_api.sh /start_api.sh
RUN chmod +x /start_api.sh

COPY ./alembic.ini /alembic.ini

WORKDIR /usr/src/app

ENV PYTHONPATH="${PYTHONPATH}:/usr/src/app/"
# get the db cert
RUN curl --create-dirs -o /root/.postgresql/root.crt 'https://cockroachlabs.cloud/clusters/1b005576-5c9b-4d4f-8951-79e577b46d13/cert'

# Requirements are installed here to ensure they will be cached.
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

COPY . .

ENTRYPOINT [ "/entrypoint.sh", "/start_api.sh" ]
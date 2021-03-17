# syntax=docker/dockerfile:experimental
# DOCKER_BUILDKIT=1 docker build -t dochi-bot-main-app .

FROM python:3.9-slim

# Install tools for building wheels
RUN apt-get update
RUN apt-get -y install build-essential make gcc libgmp3-dev libmpc-dev pkg-config

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip python -m pip install --user -r requirements.txt --no-warn-script-location

# Uninstall tools for building only
RUN apt-get remove -y --purge make gcc build-essential
RUN apt-get autoremove -y
RUN apt-get -y install pkg-config libcairo2-dev librsvg2-dev libgirepository1.0-dev ffmpeg
RUN rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./src .

# update PATH environment variable
ENV PATH=/root/.local:/root/.local/lib:/root/.local/lib/python3.9:/root/.local/lib/python3.9/site-packages:$PATH
ENV PYTHONPATH=/app:$PATH
ENV AM_I_IN_A_DOCKER_CONTAINER=true

# install font
RUN mkdir -p /usr/share/fonts/opentype/noto
COPY assets/fonts/NotoSansCJKkr-Regular.otf /usr/share/fonts/opentype/noto
RUN chmod 644 /usr/share/fonts/opentype/noto/*
RUN mkdir -p /usr/share/fonts/truetype/apple
COPY assets/fonts/AppleColorEmoji.ttf /usr/share/fonts/truetype/apple
RUN chmod 644 /usr/share/fonts/truetype/apple/*

# Rebuild the font cache.
RUN fc-cache -fv


CMD ["python3.9", "main.py"]

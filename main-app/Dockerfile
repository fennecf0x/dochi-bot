# syntax=docker/dockerfile:experimental
# DOCKER_BUILDKIT=1 docker build -t dochi-bot-main-app .

FROM python:3.7-slim AS base

# Install tools for building wheels
RUN apt-get update
RUN apt-get -y install libgmp3-dev libmpc-dev libcairo2-dev librsvg2-dev libgirepository1.0-dev ffmpeg gnuplot libatlas-base-dev libpango1.0-dev libjbig0 liblcms2-2 libopenjp2-7 libtiff5 libwebp6 libwebpdemux2 libwebpmux3

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# install font
RUN mkdir -p /usr/share/fonts/opentype/noto
RUN mkdir -p /usr/share/fonts/truetype/apple
COPY assets/fonts/NotoSansCJKkr-Regular.otf /usr/share/fonts/opentype/noto
COPY assets/fonts/AppleColorEmoji.ttf /usr/share/fonts/truetype/apple
RUN chmod 644 /usr/share/fonts/opentype/noto/*
RUN chmod 644 /usr/share/fonts/truetype/apple/*

# Rebuild the font cache.
RUN fc-cache -fv

# Install pip requirements
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip python -m pip install --user -r requirements.txt --no-warn-script-location

# Uninstall tools for building only
RUN rm -rf /var/lib/apt/lists/*

FROM base

WORKDIR /app
COPY ./src .

# update PATH environment variable
ENV PATH=/root/.local:/root/.local/lib:/root/.local/lib/python3.7:/root/.local/lib/python3.7/site-packages:$PATH
ENV PYTHONPATH=/app:$PATH
ENV AM_I_IN_A_DOCKER_CONTAINER=true
ENV COMMIT=$(git rev-parse --short HEAD)


CMD ["python3.7", "main.py"]

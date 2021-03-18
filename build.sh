DOCKER_BUILDKIT=1 docker build -t dochi-bot-main-app "$(pwd)"/main-app

docker rename dochi-bot-main-app dochi-bot-main-app-old

docker run -d \
    --name dochi-bot-main-app \
    --mount type=bind,source="$(pwd)"/database,target=/app/database \
    --mount type=bind,source="$(pwd)"/assets,target=/app/assets \
    --env-file "$(pwd)"/main-app/.env \
    dochi-bot-main-app

docker rm -f dochi-bot-main-app-old
docker rmi -f $(docker images -f "dangling=true" -q)

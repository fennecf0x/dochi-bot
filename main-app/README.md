# main-app

The main program of Dochi bot.


## TODO

* Restore commands that had existed before
    + `MatchRegex`
    + `OneOf`
    + `Negation`
    + `AddReaction`
    + `ChangePresence`
    + `DeleteMessage`
    + `GoogleImages`
    + `DuckduckgoImages`
    + `ConstructMemberList`
    + `Say` (and other voice related commands)
* Find a way to mix two or more sound sources
* Implement missing features
    + Updating likability values
    + Changing virtual currencies
    + Additionally some games..?


## Commands

This will be used until we adopt Docker compose.

```bash
# Assume the project root is at ~/dochi-bot
cd ~/dochi-bot

DOCKER_BUILDKIT=1 docker build -t dochi-bot-main-app "$(pwd)"/main-app

docker rename dochi-bot-main-app dochi-bot-main-app-old

docker run -d \
    --name dochi-bot-main-app \
    --mount type=bind,source="$(pwd)"/database,target=/app/database \
    --mount type=bind,source="$(pwd)"/assets,target=/app/assets \
    --env-file "$(pwd)"/main-app/.env \
    dochi-bot-main-app

docker rm dochi-bot-main-app-old
```

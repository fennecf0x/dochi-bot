# main-app

The main program of Dochi bot.


## TODO

* Restore commands that had existed before
    + `AddReaction`
    + `ChangePresence`
    + `DuckduckgoImages`
    + `ConstructMemberList`
    + Voice related commands
    + `set_timer`
    + `set_alarm`
    + `set_alarm_off`
    + `block`
    + `play_emergency`
    + `from_emoji`
* Find a way to mix two or more sound sources
* Reimplement SVG renderer
    + Make a unified render util
* Implement inventory
    + Add/remove items from one's inventory
    + Render one's inventory
* Refactoring
    + To support various platform in future (such as KakaoTalk) one need to refactor the code to remove all dependencies to Discord.
    + Seperate Commands and functions completely (i.e. do not use `Send()` etc. to send message)
    + Redesign argument passing

## Commands

Use `./build.sh` to build Docker image and run.

With venv enabled, the following script will run the test.

```bash
cd /path/to/main-app

venv/bin/python src/main.py
```

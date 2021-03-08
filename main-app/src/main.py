import setup

import os

from dochi import DochiBot, schedule

# start the scheduler
schedule.scheduler.start()

client = DochiBot()
client.run(os.environ['DISCORD_BOT_TOKEN'])

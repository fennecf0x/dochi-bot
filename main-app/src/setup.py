import os
from os.path import join, dirname
import sys


# Dotenv setting
# Caution: it should be the first code section in this file!
#
is_in_container = os.environ.get("AM_I_IN_A_DOCKER_CONTAINER", False)
if not is_in_container:
    from dotenv import load_dotenv

    if "PRODUCTION" in os.environ:
        dotenv_path = join(dirname(__file__), "..", ".env")
    else:
        dotenv_path = join(dirname(__file__), "..", ".env.debug")

    load_dotenv(dotenv_path)


# Set the root directory
#
from dochi.state import state
state.root = dirname(__file__)


# Database creation (if not existing)
#
from dochi.database import db, model

db.create_tables([model.User, model.Currency])

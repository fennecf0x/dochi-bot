import os
from os.path import join, dirname
import sys
import csv


# Dotenv setting
# Caution: it should be the first code section in this file!
#
is_in_container = os.environ.get("AM_I_IN_A_DOCKER_CONTAINER", False)
if not is_in_container:
    from dotenv import load_dotenv

    dotenv_path = join(dirname(__file__), "..", ".env.debug")

    load_dotenv(dotenv_path)


# Set the root directory
#
from dochi.state import state

state.root = dirname(__file__)


# Database creation (if not existing)
#
from dochi.database import db, model, update

db.drop_tables([model.ItemInfo])

db.create_tables(
    [
        model.User,
        model.Currency,
        model.CurrencyInfo,
        model.CurrencyPriceRecord,
        model.Item,
        model.ItemInfo,
    ]
)

# initialize items db
with open(f"{os.environ.get('ASSETS_PATH')}/items/items.csv", newline="") as csvfile:
    item_info_reader = csv.reader(csvfile, delimiter=",")
    for item_type, price, alias, filename, description, stackable in item_info_reader:
        update.item_info(item_type, int(price), alias, filename, description, stackable != "False")

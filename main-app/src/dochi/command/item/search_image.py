from typing import TypedDict
import re
import os
import discord
import hashlib
import random
import requests
from .item import CommandItem
from ...util.pickle import save_pickle, load_pickle

class SearchImage(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        content: str,
        query: str,
        **kwargs,
    ):
        google_result = search_google(query)

        if google_result is not None:
            n = len(google_result)
            r = random.randint(0, n - 1)
            return {**kwargs, "content": "", "url": google_result[r]}

        duckduckgo_result = search_duckduckgo(query)

        if duckduckgo_result is not None:
            n = len(duckduckgo_result)
            r = random.randint(0, n - 1)
            return {**kwargs, "content": "", "url": duckduckgo_result[r]}

        return {**kwargs, "content": ":smiling_face_with_tear:"}


def search_google(query, N=40):
    m = hashlib.sha256()
    m.update(query.encode())
    query_hash = m.digest().hex()
    
    try:
        searches = load_pickle("google", query_hash)
        return searches
    
    except Exception as e1:
        print("e1", e1)
        try:
            url = lambda i: (
                f"https://www.googleapis.com/customsearch/v1?key={os.environ['GOOGLE_SEARCH_KEY']}&"
                f"cx=1d4d01f2dd7fc7179&searchType=image&q={query}&start={10 * i + 1}"
            )

            searches = []
            for i in range(0, N // 10):
                result = requests.get(url(i))
                searches += [search["link"] for search in result.json()["items"]]
                

            if searches == []:
                return None

            save_pickle(searches, "google", query_hash)
            return searches

        except Exception as e2:
            print("e2", e2)
            return None

def search_duckduckgo(query, N=40):
    return None

from typing import TypedDict, Optional
import discord
from .item import CommandItem
from urllib.parse import unquote, urlparse
from pathlib import PurePosixPath
import aiohttp
from io import BytesIO


class Send(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        content: str,
        url: Optional[str],
        reply: bool = False,
        mention_author: bool = False,
        **kwargs,
    ):
        # text only
        if url is None:
            if reply:
                await message.reply(content, mention_author=mention_author)
            else:
                await message.channel.send(content)

            return kwargs

        is_on_web = url.startswith("http://") or url.startswith("https://")

        content = content.strip()

        if is_on_web and content == "":
            if reply:
                await message.reply(content=url, mention_author=mention_author)
            else:
                await message.channel.send(content=url)

            return kwargs

        if not is_on_web:
            try:
                if reply:
                    await message.reply(
                        content=content, file=discord.File(url), mention_author=mention_author
                    )
                else:
                    await message.channel.send(content=content, file=discord.File(url))
            except Exception as e:
                # TODO: send file failed
                print("send file failed", e)
                pass

            return kwargs

        # from now on, `url` is on the web and `content` is nonempty
        # fetch the file from `url`
        basename = PurePosixPath(unquote(urlparse(url).path)).parts[-1]

        try:
            async with aiohttp.ClientSession() as session:
                # note that it is often preferable to create a single session to use multiple times later - see below for this.
                async with session.get(url) as resp:
                    buffer = BytesIO(await resp.read())
                    file=discord.File(fp=buffer, filename=basename)

        except Exception as e:
            # TODO: fetch file failed
            print("fetch file failed", e)
            file = None
            pass

        try:
            if reply:
                await message.reply(content=content, file=file, mention_author=mention_author)
            else:
                await message.channel.send(content=content, file=file)
        except Exception as e:
            # TODO: send file failed
            print("send file failed", e)
            pass

        return kwargs

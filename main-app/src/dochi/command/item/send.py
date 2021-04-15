from typing import Optional
import discord
from .item import CommandItem
from urllib.parse import unquote, urlparse
from pathlib import PurePosixPath
import aiohttp
from io import BytesIO
import cairosvg


class Send(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        content: str,
        file: Optional[discord.File] = None,
        url: Optional[str] = None,
        svg: Optional[str] = None,
        reply: bool = False,
        dm: Optional[discord.Member] = None,
        mention_author: bool = False,
        **kwargs,
    ):
        # text only
        if url is None and svg is None and file is None:
            if reply:
                prev_message = await message.reply(content, mention_author=mention_author)
            elif dm is not None:
                prev_message = await dm.send(content)
            else:
                prev_message = await message.channel.send(content)

            return {**kwargs, "prev_message": prev_message}

        # has a file
        if file is not None:
            if reply:
                prev_message = await message.reply(content=content, file=file, mention_author=mention_author)
            elif dm is not None:
                prev_message = await dm.send(content=content, file=file)
            else:
                prev_message = await message.channel.send(content=content, file=file)

            return {**kwargs, "prev_message": prev_message}

        # svg (with text)
        if url is None:
            buffer = BytesIO()
            cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=buffer)
            buffer.seek(0)
            file_obj=discord.File(fp=buffer, filename="image.png")

            if reply:
                prev_message = await message.reply(content=content, file=file_obj, mention_author=mention_author)
            elif dm is not None:
                prev_message = await dm.send(content=content, file=file_obj)
            else:
                prev_message = await message.channel.send(content=content, file=file_obj)

            return {**kwargs, "prev_message": prev_message}

        is_on_web = url.startswith("http://") or url.startswith("https://")

        content = content.strip()

        if is_on_web and content == "":
            if reply:
                prev_message = await message.reply(content=url, mention_author=mention_author)
            elif dm is not None:
                prev_message = await dm.send(content=url)
            else:
                prev_message = await message.channel.send(content=url)

            return {**kwargs, "prev_message": prev_message}

        if not is_on_web:
            try:
                if reply:
                    prev_message = await message.reply(
                        content=content, file=discord.File(url), mention_author=mention_author
                    )
                elif dm is not None:
                    prev_message = await dm.send(content=content, file=discord.File(url))
                else:
                    prev_message = await message.channel.send(content=content, file=discord.File(url))
            except Exception as e:
                # send file failed
                prev_message = None
                print("send file failed", e)
                pass

            return {**kwargs, "prev_message": prev_message}

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
            # fetch file failed
            print("fetch file failed", e)
            file = None
            pass

        try:
            if reply:
                prev_message = await message.reply(content=content, file=file, mention_author=mention_author)
            elif dm is not None:
                prev_message = await dm.send(content=content, file=file)
            else:
                prev_message = await message.channel.send(content=content, file=file)
        except Exception as e:
            # send file failed
            prev_message = None
            print("send file failed", e)
            pass

        return {**kwargs, "prev_message": prev_message}

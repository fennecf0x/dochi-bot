from typing import Optional
import os
import discord
import aiohttp
import asyncio
from io import BytesIO
import tempfile
from .item import CommandItem
from ...state import state


class Shout(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        content: str,
        **kwargs,
    ):
        content = content.strip()
        if content == "":
            return kwargs

        channel = message.channel
        if channel is None:
            return kwargs

        guild = channel.guild
        if guild is None:
            return kwargs

        voice_state = message.author.voice
        if voice_state is None:
            return kwargs

        voice_channel = message.author.voice.channel
        if voice_channel is None:
            if guild.voice_channels == []:
                return kwargs

            voice_channel == guild.voice_channels[0]

        voice_client = client.voice_clients[0] if client.voice_clients != [] else None

        try:
            if voice_client is not None and voice_client.channel != voice_channel:
                await voice_client.disconnect(force=True)
        except Exception as e:
            print("error during disconnecting")
            print(e)
            return kwargs

        try:
            if voice_client is None or not voice_client.is_connected():
                voice_client = await voice_channel.connect()
        except Exception as e:
            print("error during connecting")
            print(e)
            return kwargs

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://kakaoi-newtone-openapi.kakao.com/v1/synthesize",
                data=f"""<speak><prosody rate="slow"><voice name="WOMAN_READ_CALM">{content}</voice></prosody></speak>""",
                headers={
                    "Content-Type": "application/xml",
                    "Authorization": f"KakaoAK {os.environ['KAKAO_API_KEY']}",
                },
            ) as resp:
                print("voice synt", resp.status)

                fp = tempfile.NamedTemporaryFile(mode="w+b", suffix=".mp3", delete=False)
                fp.write(await resp.read())
                fp.seek(0)

                filename = fp.name

                def cleanup():
                    try:
                        os.remove(filename)
                    except Exception as e:
                        print("ERROR during audio file deletion")
                        print(e)

                async def callback_coro():
                    await asyncio.sleep(2)
                    await voice_client.disconnect(force=True)

                def callback(error: Optional[Exception] = None):
                    if error is not None:
                        print("ERROR during voice callback")
                        print(error)
                        
                    coro = callback_coro()
                    fut = asyncio.run_coroutine_threadsafe(coro, client.loop)
                    try:
                        fut.result()
                    except Exception as e:
                        print("ERROR during ending play audio")
                        print(e)
                    finally:
                        fp.close()
                        cleanup()
                
                print("filename", filename)

                try:
                    voice_client.play(discord.FFmpegPCMAudio(filename), after=callback)
                except Exception as e:
                    print("ERROR during playing audio")
                    print(e)
                    fp.close()
                    cleanup()

        return {**kwargs}

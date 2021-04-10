import discord
from .item import CommandItem
from .send import Send
from ...state import state
from ...games.ff_triple_triad import FFTripleTriad
from .finance import ChangeFinance
from ...database.types import CurrencyType
import tossi
import re
import asyncio
from typing import Tuple, Optional
from contextlib import suppress


class JoinFFTripleTriad(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        **kwargs,
    ):
        """
        join FF triple triad
        """

        if (True, message.channel.id) not in state.games:
            game = FFTripleTriad(client, message.channel.id, message.author.id)
            state.games[game.id] = game
            return {
                **kwargs,
                "content": "트리플 트라이어드 게임이 만들어졌어!\n참가하려면 '돛 트트 할래'라고 말하면 되고, 옵션을 바꾸려면 '돛 트트 (옵션 이름)ㅇ (옵션 이름)ㄴ'으로 알려주면 돼.\n\n가능한 옵션: 동수, 합산, 순서대로, 랜덤순서, 랜덤",
                "notify": False,
            }

        game: FFTripleTriad = state.games[(True, message.channel.id)]
        if game.__class__.__name__ != "FFTripleTriad":
            return {**kwargs, "content": "이 방에선 다른 게임이 이미 진행 중이야.", "notify": True}

        if not game.join(message.author.id):
            return {**kwargs, "content": "이 방에선 다른 게임이 이미 진행 중이야.", "notify": True}

        game.start()
        member = message.guild.get_member(game.player_ids[0])

        options = f"\n\n현재 옵션: {', '.join(f'**{key}**' if game.options[key] else f'~~{key}~~' for key in game.options.keys())}"

        return {
            **kwargs,
            "content": f"게임 시작! <@!{game.player_ids[0]}>{tossi.pick(member.nick or member.name, '이')} 할 차례야. 패를 보고 해당하는 {'알파벳을' if game.options['순서대로'] or game.options['랜덤순서'] else  '숫자랑 알파벳을 같이'} 써줘!{'' if not game.options['랜덤'] else options}",
        }


class NotifyFFTripleTriad(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        **kwargs,
    ):
        """
        send board in ff triple triad
        """

        if (True, message.channel.id) not in state.games:
            if "notify" in kwargs and kwargs["notify"]:
                return kwargs
            return {**kwargs, "is_satisfied": False}

        game: FFTripleTriad = state.games[(True, message.channel.id)]
        if game.__class__.__name__ != "FFTripleTriad":
            if "notify" in kwargs and kwargs["notify"]:
                return kwargs
            return {**kwargs, "is_satisfied": False}

        if "notify" in kwargs and not kwargs["notify"]:
            return kwargs

        if game.hand_messages[1 - game.turn_index] is not None:
            with suppress(Exception):
                await game.hand_messages[1 - game.turn_index].delete()

        if game.get_winner() is not None:
            await game.prev_message.delete()
            for hand_message in game.hand_messages:
                with suppress(Exception):
                    await hand_message.delete()

            winner = game.get_winner()
            state.games.pop(game.id)
            return {
                **kwargs,
                "content": f"""<@!{game.player_ids[winner]}>{
                    tossi.pick(
                        message.guild.get_member(game.player_ids[winner]).nick
                        or message.guild.get_member(game.player_ids[winner]).name,
                        '이',
                    )
                } 이겼어!"""
                if winner in [0, 1]
                else "비겼어!",
                "winner": game.player_ids[winner] if winner in [0, 1] else None,
                "loser": game.player_ids[winner] if winner in [0, 1] else None,
                "svg": game.print_board(),
            }

        if game.hand_messages[game.turn_index] is None:
            game.hand_messages[game.turn_index] = (
                await Send()(
                    client,
                    message,
                    content=f"<@!{game.player_ids[game.turn_index]}>의 덱",
                    svg=game.print_hand(game.turn_index),
                    dm=message.guild.get_member(game.player_ids[game.turn_index]),
                )
            )["prev_message"]

        game.hand_messages[1 - game.turn_index] = (
            await Send()(
                client,
                message,
                content=f"<@!{game.player_ids[1 - game.turn_index]}>의 덱",
                svg=game.print_hand(1 - game.turn_index),
                dm=message.guild.get_member(game.player_ids[1 - game.turn_index]),
            )
        )["prev_message"]

        curr_player = game.turn_index
        member = message.guild.get_member(game.player_ids[curr_player])

        return {
            **kwargs,
            "content": kwargs["content"]
            if kwargs["content"].startswith("게임 시작")
            else f"<@!{game.player_ids[curr_player]}>{tossi.pick(member.nick or member.name, '이')} 할 차례야. 패를 보고 해당하는 {'알파벳을' if game.options['순서대로'] or game.options['랜덤순서'] else  '숫자랑 알파벳을 같이'} 써줘!",
            "svg": game.print_board(),
        }


class PlayFFTripleTriad(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        move: Tuple[Optional[int], str],
        **kwargs,
    ):
        """
        play a move in FF triple triad
        """

        if (True, message.channel.id) not in state.games:
            return {**kwargs, "is_satisfied": False}

        game: FFTripleTriad = state.games[(True, message.channel.id)]
        if game.__class__.__name__ != "FFTripleTriad" or game.is_finished:
            return {**kwargs, "is_satisfied": False}

        if message.author.id not in game.player_ids:
            return {**kwargs, "is_satisfied": False}

        if (game.options["순서대로"] or game.options["랜덤순서"]) != (move[0] is None):
            return {**kwargs, "is_satisfied": False}

        index = game.player_ids.index(message.author.id)

        return {**kwargs, "is_satisfied": game.play(index, move)}


class StoreFFTripleTriadMessage(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        prev_message: discord.Message,
        **kwargs,
    ):
        """
        store sent message in FF TripleTriad
        """

        if (True, message.channel.id) not in state.games:
            return {**kwargs, "is_satisfied": False}

        game: FFTripleTriad = state.games[(True, message.channel.id)]
        if game.__class__.__name__ != "FFTripleTriad" or game.is_finished:
            return {**kwargs, "is_satisfied": False}

        game.prev_message = prev_message

        return kwargs


class DeleteFFTripleTriadMessage(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        **kwargs,
    ):
        """
        delete sent message in FF TripleTriad
        """

        if (True, message.channel.id) not in state.games:
            return {**kwargs, "is_satisfied": False}

        game: FFTripleTriad = state.games[(True, message.channel.id)]
        if game.__class__.__name__ != "FFTripleTriad" or game.is_finished:
            return {**kwargs, "is_satisfied": False}

        if game.prev_message is not None:
            await game.prev_message.delete()

        return kwargs


class ProcessOptionsFFTripleTriad(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        content: str,
        **kwargs,
    ):
        """
        parse game options in FF TripleTriad
        """

        if (True, message.channel.id) not in state.games:
            return {**kwargs, "is_satisfied": False}

        game: FFTripleTriad = state.games[(True, message.channel.id)]
        if game.__class__.__name__ != "FFTripleTriad" or game.has_started:
            return {**kwargs, "is_satisfied": False}

        if message.author.id not in game.player_ids:
            return {**kwargs, "is_satisfied": False}

        pattern = r"(동수|합산|순서대로|랜덤순서|랜덤)(ㅇ|ㄴ)?(,|\.)?"
        matches = [
            (option_name, yn_str != "ㄴ")
            for (option_name, yn_str, _) in re.compile(pattern).findall(content)
        ]

        if re.match(r"^((동수|합산|순서대로|랜덤순서|랜덤)(ㅇ|ㄴ)?(,|\.)?)+", content) is None:
            return {**kwargs, "is_satisfied": False}

        if ("순서대로", True) in matches and ("랜덤순서", True) in matches:
            return {**kwargs, "is_satisfied": False}

        if ("순서대로", True) in matches:
            matches.append(("랜덤순서", False))

        if ("랜덤순서", True) in matches:
            matches.append(("순서대로", False))

        for (option_name, option_value) in matches:
            game.options[option_name] = option_value

        return {
            **kwargs,
            "content": f"현재 옵션: {', '.join(f'**{key}**' if game.options[key] else f'~~{key}~~' for key in game.options.keys())}",
        }


class TerminateFFTripleTriad(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        **kwargs,
    ):
        """
        Terminate FF triple triad
        """

        if (True, message.channel.id) not in state.games:
            return {**kwargs, "is_satisfied": False}

        game: FFTripleTriad = state.games[(True, message.channel.id)]
        if game.__class__.__name__ != "FFTripleTriad":
            return {**kwargs, "is_satisfied": False}

        if message.author.id not in game.player_ids:
            return {**kwargs, "is_satisfied": False}

        game.terminate()
        state.games.pop(game.id)

        return {
            **kwargs,
            "content": f"게임이 터졌어!",
        }

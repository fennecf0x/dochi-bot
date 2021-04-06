import discord
from .item import CommandItem
from .send import Send
from ...state import state
from ...games.ff_triple_triad import FFTripleTriad
from .finance import ChangeFinance
from ...database.types import CurrencyType
import tossi
import asyncio
from typing import Tuple


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
                "content": "트리플 트라이어드 게임이 만들어졌어! 참가하려면 '돛 파판 카드게임 할래'라고 말해줘.",
                "notify": False,
            }

        game: FFTripleTriad = state.games[(True, message.channel.id)]
        if game.__class__.__name__ != "FFTripleTriad":
            return {**kwargs, "content": "이 방에선 다른 게임이 이미 진행 중이야.", "notify": True}

        if not game.join(message.author.id):
            return {**kwargs, "content": "이 방에선 다른 게임이 이미 진행 중이야.", "notify": True}

        game.start()
        member = message.guild.get_member(game.player_ids[0])

        return {
            **kwargs,
            "content": f"게임 시작! <@!{game.player_ids[0]}>{tossi.pick(member.nick or member.name, '이')} 할 차례야. 패를 보고 해당하는 숫자랑 알파벳을 같이 써줘!",
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

        if game.hand_messages[0] is not None:
            await asyncio.gather(*[m.delete() for m in game.hand_messages])

        if game.get_winner() is not None:
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

        game.hand_messages = [
            k["prev_message"]
            for k in await asyncio.gather(
                *[
                    Send()(
                        client,
                        message,
                        content=f"<@!{player_id}>의 덱",
                        svg=game.print_hand(i),
                        dm=message.guild.get_member(player_id),
                    )
                    for i, player_id in enumerate(game.player_ids)
                ]
            )
        ]

        curr_player = game.turn_index
        member = message.guild.get_member(game.player_ids[curr_player])

        return {
            **kwargs,
            "content": f"<@!{game.player_ids[curr_player]}>{tossi.pick(member.nick or member.name, '이')} 할 차례야. 패를 보고 해당하는 숫자랑 알파벳을 같이 써줘!",
            "svg": game.print_board(),
        }


class PlayFFTripleTriad(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        move: Tuple[int, str],
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

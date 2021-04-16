import discord
from .item import CommandItem
from .send import Send
from ...state import state
from ...games.penguin_party import PenguinParty
from .finance import ChangeFinance
from ...database.types import CurrencyType
import tossi
import re
import asyncio
from typing import Tuple, Optional
from contextlib import suppress


class JoinPenguinParty(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        **kwargs,
    ):
        """
        join penguin party
        """

        if (True, message.channel.id) not in state.games:
            game = PenguinParty(client, message.channel.id, message.author.id)
            state.games[game.id] = game
            return {
                **kwargs,
                "content": "펭귄 파티 게임이 만들어졌어!\n참가하려면 '돛 펭귄 할래'라고 말해줘.",
                "notify": False,
            }

        game: PenguinParty = state.games[(True, message.channel.id)]
        if game.__class__.__name__ != "PenguinParty":
            return {**kwargs, "content": "이 방에선 다른 게임이 이미 진행 중이야.", "notify": True}

        if message.author.id in game.player_ids:
            return kwargs

        if not game.join(message.author.id):
            return {**kwargs, "content": "이 방에선 다른 게임이 이미 진행 중이야.", "notify": True}

        await message.channel.send("게임 참가 완료!")

        return {
            **kwargs,
            "is_satisfied": False,
        }


class ExitPenguinParty(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        **kwargs,
    ):
        """
        exit penguin party
        """

        if (True, message.channel.id) not in state.games:
            return {**kwargs, "is_satisfied": False}

        game: PenguinParty = state.games[(True, message.channel.id)]
        if game.__class__.__name__ != "PenguinParty":
            return {**kwargs, "is_satisfied": False}

        if message.author.id not in game.player_ids:
            return {**kwargs, "is_satisfied": False}

        game.player_ids.remove(message.author.id)

        if game.has_started and not game.is_finished:
            return {
                **kwargs,
                "content": f"게임이 이미 진행 중이야.",
            }

        if len(game.player_ids) == 0:
            state.games.pop(game.id)

            return {
                **kwargs,
                "content": f"게임이 터졌어!",
            }

        return {
            **kwargs,
            "content": f"게임 퇴장 완료!",
        }


class StartPenguinParty(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        **kwargs,
    ):
        """
        start penguin party
        """

        if (True, message.channel.id) not in state.games:
            return {**kwargs, "notify": True}

        game: PenguinParty = state.games[(True, message.channel.id)]
        if game.__class__.__name__ != "PenguinParty":
            return {**kwargs, "is_satisfied": False}

        if message.author.id not in game.player_ids:
            return {**kwargs, "notify": True}

        if len(game.player_ids) < 2:
            return {**kwargs, "is_satisfied": False}

        game.start()

        curr_player = game.turn_index
        member = message.guild.get_member(game.player_ids[curr_player])

        return {
            **kwargs,
            "content": f"게임 시작! <@!{game.player_ids[0]}>{tossi.pick(member.nick or member.name, '이')} 할 차례야. 카드의 색깔(빨강(R), 노랑(Y), 초록(G), 파랑(B), 보라(P))과 놓을 위치를 같이 써줘!",
        }


class NotifyPenguinParty(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        **kwargs,
    ):
        """
        send board in penguin party
        """

        if (True, message.channel.id) not in state.games:
            if "notify" in kwargs and kwargs["notify"]:
                return kwargs
            return {**kwargs, "is_satisfied": False}

        game: PenguinParty = state.games[(True, message.channel.id)]
        if game.__class__.__name__ != "PenguinParty":
            if "notify" in kwargs and kwargs["notify"]:
                return kwargs
            return {**kwargs, "is_satisfied": False}

        if "notify" in kwargs and not kwargs["notify"]:
            return kwargs

        if not game.has_started:
            return kwargs

        turn_before = game.turn_index - 1
        if turn_before < 0:
            turn_before += len(game.player_ids)

        if game.hand_messages[turn_before] is not None:
            with suppress(Exception):
                await game.hand_messages[turn_before].delete()

        if game.is_finished:
            await game.prev_message.delete()
            for hand_message in game.hand_messages:
                with suppress(Exception):
                    await hand_message.delete()

            scores = game.get_scores()
            state.games.pop(game.id)
            return {
                **kwargs,
                "content": kwargs["content"]
                + "최종 점수:\n"
                + "\n".join(
                    f"<@!{player_id}>: {score}" for (player_id, score) in scores.items()
                ),
                "svg": game.print_board(),
            }

        player_indices = [
            i
            for i in range(len(game.player_ids))
            if game.hand_messages[i] is None or i == turn_before
        ]

        kwargses = await asyncio.gather(
            *[
                Send()(
                    client,
                    message,
                    content=f"<@!{game.player_ids[i]}>의 덱",
                    svg=game.print_hand(i),
                    dm=message.guild.get_member(game.player_ids[i]),
                )
                for i in player_indices
            ]
        )

        for i, player_index in enumerate(player_indices):
            game.hand_messages[player_index] = kwargses[i]["prev_message"]

        curr_player = game.turn_index
        member = message.guild.get_member(game.player_ids[curr_player])

        return {
            **kwargs,
            "content": kwargs["content"]
            if kwargs["content"].startswith("게임 시작")
            else kwargs["content"]
            + f"<@!{game.player_ids[curr_player]}>{tossi.pick(member.nick or member.name, '이')} 할 차례야. 카드의 색깔(빨강(R), 노랑(Y), 초록(G), 파랑(B), 보라(P))과 놓을 위치를 같이 써줘!",
            "svg": game.print_board(),
        }


class PlayPenguinParty(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        move: Tuple[int, int],
        **kwargs,
    ):
        """
        play a move in penguin party
        """

        if (True, message.channel.id) not in state.games:
            return {**kwargs, "is_satisfied": False}

        game: PenguinParty = state.games[(True, message.channel.id)]
        if game.__class__.__name__ != "PenguinParty" or game.is_finished:
            return {**kwargs, "is_satisfied": False}

        if message.author.id not in game.player_ids:
            return {**kwargs, "is_satisfied": False}

        index = game.player_ids.index(message.author.id)

        result = game.play(index, move)
        surrendered_player_ids = [
            game.player_ids[player_index]
            for player_index in (result[1] if result != False else [])
        ]

        if surrendered_player_ids != []:
            nickname = lambda m: (m.nick or m.name)
            content = (
                "".join(
                    f"<@!{player_id}>{tossi.pick(nickname(message.guild.get_member(player_id)), '랑' if player_id != surrendered_player_ids[-1] else '은')} "
                    for player_id in surrendered_player_ids
                )
                + " 할 수 있는 게 없어!\n\n"
            )

        else:
            content = ""

        return {
            **kwargs,
            "is_satisfied": result if result == False else True,
            "content": content,
        }


class StorePenguinPartyMessage(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        prev_message: discord.Message,
        **kwargs,
    ):
        """
        store sent message in penguin party
        """

        if (True, message.channel.id) not in state.games:
            return {**kwargs, "is_satisfied": False}

        game: PenguinParty = state.games[(True, message.channel.id)]
        if game.__class__.__name__ != "PenguinParty" or game.is_finished:
            return {**kwargs, "is_satisfied": False}

        game.prev_message = prev_message

        return kwargs


class DeletePenguinPartyMessage(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        **kwargs,
    ):
        """
        delete sent message in penguin party
        """

        if (True, message.channel.id) not in state.games:
            return {**kwargs, "is_satisfied": False}

        game: PenguinParty = state.games[(True, message.channel.id)]
        if game.__class__.__name__ != "PenguinParty" or game.is_finished:
            return {**kwargs, "is_satisfied": False}

        if game.prev_message is not None:
            await game.prev_message.delete()

        return kwargs


# class ProcessOptionsPenguinParty(CommandItem):
#     async def __call__(  # type: ignore
#         self,
#         client: discord.Client,
#         message: discord.Message,
#         *,
#         content: str,
#         **kwargs,
#     ):
#         """
#         parse game options in penguin party
#         """

#         if (True, message.channel.id) not in state.games:
#             return {**kwargs, "is_satisfied": False}

#         game: FFTripleTriad = state.games[(True, message.channel.id)]
#         if game.__class__.__name__ != "FFTripleTriad" or game.has_started:
#             return {**kwargs, "is_satisfied": False}

#         if message.author.id not in game.player_ids:
#             return {**kwargs, "is_satisfied": False}

#         pattern = r"(동수|합산|순서대로|랜덤순서|랜덤)(ㅇ|ㄴ)?(,|\.)?"
#         matches = [
#             (option_name, yn_str != "ㄴ")
#             for (option_name, yn_str, _) in re.compile(pattern).findall(content)
#         ]

#         if re.match(r"^((동수|합산|순서대로|랜덤순서|랜덤)(ㅇ|ㄴ)?(,|\.)?)+", content) is None:
#             return {**kwargs, "is_satisfied": False}

#         if ("순서대로", True) in matches and ("랜덤순서", True) in matches:
#             return {**kwargs, "is_satisfied": False}

#         if ("순서대로", True) in matches:
#             matches.append(("랜덤순서", False))

#         if ("랜덤순서", True) in matches:
#             matches.append(("순서대로", False))

#         for (option_name, option_value) in matches:
#             game.options[option_name] = option_value

#         return {
#             **kwargs,
#             "content": f"현재 옵션: {', '.join(f'**{key}**' if game.options[key] else f'~~{key}~~' for key in game.options.keys())}",
#         }


class TerminatePenguinParty(CommandItem):
    async def __call__(  # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        **kwargs,
    ):
        """
        Terminate penguin party
        """

        if (True, message.channel.id) not in state.games:
            return {**kwargs, "is_satisfied": False}

        game: PenguinParty = state.games[(True, message.channel.id)]
        if game.__class__.__name__ != "PenguinParty":
            return {**kwargs, "is_satisfied": False}

        if message.author.id not in game.player_ids:
            return {**kwargs, "is_satisfied": False}

        game.terminate()
        state.games.pop(game.id)

        return {
            **kwargs,
            "content": f"게임이 터졌어!",
        }

import discord
from .item import CommandItem
from ...state import state
from ...games.ff_lottery import FFLottery
from .finance import ChangeFinance
from ...database.types import CurrencyType

class StartFFLottery(CommandItem):
    async def __call__( # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        **kwargs,
    ):
        """
        start FF lottery
        """

        if (False, "FFLottery", message.author.id) in state.games:
            return {**kwargs, "is_satisfied": False}

        game = FFLottery(client, message.author.id)

        state.games[game.id] = game


class NotifyFFLottery(CommandItem):
    async def __call__( # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        **kwargs,
    ):
        """
        notify next move in FF lottery
        """

        if (False, "FFLottery", message.author.id) not in state.games:
            return {**kwargs, "is_satisfied": False}

        game: FFLottery = state.games[(False, "FFLottery", message.author.id)]

        if game.stage < 3:
            return {**kwargs, "content": "A부터 I까지 중에서 하나를 골라줘!\n\n" + game.print_board()}

        if game.stage == 3:
            return {**kwargs, "content": "A부터 H까지 중에서 하나를 골라줘!\n\n" + game.print_board()}

        if game.stage == 4:
            points = game.get_points()
            content = f"{points}원을 얻었어!\n\n" + game.print_board()
            
            await ChangeFinance(currency_type=CurrencyType.MONEY, amount=points, incremental=True)(client, message)

            state.games.pop((False, "FFLottery", message.author.id), None)
            return {**kwargs, "points": points, "content": content}


class PlayFFLottery(CommandItem):
    async def __call__( # type: ignore
        self,
        client: discord.Client,
        message: discord.Message,
        *,
        move: str,
        **kwargs,
    ):
        """
        play a move in FF lottery
        """

        if (False, "FFLottery", message.author.id) not in state.games:
            return {**kwargs, "is_satisfied": False}

        game: FFLottery = state.games[(False, "FFLottery", message.author.id)]

        return {**kwargs, "is_satisfied": game.play(None, move)}

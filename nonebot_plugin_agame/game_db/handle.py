from pathlib import Path

from nonebot.adapters import Event, Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from pydantic import BaseModel
from tortoise import Tortoise

from .model import PlayerInfo

DATA_PATH = Path("data/agame/data.sqlite")
DATA_PATH.parent.mkdir(parents=True, exist_ok=True)


async def init():
    await Tortoise.init(db_url=f"sqlite://{DATA_PATH!s}", modules={"models": ["models"]})
    await Tortoise.generate_schemas()  # safe：仅在表不存在时创建表


class KeywordHandler(BaseModel):
    # async def __init__(self):
    #     self.allow_group: bool = utils.allow_group

    @staticmethod
    async def create_country(
        matcher: Matcher,
        event: Event,
        arg: Message = CommandArg(),
    ) -> None:
        """创建国家"""
        country_name = arg.extract_plain_text()
        if len(country_name) == 0:
            country_name = "无名国"
        msg = await PlayerInfo.new(user_id=event.get_user_id(), name=country_name)
        if msg:
            await matcher.send(f"创建国家成功：{country_name}")
        else:
            await matcher.send("创建国家失败")

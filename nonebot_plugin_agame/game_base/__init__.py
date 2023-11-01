from nonebot import on_command

from ..game_db.handle import KeywordHandler

new = on_command(
    "create_country",
    aliases={"建立国家"},
    block=True,
    priority=10,
    handlers=[KeywordHandler.create_country],
)

import contextlib

from nonebot import require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from tortoise import run_async

from .game_db import init

require("nonebot_plugin_saa")


with contextlib.suppress(Exception):
    __version__ = "0.0.1"
    __plugin_meta__ = PluginMetadata(
        name="万界之门",
        description="群聊小游戏，模拟社会发展",
        usage="发送：建立国家",
        type="application",
        homepage="https://github.com/Agnes4m/agens_game",
        config=None,
        supported_adapters=inherit_supported_adapters("nonebot_plugin_saa"),
        extra={
            "version": __version__,
            "link": "https://github.com/Agnes4m/agens_game",
            "author": "Agnes4m <Z735803792@163.com>",
            "priority": [1],
        },
    )
run_async(init())  # 数据库校验

from .game_base import *  # noqa: F403

from nonebot import require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_session")
require("nonebot_plugin_saa")

from . import __main__ as __main__  # noqa: E402

__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="万界之门",
    description="个人小游戏",
    usage="",
    type="",
    homepage="https://github.com/Agnes4m/agens_game",
    config=None,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_saa"),
    extra={
        "version": __version__,
        "author": "Agnes4m <Z735803792@163.com>",
    },
)

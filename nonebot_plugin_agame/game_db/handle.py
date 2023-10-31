from pathlib import Path

from tortoise import Tortoise

DATA_PATH = Path("data/agame/data.sqlite")
DATA_PATH.parent.mkdir(parents=True, exist_ok=True)


async def init():
    await Tortoise.init(db_url=f"sqlite://{DATA_PATH!s}", modules={"models": ["models"]})
    await Tortoise.generate_schemas()  # safe：仅在表不存在时创建表

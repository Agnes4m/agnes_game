# import random

from tortoise import fields
from tortoise.models import Model


class PlayerInfo(Model):
    """基础信息"""

    user_id = fields.TextField(pk=True, description="用户ID", index=True)
    name = fields.TextField(description="国家昵称")
    power = fields.FloatField(description="综合国力")
    """战斗力计算公式 """
    level = fields.IntField(description="等级")
    people = fields.FloatField(description="人口")
    title = fields.TextField(description="政体")

    class Meta:
        table = "PlayerInfo"

    @classmethod
    async def new(
        cls,
        user_id: str,
        name: str = "无名国",
        level: int = 1,
        people: float = 100,
        title: str = "原始社会",
    ):
        """新增一行,返回结果是否创建成功"""
        _, confirm = await cls.get_or_create(
            user_id=user_id,
            name=name,
            level=level,
            people=people,
            title=title,
        )
        return confirm


class VarInfo(Model):
    """次数信息
    主要有关定时刷新的变量"""

    user_id = fields.TextField(pk=True, description="用户ID", index=True)

    class Meta:
        table = "VarInfo"


# class ArmyInfo(Model):
#     """军队信息"""

#     user_id = fields.TextField(pk=True, description="用户ID", index=True)
#     name = fields.TextField(description="军体名称")
#     level = fields.IntField(description="等级")
#     tactics = fields.TextField(description="军事策略")
#     qua_max = fields.IntField(description="适役人口")
#     score = fields.FloatField(description="军队评分")

#     class Meta:
#         table = "ArmyInfo"


# class EconomyInfo(Model):
#     """经济信息"""

#     user_id = fields.TextField(pk=True, description="用户ID", index=True)
#     name = fields.TextField(description="经济体名称")
#     level = fields.IntField(description="等级")
#     score = fields.FloatField(description="经济评分")

#     class Meta:
#         table = "EconomyInfo"

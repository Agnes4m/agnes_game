import random

from tortoise import fields
from tortoise.models import Model


class PlayerInfo(Model):
    """基础信息"""

    user_id = fields.TextField(pk=True, description="用户ID", index=True)
    name = fields.TextField(description="昵称")
    power = fields.IntField(description="综合国力")
    """战斗力计算公式 """
    level = fields.IntField(description="人口")
    title = fields.TextField(description="称号")

    class Meta:
        table = "PlayerInfo"

    @classmethod
    async def new(cls, user_id: int):
        """新增一行,返回结果是否创建成功"""
        _, confirm = await cls.get_or_create(user_id=user_id)
        # 随机生成数据
        return confirm


class VarInfo(Model):
    """次数信息"""

    user_id = fields.TextField(pk=True, description="用户ID", index=True)

    class Meta:
        table = "VarInfo"


class ArmyInfo(Model):
    """军队信息"""

    user_id = fields.TextField(pk=True, description="用户ID", index=True)
    name = fields.TextField(description="军体名称")
    qua_max = fields.IntField(description="适役人口")

    class Meta:
        table = "ArmyInfo"


class EconomyInfo(Model):
    """经济信息"""

    user_id = fields.TextField(pk=True, description="用户ID", index=True)
    name = fields.TextField(description="经济体名称")

    class Meta:
        table = "EconomyInfo"


class PoliticsInfo(Model):
    """政治信息"""

    user_id = fields.TextField(pk=True, description="用户ID", index=True)
    name = fields.TextField(description="政体名称")
    pol_by_amry = fields.FloatField(description="军政占比")
    eco_by_amry = fields.FloatField(description="商政占比")

    class Meta:
        table = "PoliticsInfo"

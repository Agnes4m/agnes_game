# models.py
from tortoise import fields
from tortoise.models import Model


class PlayerInfo(Model):
    id_ = fields.IntField(
        pk=True, description="用户ID", index=True, source_field="user_id"
    )
    name = fields.TextField(max_length=100, description="昵称", source_field="name")

    class Meta:
        table = "users"

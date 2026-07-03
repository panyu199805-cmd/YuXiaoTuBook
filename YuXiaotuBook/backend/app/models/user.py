from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password_hash = fields.CharField(max_length=255)
    nickname = fields.CharField(max_length=50)
    avatar = fields.CharField(max_length=255, null=True)
    province = fields.CharField(max_length=50, null=True)
    city = fields.CharField(max_length=50, null=True)
    role = fields.CharField(max_length=20, default="user")
    status = fields.IntField(default=1)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "user"

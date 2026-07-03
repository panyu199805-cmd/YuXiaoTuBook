from tortoise import fields
from tortoise.models import Model


class UserPreference(Model):
    id = fields.IntField(pk=True)
    user_id = fields.IntField(unique=True)
    category_ids = fields.TextField(default="[]")
    scene_tags = fields.TextField(default="[]")
    bio = fields.CharField(max_length=100, null=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user_preference"

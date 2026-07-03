from tortoise import fields
from tortoise.models import Model


class Category(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)
    slug = fields.CharField(max_length=50, unique=True)
    sort_order = fields.IntField(default=0)

    class Meta:
        table = "category"

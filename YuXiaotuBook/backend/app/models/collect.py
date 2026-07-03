from tortoise import fields
from tortoise.models import Model


class UserBookCollect(Model):
    id = fields.IntField(pk=True)
    user_id = fields.IntField()
    book_id = fields.IntField()
    collect_type = fields.IntField(default=1)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "user_book_collect"
        unique_together = (("user_id", "book_id", "collect_type"),)

from tortoise import fields
from tortoise.models import Model


class DailyBook(Model):
    id = fields.IntField(pk=True)
    book_id = fields.IntField()
    daily_sentence = fields.TextField()
    daily_intro = fields.TextField(null=True)
    publish_date = fields.DateField(unique=True)
    is_top = fields.BooleanField(default=False)
    status = fields.IntField(default=1)
    like_count = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "daily_book"

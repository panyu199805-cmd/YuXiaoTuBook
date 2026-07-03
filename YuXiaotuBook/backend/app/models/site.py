from tortoise import fields
from tortoise.models import Model


class SiteConfig(Model):
    id = fields.IntField(pk=True)
    bg_type = fields.CharField(max_length=20, default="image")
    bg_url = fields.CharField(max_length=500, null=True)
    bg_videos = fields.JSONField(null=True)
    bg_music = fields.CharField(max_length=500, null=True)
    white_noise = fields.CharField(max_length=500, null=True)
    music_enabled = fields.BooleanField(default=True)
    bg_enabled = fields.BooleanField(default=True)
    featured_book_id = fields.IntField(null=True)
    promo_title = fields.CharField(max_length=200, null=True)
    daily_sentence = fields.CharField(max_length=500, null=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "site_config"

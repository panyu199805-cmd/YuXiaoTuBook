from tortoise import fields
from tortoise.models import Model


class MemberPackage(Model):
    id = fields.IntField(pk=True)
    package_name = fields.CharField(max_length=50)
    price = fields.FloatField(default=0)
    valid_day = fields.IntField(default=30)
    rights = fields.TextField(default="[]")
    status = fields.IntField(default=1)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "member_package"


class UserMember(Model):
    id = fields.IntField(pk=True)
    user_id = fields.IntField(unique=True)
    package_id = fields.IntField()
    expire_time = fields.DatetimeField()
    is_vip = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user_member"


class MemberOrder(Model):
    id = fields.IntField(pk=True)
    order_no = fields.CharField(max_length=64, unique=True)
    user_id = fields.IntField()
    package_id = fields.IntField()
    amount = fields.FloatField(default=0)
    status = fields.CharField(max_length=20, default="pending_payment")
    pay_channel = fields.CharField(max_length=20, default="mock")
    pay_time = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "member_order"

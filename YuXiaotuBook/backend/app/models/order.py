from tortoise import fields
from tortoise.models import Model


class Order(Model):
    id = fields.IntField(pk=True)
    order_no = fields.CharField(max_length=32, unique=True)
    user_id = fields.IntField()
    total_amount = fields.DecimalField(max_digits=10, decimal_places=2)
    status = fields.CharField(max_length=20, default="pending_payment")
    receiver_name = fields.CharField(max_length=50)
    receiver_phone = fields.CharField(max_length=20)
    receiver_address = fields.CharField(max_length=500)
    pay_time = fields.DatetimeField(null=True)
    ship_company = fields.CharField(max_length=50, null=True)
    ship_tracking_no = fields.CharField(max_length=64, null=True)
    shipped_at = fields.DatetimeField(null=True)
    completed_at = fields.DatetimeField(null=True)
    cancel_reason = fields.CharField(max_length=500, null=True)
    cancelled_at = fields.DatetimeField(null=True)
    cancel_by = fields.CharField(max_length=20, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "orders"


class OrderItem(Model):
    id = fields.IntField(pk=True)
    order_id = fields.IntField()
    book_id = fields.IntField()
    book_title = fields.CharField(max_length=200)
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    quantity = fields.IntField(default=1)

    class Meta:
        table = "order_item"

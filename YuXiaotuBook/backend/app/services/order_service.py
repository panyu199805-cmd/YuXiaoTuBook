from __future__ import annotations

from typing import Optional

from tortoise.transactions import in_transaction

from app.models import Book, Order, OrderItem


class OrderService:
    """Admin 订单履约（发货/取消）。C 端下单与支付已迁移至 Java trade-service。"""

    @staticmethod
    async def cancel(
        order_id: int,
        user_id: Optional[int],
        is_admin: bool = False,
        cancel_reason: Optional[str] = None,
    ) -> Order:
        from datetime import datetime

        async with in_transaction() as conn:
            q = Order.filter(id=order_id)
            if not is_admin:
                q = q.filter(user_id=user_id)
            order = await q.using_db(conn).first()
            if not order:
                raise ValueError("订单不存在")
            if order.status in ("cancelled", "completed"):
                raise ValueError("订单状态不可取消")

            if order.status == "paid":
                item = await OrderItem.filter(order_id=order.id).using_db(conn).first()
                if item:
                    book = await Book.filter(id=item.book_id).using_db(conn).select_for_update().first()
                    if book:
                        book.stock += item.quantity
                        await book.save(using_db=conn)

            order.status = "cancelled"
            order.cancel_reason = (cancel_reason or "").strip() or None
            order.cancelled_at = datetime.utcnow()
            order.cancel_by = "admin" if is_admin else "user"
            await order.save(using_db=conn)
            return order

    @staticmethod
    async def ship_order(order_id: int, ship_company: str, ship_tracking_no: str) -> Order:
        from datetime import datetime

        order = await Order.get_or_none(id=order_id)
        if not order:
            raise ValueError("订单不存在")
        if order.status != "paid":
            raise ValueError("仅待发货订单可发货")
        order.status = "shipped"
        order.ship_company = ship_company.strip()
        order.ship_tracking_no = ship_tracking_no.strip()
        order.shipped_at = datetime.utcnow()
        await order.save()
        return order

    @staticmethod
    async def update_order(
        order_id: int,
        receiver_name: str,
        receiver_phone: str,
        receiver_address: str,
        ship_company: Optional[str] = None,
        ship_tracking_no: Optional[str] = None,
    ) -> Order:
        order = await Order.get_or_none(id=order_id)
        if not order:
            raise ValueError("订单不存在")
        if order.status == "cancelled":
            raise ValueError("已取消订单不可编辑")

        order.receiver_name = receiver_name.strip()
        order.receiver_phone = receiver_phone.strip()
        order.receiver_address = receiver_address.strip()

        if order.status in ("paid", "shipped", "completed"):
            order.ship_company = ship_company.strip() if ship_company else None
            order.ship_tracking_no = ship_tracking_no.strip() if ship_tracking_no else None

        await order.save()
        return order

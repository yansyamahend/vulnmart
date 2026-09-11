from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.user import User

router = APIRouter(
    prefix="/api/orders",
    tags=["Orders"],
)


@router.get("/my")
def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .all()
    )

    return [
        {
            "id": order.id,
            "user_id": order.user_id,
            "total_amount": order.total_amount,
            "currency": order.currency,
            "status": order.status,
            "created_at": order.created_at,
            "challenge_flag": order.challenge_flag,
        }
        for order in orders
    ]


@router.get("/{order_id}")
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed to access this order",
        )

    items = (
        db.query(OrderItem, Product)
        .join(
            Product,
            OrderItem.product_id == Product.id,
        )
        .filter(OrderItem.order_id == order.id)
        .all()
    )

    return {
        "id": order.id,
        "user_id": order.user_id,
        "total_amount": order.total_amount,
        "currency": order.currency,
        "status": order.status,
        "created_at": order.created_at,
        "challenge_flag": order.challenge_flag,
        "items": [
            {
                "product_id": product.id,
                "product_name": product.name,
                "quantity": item.quantity,
                "price": item.price,
                "currency": product.currency,
            }
            for item, product in items
        ],
    }
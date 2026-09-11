from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.user import User

router = APIRouter(
    prefix="/api/cart",
    tags=["Cart"],
)


@router.get("/")
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = (
        db.query(CartItem, Product)
        .join(
            Product,
            CartItem.product_id == Product.id,
        )
        .filter(
            CartItem.user_id == current_user.id
        )
        .all()
    )

    return {
        "items": [
            {
                "id": item.id,
                "product_id": product.id,
                "product_name": product.name,
                "quantity": item.quantity,
                "price": product.price,
                "currency": product.currency,
            }
            for item, product in items
        ]
    }


@router.post("/")
def add_to_cart(
    product_id: int,
    quantity: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    # Hanya produk yang menjadi target challenge
    # yang tidak boleh menggunakan quantity 0 atau negatif.
    #
    # Produk lain tetap mengizinkan negative quantity
    # untuk kebutuhan challenge.
    if product.id in (4, 5) and quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Challenge target product quantity must be greater than 0",
        )

    item = CartItem(
        user_id=current_user.id,
        product_id=product.id,
        quantity=quantity,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        "message": "Product added to cart",
        "cart_item_id": item.id,
        "product_id": product.id,
        "product_name": product.name,
        "quantity": item.quantity,
        "price": product.price,
        "currency": product.currency,
    }
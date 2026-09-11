from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.cart_item import CartItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.user import User
from app.models.wallet import Wallet

router = APIRouter(
    prefix="/api/checkout",
    tags=["Checkout"],
)


@router.post("/")
def checkout(
    currency: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    currency = currency.upper()

    if currency not in ("IDR", "USD"):
        raise HTTPException(
            status_code=400,
            detail="Unsupported currency",
        )

    # Ambil hanya item cart dengan currency
    # yang sedang di-checkout.
    cart_items = (
        db.query(CartItem, Product)
        .join(
            Product,
            CartItem.product_id == Product.id,
        )
        .filter(
            CartItem.user_id == current_user.id,
            Product.currency == currency,
        )
        .all()
    )

    if not cart_items:
        raise HTTPException(
            status_code=400,
            detail=f"No {currency} items in cart",
        )

    # ========================================================
    # CHALLENGE TARGET VALIDATION
    #
    # Product target yang mengandung flag tidak boleh
    # menggunakan quantity 0 atau negatif.
    #
    # Product lain tetap vulnerable terhadap negative quantity.
    # ========================================================

    invalid_items = [
        (item, product)
        for item, product in cart_items
        if product.id in (4, 5)
        and item.quantity <= 0
    ]

    if invalid_items:
        raise HTTPException(
            status_code=400,
            detail="Challenge target product quantity must be greater than 0",
        )

    # Hitung total berdasarkan harga produk dari database.
    total = sum(
        product.price * item.quantity
        for item, product in cart_items
    )

    # Minimum pembelian USD harus $2,000.
    if currency == "USD" and total < 2000:
        raise HTTPException(
            status_code=400,
            detail="USD checkout requires a minimum total of $2,000",
        )

    # Ambil wallet sesuai currency.
    wallet = (
        db.query(Wallet)
        .filter(
            Wallet.user_id == current_user.id,
            Wallet.currency == currency,
        )
        .first()
    )

    if wallet is None:
        raise HTTPException(
            status_code=400,
            detail=f"{currency} wallet not found",
        )

    if wallet.balance < total:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient {currency} balance",
        )

    # ========================================================
    # H4 OBJECTIVE
    #
    # Flag diberikan berdasarkan produk target yang berhasil
    # dibeli, bukan berdasarkan bagaimana user memanipulasi
    # cart/quantity.
    # ========================================================

    contains_global_x = any(
        product.id == 5
        and product.currency == "USD"
        for _, product in cart_items
    )

    contains_ultrabook = any(
        product.id == 4
        and product.currency == "IDR"
        for _, product in cart_items
    )

    challenge_flag = None

    if contains_global_x:
        challenge_flag = (
            "flag{4nda_t3rdeteks1_D3s1L_10_72813}"
        )

    elif contains_ultrabook:
        challenge_flag = (
            "flag{!ni_$truk_ny4_tu4n_37183917}"
        )

    # ========================================================
    # CREATE ORDER
    # ========================================================

    order = Order(
        user_id=current_user.id,
        total_amount=total,
        currency=currency,
        status="completed",
        challenge_flag=challenge_flag,
        description=", ".join(
            f"{product.name} x{item.quantity}"
            for item, product in cart_items
        ),
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    # ========================================================
    # CREATE ORDER ITEMS
    # ========================================================

    for item, product in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            price=product.price,
        )

        db.add(order_item)

    # ========================================================
    # DEDUCT BALANCE
    # ========================================================

    wallet.balance -= total

    # ========================================================
    # CLEAR CHECKED-OUT ITEMS
    # ========================================================

    for item, _ in cart_items:
        db.delete(item)

    db.commit()

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "message": "Checkout successful",
        "order_id": order.id,
        "total_amount": total,
        "currency": currency,
        "remaining_balance": wallet.balance,
        "challenge_completed": challenge_flag is not None,
        "challenge_flag": challenge_flag,
    }
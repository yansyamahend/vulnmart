from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product

router = APIRouter(
    prefix="/api/products",
    tags=["Products"],
)


@router.get("/")
def get_products(
    db: Session = Depends(get_db),
):
    return db.query(Product).all()


@router.get("/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )
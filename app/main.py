from fastapi import FastAPI

from app.database import Base, engine

from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.wallet import Wallet
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.cart_item import CartItem

from app.routes.products import router as products_router
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.orders import router as orders_router
from app.routes.cart import router as cart_router
from app.routes.checkout import router as checkout_router
from app.routes.wallet import router as wallet_router
from app.routes.exchange import router as exchange_router
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from app.routes.pages import router as pages_router
from app.routes.admin import router as admin_router
from app.routes.password_reset import router as password_reset_router
from app.routes.crew import router as crew_router
from app.routes.transactions import router as transactions_router
from app.models.h5_challenge import H5Challenge
from app.routes.accounts import router as accounts_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="VulnMart API",
    description="Educational e-commerce security lab",
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


app.include_router(products_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(orders_router)
app.include_router(cart_router)
app.include_router(checkout_router)
app.include_router(wallet_router)
app.include_router(exchange_router)
app.include_router(pages_router)
app.include_router(admin_router)
app.include_router(password_reset_router)
app.include_router(crew_router)
app.include_router(transactions_router)
app.include_router(accounts_router)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
    }
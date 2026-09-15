from app.database import Base, SessionLocal, engine
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.wallet import Wallet
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.cart_item import CartItem
from app.models.password_reset import PasswordReset

Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # =========================
    # USERS
    # =========================

    admin = User(
        username="admin",
        email="admin@vulnmart.local",
        password="admin_dummy",
        full_name="VulnMart Administrator",
        role="admin",
        bio="Official VulnMart administrator.",
        account_number="1000000001",
    )

    victim = User(
        username="victim",
        email="victim@vulnmart.local",
        password="VictimPass123!",
        full_name="Demo Victim",
        role="member",
        bio="Regular VulnMart member.",
        account_number="8058997464",
    )

    student = User(
        username="student",
        email="student@vulnmart.local",
    password="StudentPass123!",
        full_name="Demo Student",
        role="member",
        bio="Security lab student account.",
        account_number="5935728866",
    )

    db.add_all([
        admin,
        victim,
        student,
    ])

    db.commit()

    # =========================
    # CATEGORIES
    # =========================

    electronics = Category(
        name="Electronics"
    )

    gaming = Category(
        name="Gaming"
    )

    fashion = Category(
        name="Fashion"
    )

    db.add_all([
        electronics,
        gaming,
        fashion,
    ])

    db.commit()

    # =========================
    # PRODUCTS
    # =========================

    mouse = Product(
        seller_id=admin.id,
        category_id=electronics.id,
        name="VulnMouse X1",
        description="Wireless gaming mouse.",
        price=100000,
        currency="IDR",
        stock=100,
        image="/static/images/mouse.jpg",
    )

    keyboard = Product(
        seller_id=admin.id,
        category_id=electronics.id,
        name="VulnKeyboard K1",
        description="Mechanical keyboard.",
        price=250000,
        currency="IDR",
        stock=100,
        image="/static/images/keyboard.jpg",
    )

    headset = Product(
        seller_id=admin.id,
        category_id=gaming.id,
        name="VulnHeadset H1",
        description="Gaming headset.",
        price=500000,
        currency="IDR",
        stock=100,
        image="/static/images/headset.jpg",
    )

    premium_laptop = Product(
        seller_id=admin.id,
        category_id=electronics.id,
        name="VulnMart UltraBook X",
        description="Ultra premium laptop for the H4 security lab.",
        price=100000000,
        currency="IDR",
        stock=10,
        image="/static/images/laptop.jpg",
    )

    global_product = Product(
        seller_id=admin.id,
        category_id=electronics.id,
        name="VulnMart Global X",
        description="Premium international product. Payment in USD only.",
        price=2000,
        currency="USD",
        stock=5,
        image="/static/images/global-x.jpg",
    )

    db.add_all([
        mouse,
        keyboard,
        headset,
        premium_laptop,
        global_product,
    ])

    db.commit()

    # =========================
    # WALLETS
    # =========================

    wallets = [
        Wallet(
            user_id=admin.id,
            balance=100000000,
            currency="IDR",
        ),
        Wallet(
            user_id=admin.id,
            balance=0,
            currency="USD",
        ),
        Wallet(
            user_id=victim.id,
            balance=5000000,
            currency="IDR",
        ),
        Wallet(
            user_id=victim.id,
            balance=0,
            currency="USD",
        ),
        Wallet(
            user_id=student.id,
            balance=100000,
            currency="IDR",
        ),
        Wallet(
            user_id=student.id,
            balance=0,
            currency="USD",
        ),
    ]

    db.add_all(wallets)
    db.commit()

    # =========================
    # VICTIM TRANSACTION
    # =========================

    victim_order = Order(
        user_id=victim.id,
        total_amount=350000,
        currency="IDR",
        status="completed",
        reference_code="VM-SECRET-8472",
        description="flag{dummy4}",
    )

    db.add(victim_order)
    db.commit()
    db.refresh(victim_order)

    victim_order_item = OrderItem(
        order_id=victim_order.id,
        product_id=keyboard.id,
        quantity=1,
        price=keyboard.price,
    )

    db.add(victim_order_item)
    db.commit()

    print("VulnMart seed completed successfully.")
    print(f"Admin ID   : {admin.id}")
    print(f"Victim ID  : {victim.id}")
    print(f"Student ID : {student.id}")
    print(f"Victim Order ID: {victim_order.id}")
    print("Victim Account Number : 8058997464")
    print("Student Account Number: 5935728866")

finally:
    db.close()
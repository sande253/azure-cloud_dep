import os
import sqlite3
from datetime import UTC, datetime
from uuid import uuid4

from flask import Flask, abort, jsonify, render_template, request

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")
TAX_RATE = 0.08
SHIPPING_THRESHOLD = 100.0
SHIPPING_FEE = 6.99

PRODUCT_SEED = [
    {"id": 1, "name": "Echo Smart Speaker", "price": 49.99, "original_price": 69.99, "rating": 4.4, "reviews": 2384, "category": "Electronics", "badge": "Best Seller", "brand": "AtoZ Basics", "image": "https://images.unsplash.com/photo-1518444065439-e933c06ce9cd?auto=format&fit=crop&w=900&q=80", "description": "Compact smart speaker with voice assistant support."},
    {"id": 2, "name": "Noise Cancelling Headphones", "price": 119.00, "original_price": 159.00, "rating": 4.7, "reviews": 4582, "category": "Electronics", "badge": "Prime Pick", "brand": "WaveX", "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80", "description": "Wireless over-ear headphones with active noise cancellation."},
    {"id": 3, "name": "Stainless Steel Bottle", "price": 19.50, "original_price": 24.99, "rating": 4.3, "reviews": 782, "category": "Home & Kitchen", "badge": "Deal", "brand": "HydroPeak", "image": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=80", "description": "Insulated bottle keeps beverages hot or cold for hours."},
    {"id": 4, "name": "Mechanical Keyboard", "price": 79.99, "original_price": 99.99, "rating": 4.6, "reviews": 1224, "category": "Computers", "badge": "Limited Time", "brand": "TypeCraft", "image": "https://images.unsplash.com/photo-1511467687858-23d96c32e4ae?auto=format&fit=crop&w=900&q=80", "description": "Tactile keyboard with customizable backlight."},
    {"id": 5, "name": "Running Shoes", "price": 64.99, "original_price": 84.99, "rating": 4.2, "reviews": 3120, "category": "Fashion", "badge": "Top Rated", "brand": "SprintGo", "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80", "description": "Lightweight running shoes built for comfort and durability."},
    {"id": 6, "name": "Air Fryer", "price": 89.99, "original_price": 129.99, "rating": 4.5, "reviews": 1970, "category": "Home & Kitchen", "badge": "Deal", "brand": "CrispChef", "image": "https://images.unsplash.com/photo-1585515657023-0d8fb89f9584?auto=format&fit=crop&w=900&q=80", "description": "Digital air fryer for quick and healthy family meals."},
    {"id": 7, "name": "Gaming Mouse", "price": 34.99, "original_price": 49.99, "rating": 4.6, "reviews": 2468, "category": "Computers", "badge": "Prime Pick", "brand": "Apex", "image": "https://images.unsplash.com/photo-1527814050087-3793815479db?auto=format&fit=crop&w=900&q=80", "description": "Ergonomic RGB gaming mouse with fast tracking."},
    {"id": 8, "name": "4K Action Camera", "price": 149.00, "original_price": 189.00, "rating": 4.1, "reviews": 658, "category": "Electronics", "badge": "New", "brand": "TrailSnap", "image": "https://images.unsplash.com/photo-1516724562728-afc824a36e84?auto=format&fit=crop&w=900&q=80", "description": "Waterproof action camera with image stabilization."},
    {"id": 9, "name": "Office Chair", "price": 139.99, "original_price": 199.99, "rating": 4.4, "reviews": 1022, "category": "Home & Kitchen", "badge": "Best Seller", "brand": "ErgoNest", "image": "https://images.unsplash.com/photo-1505798577917-a65157d3320a?auto=format&fit=crop&w=900&q=80", "description": "Adjustable mesh chair with lumbar support."},
    {"id": 10, "name": "Smart Watch", "price": 179.99, "original_price": 229.99, "rating": 4.5, "reviews": 3210, "category": "Electronics", "badge": "Deal", "brand": "PulseOne", "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80", "description": "Fitness tracking watch with heart-rate monitor."},
    {"id": 11, "name": "Yoga Mat", "price": 22.99, "original_price": 29.99, "rating": 4.3, "reviews": 943, "category": "Sports", "badge": "Prime Pick", "brand": "FlexCore", "image": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=900&q=80", "description": "Non-slip yoga mat with carry strap."},
    {"id": 12, "name": "Portable SSD 1TB", "price": 98.00, "original_price": 139.00, "rating": 4.8, "reviews": 1875, "category": "Computers", "badge": "Best Seller", "brand": "DataVault", "image": "https://images.unsplash.com/photo-1593640495253-23196b27a87f?auto=format&fit=crop&w=900&q=80", "description": "High-speed USB-C external SSD drive."},
    {"id": 13, "name": "Coffee Grinder", "price": 44.95, "original_price": 64.95, "rating": 4.2, "reviews": 511, "category": "Home & Kitchen", "badge": "Deal", "brand": "BeanBrew", "image": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=80", "description": "Electric burr grinder for even coffee grounds."},
    {"id": 14, "name": "Men's Casual Jacket", "price": 74.99, "original_price": 109.99, "rating": 4.1, "reviews": 602, "category": "Fashion", "badge": "Limited Time", "brand": "UrbanTrail", "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=900&q=80", "description": "Lightweight jacket for everyday wear."},
    {"id": 15, "name": "Robot Vacuum", "price": 219.99, "original_price": 299.99, "rating": 4.4, "reviews": 1550, "category": "Home & Kitchen", "badge": "Top Rated", "brand": "CleanBot", "image": "https://images.unsplash.com/photo-1581578731548-c64695cc6952?auto=format&fit=crop&w=900&q=80", "description": "Smart robot vacuum with app scheduling."},
    {"id": 16, "name": "Bluetooth Speaker", "price": 39.99, "original_price": 59.99, "rating": 4.5, "reviews": 2021, "category": "Electronics", "badge": "Deal", "brand": "SoundMini", "image": "https://images.unsplash.com/photo-1589003077984-894e133dabab?auto=format&fit=crop&w=900&q=80", "description": "Portable speaker with deep bass and long battery."},
    {"id": 17, "name": "Cookware Set 10-Piece", "price": 129.99, "original_price": 179.99, "rating": 4.6, "reviews": 880, "category": "Home & Kitchen", "badge": "Best Seller", "brand": "PanMaster", "image": "https://images.unsplash.com/photo-1584990347449-a823f0f26f3c?auto=format&fit=crop&w=900&q=80", "description": "Non-stick cookware set for daily cooking."},
    {"id": 18, "name": "DSLR Camera Lens 50mm", "price": 159.00, "original_price": 199.00, "rating": 4.7, "reviews": 740, "category": "Electronics", "badge": "Prime Pick", "brand": "Optix", "image": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=900&q=80", "description": "Prime lens ideal for portraits and low light."},
    {"id": 19, "name": "Laptop Stand", "price": 27.50, "original_price": 39.99, "rating": 4.3, "reviews": 1310, "category": "Computers", "badge": "Top Rated", "brand": "DeskLift", "image": "https://images.unsplash.com/photo-1517336714739-489689fd1ca8?auto=format&fit=crop&w=900&q=80", "description": "Aluminum stand to improve posture and cooling."},
    {"id": 20, "name": "Protein Powder 2lb", "price": 36.99, "original_price": 49.99, "rating": 4.2, "reviews": 2100, "category": "Sports", "badge": "Deal", "brand": "FitFuel", "image": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=900&q=80", "description": "Whey protein blend for muscle recovery."},
    {"id": 21, "name": "Women's Tote Bag", "price": 42.00, "original_price": 59.99, "rating": 4.4, "reviews": 960, "category": "Fashion", "badge": "Prime Pick", "brand": "CityLuxe", "image": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=80", "description": "Spacious tote bag with premium finish."},
    {"id": 22, "name": "LED Desk Lamp", "price": 24.99, "original_price": 34.99, "rating": 4.5, "reviews": 1722, "category": "Home & Kitchen", "badge": "Best Seller", "brand": "BrightDesk", "image": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=900&q=80", "description": "Dimmable LED lamp with USB charging port."},
    {"id": 23, "name": "Tablet 10-inch", "price": 229.99, "original_price": 289.99, "rating": 4.1, "reviews": 515, "category": "Electronics", "badge": "New", "brand": "NovaTab", "image": "https://images.unsplash.com/photo-1561154464-82e9adf32764?auto=format&fit=crop&w=900&q=80", "description": "Portable tablet for reading, streaming, and browsing."},
    {"id": 24, "name": "Wireless Router AX3000", "price": 109.99, "original_price": 149.99, "rating": 4.6, "reviews": 1322, "category": "Computers", "badge": "Top Rated", "brand": "NetFlux", "image": "https://images.unsplash.com/photo-1614624532983-4ce03382d63d?auto=format&fit=crop&w=900&q=80", "description": "Dual-band Wi-Fi 6 router for fast home internet."},
]


def iso_now() -> str:
    return datetime.now(UTC).isoformat()


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                original_price REAL NOT NULL,
                rating REAL NOT NULL,
                reviews INTEGER NOT NULL,
                category TEXT NOT NULL,
                badge TEXT NOT NULL,
                brand TEXT NOT NULL,
                image TEXT NOT NULL,
                description TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS cart_items (
                client_id TEXT NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                PRIMARY KEY (client_id, product_id),
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS wishlist_items (
                client_id TEXT NOT NULL,
                product_id INTEGER NOT NULL,
                PRIMARY KEY (client_id, product_id),
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                client_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                item_count INTEGER NOT NULL,
                subtotal REAL NOT NULL,
                shipping REAL NOT NULL,
                tax REAL NOT NULL,
                total REAL NOT NULL,
                status TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                unit_price REAL NOT NULL,
                line_total REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id)
            );

            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                client_id TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                title TEXT NOT NULL,
                comment TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE (product_id, client_id),
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS coupons (
                code TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                discount_percent INTEGER NOT NULL CHECK (discount_percent BETWEEN 0 AND 100),
                minimum_subtotal REAL NOT NULL DEFAULT 0,
                active INTEGER NOT NULL DEFAULT 1
            );
            """
        )

        order_columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(orders)").fetchall()
        }
        if "coupon_code" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN coupon_code TEXT")
        if "discount" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN discount REAL NOT NULL DEFAULT 0")
        if "shipping_address" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN shipping_address TEXT")

        count = conn.execute("SELECT COUNT(*) AS c FROM products").fetchone()["c"]
        if count == 0:
            conn.executemany(
                """
                INSERT INTO products
                (id, name, price, original_price, rating, reviews, category, badge, brand, image, description)
                VALUES (:id, :name, :price, :original_price, :rating, :reviews, :category, :badge, :brand, :image, :description)
                """,
                PRODUCT_SEED,
            )
        conn.executemany(
            """
            INSERT OR IGNORE INTO coupons
            (code, description, discount_percent, minimum_subtotal, active)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                ("WELCOME10", "10% off orders over $50", 10, 50.0, 1),
                ("SAVE20", "20% off orders over $150", 20, 150.0, 1),
                ("FREESHIP", "Free shipping on any order", 0, 0.0, 1),
            ],
        )


def get_client_id() -> str:
    client_id = request.headers.get("X-Client-Id") or request.args.get("clientId")
    if not client_id:
        abort(400, description="clientId is required")
    return client_id.strip()


def clamp(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(value, max_value))


def parse_int_param(name: str, default: int) -> int:
    raw_value = request.args.get(name, "").strip()
    if not raw_value:
        return default
    try:
        return int(raw_value)
    except ValueError:
        abort(400, description=f"{name} must be an integer")


def parse_float_param(name: str) -> float | None:
    raw_value = request.args.get(name, "").strip()
    if not raw_value:
        return None
    try:
        return float(raw_value)
    except ValueError:
        abort(400, description=f"{name} must be a number")


def product_row_to_dict(row: sqlite3.Row) -> dict:
    price = float(row["price"])
    original_price = float(row["original_price"])
    discount = round((1 - price / original_price) * 100) if original_price else 0
    return {
        "id": row["id"],
        "name": row["name"],
        "price": price,
        "originalPrice": original_price,
        "rating": float(row["rating"]),
        "reviews": int(row["reviews"]),
        "category": row["category"],
        "badge": row["badge"],
        "brand": row["brand"],
        "image": row["image"],
        "description": row["description"],
        "discountPercent": max(0, discount),
    }


def cart_summary(conn: sqlite3.Connection, client_id: str) -> dict:
    rows = conn.execute(
        """
        SELECT p.*, c.quantity
        FROM cart_items c
        JOIN products p ON p.id = c.product_id
        WHERE c.client_id = ?
        ORDER BY p.name
        """,
        (client_id,),
    ).fetchall()

    items = []
    subtotal = 0.0
    total_qty = 0
    for row in rows:
        product = product_row_to_dict(row)
        quantity = int(row["quantity"])
        line_total = round(product["price"] * quantity, 2)
        subtotal += line_total
        total_qty += quantity
        items.append({"product": product, "quantity": quantity, "lineTotal": line_total})

    subtotal = round(subtotal, 2)
    shipping = 0.0 if subtotal == 0 or subtotal >= SHIPPING_THRESHOLD else SHIPPING_FEE
    tax = round(subtotal * TAX_RATE, 2)
    total = round(subtotal + shipping + tax, 2)
    return {
        "items": items,
        "itemCount": total_qty,
        "subtotal": subtotal,
        "shipping": shipping,
        "tax": tax,
        "total": total,
    }


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "atoz-shop", "database": "sqlite", "timestamp": iso_now()})


@app.get("/api/config")
def get_config():
    with get_conn() as conn:
        categories = [r["category"] for r in conn.execute("SELECT DISTINCT category FROM products ORDER BY category").fetchall()]
        min_max = conn.execute("SELECT MIN(price) AS min_price, MAX(price) AS max_price, COUNT(*) AS total FROM products").fetchone()
    return jsonify(
        {
            "categories": categories,
            "priceRange": {"min": float(min_max["min_price"]), "max": float(min_max["max_price"])},
            "sortOptions": ["featured", "price_asc", "price_desc", "rating_desc", "discount_desc"],
            "totalProducts": int(min_max["total"]),
        }
    )


@app.get("/api/products")
def list_products():
    search = request.args.get("search", "").strip().lower()
    category = request.args.get("category", "").strip().lower()
    min_price = parse_float_param("minPrice")
    max_price = parse_float_param("maxPrice")
    min_rating = parse_float_param("minRating")
    sort_by = request.args.get("sort", "featured").strip().lower()
    page = clamp(parse_int_param("page", 1), 1, 10000)
    page_size = clamp(parse_int_param("pageSize", 12), 1, 48)

    filters = []
    params = []
    if search:
        filters.append("(LOWER(name) LIKE ? OR LOWER(description) LIKE ? OR LOWER(brand) LIKE ?)")
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard, wildcard])
    if category and category != "all":
        filters.append("LOWER(category) = ?")
        params.append(category)
    if min_price is not None:
        filters.append("price >= ?")
        params.append(min_price)
    if max_price is not None:
        filters.append("price <= ?")
        params.append(max_price)
    if min_rating is not None:
        filters.append("rating >= ?")
        params.append(min_rating)

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    sort_map = {
        "price_asc": "price ASC",
        "price_desc": "price DESC",
        "rating_desc": "rating DESC, reviews DESC",
        "discount_desc": "(1 - price / original_price) DESC, reviews DESC",
        "featured": "rating DESC, reviews DESC",
    }
    order_clause = sort_map.get(sort_by, sort_map["featured"])
    offset = (page - 1) * page_size

    with get_conn() as conn:
        count_row = conn.execute(f"SELECT COUNT(*) AS c FROM products {where_clause}", params).fetchone()
        total = int(count_row["c"])
        rows = conn.execute(
            f"""
            SELECT *
            FROM products
            {where_clause}
            ORDER BY {order_clause}
            LIMIT ? OFFSET ?
            """,
            params + [page_size, offset],
        ).fetchall()

    products = [product_row_to_dict(row) for row in rows]
    total_pages = max(1, (total + page_size - 1) // page_size)
    return jsonify(
        {
            "products": products,
            "meta": {
                "count": total,
                "page": page,
                "pageSize": page_size,
                "totalPages": total_pages,
                "hasNext": page < total_pages,
                "hasPrev": page > 1,
                "sort": sort_by,
            },
        }
    )


@app.get("/api/products/<int:product_id>")
def get_product(product_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        if not row:
            abort(404, description="Product not found")
        product = product_row_to_dict(row)
        related_rows = conn.execute(
            """
            SELECT * FROM products
            WHERE category = ? AND id != ?
            ORDER BY rating DESC, reviews DESC
            LIMIT 4
            """,
            (row["category"], product_id),
        ).fetchall()
    return jsonify({"product": product, "related": [product_row_to_dict(r) for r in related_rows]})


@app.get("/api/products/<int:product_id>/reviews")
def get_reviews(product_id: int):
    with get_conn() as conn:
        product_exists = conn.execute(
            "SELECT 1 FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        if not product_exists:
            abort(404, description="Product not found")
        rows = conn.execute(
            """
            SELECT rating, title, comment, created_at
            FROM reviews
            WHERE product_id = ?
            ORDER BY created_at DESC
            LIMIT 20
            """,
            (product_id,),
        ).fetchall()
        average = conn.execute(
            "SELECT AVG(rating) AS average, COUNT(*) AS count FROM reviews WHERE product_id = ?",
            (product_id,),
        ).fetchone()
    return jsonify(
        {
            "reviews": [
                {
                    "rating": row["rating"],
                    "title": row["title"],
                    "comment": row["comment"],
                    "createdAt": row["created_at"],
                }
                for row in rows
            ],
            "averageRating": round(float(average["average"]), 1)
            if average["average"] is not None
            else None,
            "count": int(average["count"]),
        }
    )


@app.post("/api/products/<int:product_id>/reviews")
def add_review(product_id: int):
    client_id = get_client_id()
    payload = request.get_json(silent=True) or {}
    rating = payload.get("rating")
    title = str(payload.get("title", "")).strip()
    comment = str(payload.get("comment", "")).strip()
    if not isinstance(rating, int) or not 1 <= rating <= 5:
        abort(400, description="rating must be an integer from 1 to 5")
    if not title or not comment:
        abort(400, description="title and comment are required")
    if len(title) > 100 or len(comment) > 1000:
        abort(400, description="review title or comment is too long")

    with get_conn() as conn:
        product_exists = conn.execute(
            "SELECT 1 FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        if not product_exists:
            abort(404, description="Product not found")
        conn.execute(
            """
            INSERT INTO reviews (product_id, client_id, rating, title, comment, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(product_id, client_id)
            DO UPDATE SET rating = excluded.rating, title = excluded.title,
                          comment = excluded.comment, created_at = excluded.created_at
            """,
            (product_id, client_id, rating, title, comment, iso_now()),
        )
    return jsonify({"ok": True, "message": "Review saved"}), 201


@app.get("/api/deals")
def deals():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM products
            ORDER BY (1 - price / original_price) DESC, reviews DESC
            LIMIT 10
            """
        ).fetchall()
    return jsonify({"deals": [product_row_to_dict(row) for row in rows]})


@app.get("/api/coupons/<string:code>")
def validate_coupon(code: str):
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT code, description, discount_percent, minimum_subtotal
            FROM coupons
            WHERE code = ? AND active = 1
            """,
            (code.strip().upper(),),
        ).fetchone()
    if not row:
        abort(404, description="Coupon not found or inactive")
    return jsonify(
        {
            "code": row["code"],
            "description": row["description"],
            "discountPercent": row["discount_percent"],
            "minimumSubtotal": row["minimum_subtotal"],
        }
    )


@app.get("/api/cart")
def get_cart():
    client_id = get_client_id()
    with get_conn() as conn:
        return jsonify(cart_summary(conn, client_id))


@app.post("/api/cart/items")
def add_cart_item():
    client_id = get_client_id()
    payload = request.get_json(silent=True)
    if not payload:
        abort(400, description="JSON body is required")
    product_id = payload.get("productId")
    quantity = payload.get("quantity", 1)
    if not isinstance(product_id, int):
        abort(400, description="productId must be a valid product id")
    if not isinstance(quantity, int) or quantity < 1:
        abort(400, description="quantity must be a positive integer")

    with get_conn() as conn:
        exists = conn.execute("SELECT 1 FROM products WHERE id = ?", (product_id,)).fetchone()
        if not exists:
            abort(400, description="productId must be a valid product id")
        conn.execute(
            """
            INSERT INTO cart_items (client_id, product_id, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(client_id, product_id)
            DO UPDATE SET quantity = quantity + excluded.quantity
            """,
            (client_id, product_id, quantity),
        )
        return jsonify(cart_summary(conn, client_id)), 201


@app.patch("/api/cart/items/<int:product_id>")
def update_cart_item(product_id: int):
    client_id = get_client_id()
    payload = request.get_json(silent=True)
    if not payload:
        abort(400, description="JSON body is required")
    quantity = payload.get("quantity")
    if not isinstance(quantity, int) or quantity < 1:
        abort(400, description="quantity must be a positive integer")

    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM cart_items WHERE client_id = ? AND product_id = ?",
            (client_id, product_id),
        ).fetchone()
        if not row:
            abort(404, description="Item not found in cart")
        conn.execute(
            "UPDATE cart_items SET quantity = ? WHERE client_id = ? AND product_id = ?",
            (quantity, client_id, product_id),
        )
        return jsonify(cart_summary(conn, client_id))


@app.delete("/api/cart/items/<int:product_id>")
def remove_cart_item(product_id: int):
    client_id = get_client_id()
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM cart_items WHERE client_id = ? AND product_id = ?",
            (client_id, product_id),
        )
        return jsonify(cart_summary(conn, client_id))


@app.delete("/api/cart")
def clear_cart():
    client_id = get_client_id()
    with get_conn() as conn:
        conn.execute("DELETE FROM cart_items WHERE client_id = ?", (client_id,))
        return jsonify(cart_summary(conn, client_id))


@app.get("/api/wishlist")
def get_wishlist():
    client_id = get_client_id()
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT p.*
            FROM wishlist_items w
            JOIN products p ON p.id = w.product_id
            WHERE w.client_id = ?
            ORDER BY p.rating DESC, p.reviews DESC
            """,
            (client_id,),
        ).fetchall()
    items = [product_row_to_dict(row) for row in rows]
    return jsonify({"items": items, "count": len(items)})


@app.post("/api/wishlist/items")
def add_wishlist_item():
    client_id = get_client_id()
    payload = request.get_json(silent=True)
    if not payload:
        abort(400, description="JSON body is required")
    product_id = payload.get("productId")
    if not isinstance(product_id, int):
        abort(400, description="productId must be a valid product id")

    with get_conn() as conn:
        exists = conn.execute("SELECT 1 FROM products WHERE id = ?", (product_id,)).fetchone()
        if not exists:
            abort(400, description="productId must be a valid product id")
        conn.execute(
            "INSERT OR IGNORE INTO wishlist_items (client_id, product_id) VALUES (?, ?)",
            (client_id, product_id),
        )
        count = conn.execute(
            "SELECT COUNT(*) AS c FROM wishlist_items WHERE client_id = ?",
            (client_id,),
        ).fetchone()["c"]
    return jsonify({"ok": True, "wishlistCount": int(count)})


@app.delete("/api/wishlist/items/<int:product_id>")
def remove_wishlist_item(product_id: int):
    client_id = get_client_id()
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM wishlist_items WHERE client_id = ? AND product_id = ?",
            (client_id, product_id),
        )
        count = conn.execute(
            "SELECT COUNT(*) AS c FROM wishlist_items WHERE client_id = ?",
            (client_id,),
        ).fetchone()["c"]
    return jsonify({"ok": True, "wishlistCount": int(count)})


@app.post("/api/checkout")
def checkout():
    client_id = get_client_id()
    payload = request.get_json(silent=True) or {}
    coupon_code = str(payload.get("couponCode", "")).strip().upper() or None
    shipping_address = str(payload.get("shippingAddress", "")).strip()
    with get_conn() as conn:
        summary = cart_summary(conn, client_id)
        if not summary["items"]:
            abort(400, description="Cart is empty")

        discount = 0.0
        if coupon_code:
            coupon = conn.execute(
                """
                SELECT code, discount_percent, minimum_subtotal
                FROM coupons
                WHERE code = ? AND active = 1
                """,
                (coupon_code,),
            ).fetchone()
            if not coupon:
                abort(400, description="Coupon not found or inactive")
            if summary["subtotal"] < coupon["minimum_subtotal"]:
                abort(
                    400,
                    description=f"Coupon requires a subtotal of at least ${coupon['minimum_subtotal']:.2f}",
                )
            discount = round(summary["subtotal"] * coupon["discount_percent"] / 100, 2)
            if coupon_code == "FREESHIP":
                summary["shipping"] = 0.0
            summary["total"] = round(
                summary["subtotal"] + summary["shipping"] + summary["tax"] - discount,
                2,
            )

        order_id = f"ORD-{uuid4().hex[:8].upper()}"
        created_at = iso_now()
        conn.execute(
            """
            INSERT INTO orders
            (order_id, client_id, created_at, item_count, subtotal, shipping, tax,
             total, status, coupon_code, discount, shipping_address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                order_id,
                client_id,
                created_at,
                summary["itemCount"],
                summary["subtotal"],
                summary["shipping"],
                summary["tax"],
                summary["total"],
                "Placed",
                coupon_code,
                discount,
                shipping_address or None,
            ),
        )
        conn.executemany(
            """
            INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    order_id,
                    item["product"]["id"],
                    item["quantity"],
                    item["product"]["price"],
                    item["lineTotal"],
                )
                for item in summary["items"]
            ],
        )
        conn.execute("DELETE FROM cart_items WHERE client_id = ?", (client_id,))

    order = {
        "orderId": order_id,
        "createdAt": created_at,
        "items": summary["items"],
        "itemCount": summary["itemCount"],
        "subtotal": summary["subtotal"],
        "shipping": summary["shipping"],
        "tax": summary["tax"],
        "discount": discount,
        "total": summary["total"],
        "shippingAddress": shipping_address,
        "couponCode": coupon_code,
        "status": "Placed",
    }
    return jsonify({"message": "Order placed successfully", "order": order})


@app.get("/api/orders")
def orders():
    client_id = get_client_id()
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT order_id, created_at, item_count, total, status
                   , subtotal, shipping, tax, coupon_code, discount, shipping_address
            FROM orders
            WHERE client_id = ?
            ORDER BY created_at DESC
            LIMIT 10
            """,
            (client_id,),
        ).fetchall()

    items = [
        {
            "orderId": row["order_id"],
            "createdAt": row["created_at"],
            "itemCount": int(row["item_count"]),
            "subtotal": float(row["subtotal"]),
            "shipping": float(row["shipping"]),
            "tax": float(row["tax"]),
            "couponCode": row["coupon_code"],
            "discount": float(row["discount"]),
            "shippingAddress": row["shipping_address"],
            "total": float(row["total"]),
            "status": row["status"],
        }
        for row in rows
    ]
    return jsonify({"orders": items, "count": len(items)})


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

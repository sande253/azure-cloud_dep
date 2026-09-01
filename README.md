# AtoZ Shop (Massive Overhaul)

An Amazon-style fullstack e-commerce demo built with:
- **Frontend**: Responsive HTML/CSS/vanilla JavaScript UI
- **Backend**: Flask APIs with catalog, cart, wishlist, deals, and orders
- **Database**: SQLite (`app.db`) for persistent products/cart/wishlist/orders

What changed in the overhaul:
- Expanded catalog to **24 products** across multiple categories
- Added **filtering** (category, price range, rating), **sorting**, and **pagination**
- Added **deals feed** and **quick product view**
- Added **wishlist APIs + UI**
- Added **order history APIs + UI**
- Upgraded visual design and responsiveness for desktop and mobile
- Replaced in-memory backend state with a real **SQLite database**

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000`.

On first start, the app auto-creates `app.db` and seeds products.

## API endpoints

- `GET /api/health`
- `GET /api/config`
- `GET /api/products?search=...&category=...&minPrice=...&maxPrice=...&minRating=...&sort=...&page=...&pageSize=...`
- `GET /api/products/<product_id>` (includes related products)
- `GET /api/deals`
- `GET /api/cart?clientId=<client-id>`
- `POST /api/cart/items?clientId=<client-id>`
- `PATCH /api/cart/items/<product_id>?clientId=<client-id>`
- `DELETE /api/cart/items/<product_id>?clientId=<client-id>`
- `DELETE /api/cart?clientId=<client-id>`
- `GET /api/wishlist?clientId=<client-id>`
- `POST /api/wishlist/items?clientId=<client-id>`
- `DELETE /api/wishlist/items/<product_id>?clientId=<client-id>`
- `POST /api/checkout?clientId=<client-id>`
- `GET /api/orders?clientId=<client-id>`

`POST /api/cart/items` body example:
```json
{ "productId": 1, "quantity": 2 }
```

`POST /api/wishlist/items` body example:
```json
{ "productId": 4 }
```

## Deploy with Docker

```bash
docker build -t atoz-shop .
docker run -e PORT=8080 -p 8080:8080 atoz-shop
```

Open `http://localhost:8080`.

Note: in container deployments, SQLite data is ephemeral unless you mount a volume.

## Deploy to Procfile-based PaaS (Render/Heroku-like)

Build command:
```bash
pip install -r requirements.txt
```

Start command:
```bash
gunicorn --bind 0.0.0.0:$PORT main:app
```

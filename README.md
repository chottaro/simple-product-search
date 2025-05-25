# Simple Product Search

A web application that allows you to search for products across multiple e-commerce platforms — Yahoo Shopping, Rakuten, and eBay — using keywords or JAN codes. It displays the lowest and highest prices along with product images side-by-side for easy comparison.

## 🚀 Features

- 🔍 **Keyword or JAN Code Search**
  - Search products using a keyword or JAN (Japanese Article Number) code.
- 🏬 **Multi-store Integration**
  - Aggregates product data from Yahoo, Rakuten, and eBay.
- 🌐 **Automatic keyword translation (JP ↔ EN)**
- ⚡ **Asynchronous Backend Processing**
  - API requests are made concurrently to speed up search results.
- 🖼️ **Side-by-side Product Display**
  - Images and price ranges are displayed horizontally per store per product.
- 📊 **Result Count Display**
  - Shows the number of product results after each search.
- 📦 **Docker & Docker Compose ready**
- ✅ **Built-in test with pytest**

## 🛠️ Tech Stack

| Layer  | Technology |
| ------------- | ------------- |
| Frontend  | Next.js, TypeScript, Tailwind CSS  |
| Backend | Python 3.11, FastAPI, requests, googletrans, pytest + pytest-asyncio  |
| Containerization  | Docker, Docker Compose  |

## 📂 Project Structure

```
simple-product-search/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api.py        # Main API endpoint
│   │   ├── main.py       # CLI entry point
│   │   ├── services/     # Logic for Yahoo, Rakuten, eBay
│   ├── .env              # (You must create this)
│   └── ...
├── frontend/             # Next.js frontend
│   ├── app/
│   │   └── page.tsx      # Main search UI
│   ├── public/
│   └── ...
├── docker-compose.yml    # Container orchestration
└── ...
```

## ⚙️ Getting Started

### 1. Clone the repository

```
git clone https://github.com/chottaro/simple-product-search.git
cd simple-product-search
```

### 2. Prepare your .env
Create a `.env` file in the backend directory:

```
YAHOO_APP_ID=your_yahoo_client_id
RAKUTEN_APP_ID=your_rakuten_app_id
EBAY_APP_ID=your_ebay_app_id
EBAY_CLIENT_SECRET=your_ebay_client_secret
```

### 3. Run with Docker
```
docker-compose up --build
```

## 🧪 Run Tests
```
docker-compose run --rm backend pytest
```
## 📘 Usage
Browser
```
http://localhost:3000
```

API
```
GET http://localhost:8000/search?keyword=nintendo+switch
```

CLI (inside container)
```
docker-compose exec backend python -m app.main "nintendo switch"
```

## 🔐 License
This project is licensed under the MIT License.

## 🙏 Acknowledgements
- Yahoo API
- Rakuten Ichiba API
- eBay Buy API
- googletrans for translation
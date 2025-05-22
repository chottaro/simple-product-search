# Simple Product Search

Simple Product Search is a Python-based tool that allows you to search products from Rakuten and eBay by keyword or JAN code, aggregate the results, and return unified JSON data.

It supports Docker and provides both CLI and API interfaces.

## 🚀 Features

- 🔍 Keyword-based and JAN-code-based product search
- 🏬 Multi-store support: Rakuten & eBay
- 🌐 Automatic keyword translation (JP ↔ EN)
- 🧠 Similarity-based product grouping
- 📦 Docker & Docker Compose ready
- ✅ Built-in test with pytest

## 🛠️ Tech Stack

- Python 3.11
- FastAPI
- requests
- googletrans
- pytest + pytest-asyncio
- Docker / Docker Compose

## 📂 Project Structure

```
simple-product-search/
├── app/
│ ├── common/ # Enums and shared data definitions
│ ├── search/ # Rakuten and eBay search logic
│ ├── services/ # Utilities: translation, request, formatting
│ ├── api.py # FastAPI entry point
│ └── main.py # CLI entry point
├── tests/ # Unit tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env # (You must create this)
```

## ⚙️ Setup

### 1. Clone the repository

```
git clone https://github.com/chottaro/simple-product-search.git
cd simple-product-search
```

### 2. Prepare your .env
Create a .env file in the root directory:

```
RAKUTEN_APP_ID=your_rakuten_app_id
EBAY_APP_ID=your_ebay_app_id
EBAY_CLIENT_SECRET=your_ebay_client_secret
```

### 3. Run with Docker
```
docker-compose up --build
```

## 🧪 Run Tests


docker-compose exec app pytest
## 📘 Usage
CLI (inside container)
```
docker-compose exec app python -m app.main "nintendo switch"
```

API
After running the container, access:

```
GET http://localhost:8000/search?keyword=nintendo+switch
```

## 🔐 License
This project is licensed under the MIT License.
You can use, modify, and distribute this code freely without requiring prior approval.

## 🙏 Acknowledgements
- Rakuten Ichiba API
- eBay Buy API
- googletrans for translation
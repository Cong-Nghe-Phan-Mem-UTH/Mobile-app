# BigBoy Backend API

SaaS Smart Restaurant Management Platform - Backend API (Flask)

## Công nghệ sử dụng

- **Framework**: Flask 2.3+
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Authentication**: JWT
- **Language**: Python 3.11+

## Cài đặt

```bash
# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt

# Copy và cấu hình .env
cp .env.example .env
# Chỉnh sửa .env với thông tin database của bạn

# Chạy development server
python app/main.py
# hoặc
flask run --host=0.0.0.0 --port=4000
```

## API Endpoints

Xem chi tiết trong [README.md](../README.md) hoặc chạy server và truy cập `/test` để kiểm tra.

## Cấu trúc Project

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/          # API routes (Flask blueprints)
│   │   ├── decorators.py    # Authentication decorators
│   │   └── middleware.py    # Middleware
│   ├── infrastructure/
│   │   └── databases/       # Database setup
│   ├── models/              # SQLAlchemy models
│   ├── services/            # Business logic services
│   ├── utils/               # Utilities
│   ├── config.py            # Configuration
│   ├── create_app.py        # Flask app factory
│   ├── main.py             # Entry point
│   └── error_handler.py     # Error handling
├── requirements.txt
└── README.md
```

## Development

```bash
# Development với auto-reload
python app/main.py

# Hoặc dùng Flask CLI
export FLASK_APP=app/main.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=4000
```

## Tài khoản mặc định

Sau khi setup database:
- **Email**: admin@bigboy.com
- **Password**: 123456

# Provokely - Social Media Sentiment Analysis Platform

**API-First Platform for Mobile Apps**

A Django-based modular social media sentiment analysis and auto-commenting system that works across multiple platforms (starting with Instagram) using AI-driven responses based on comment sentiment analysis.

## 🏗️ Project Structure

```
provokely/
├── config/                          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                            # Core platform-agnostic functionality
│   ├── models.py                    # Comment, Post models
│   ├── serializers.py               # DRF serializers
│   ├── views.py                     # API ViewSets
│   ├── services.py                  # Business logic
│   ├── sentiment.py                 # Sentiment analysis
│   └── responses.py                 # AI response generation
├── shared/                          # Shared code and interfaces
│   ├── models.py                    # Abstract base models
│   ├── interfaces.py                # Abstract interfaces
│   ├── exceptions.py                # Custom exceptions
│   └── api_responses.py             # Standard API response helpers
├── platforms/                       # Platform-specific apps
│   └── instagram/                   # Instagram integration
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── services.py
│       ├── config.py
│       └── urls.py
├── static/                          # Static files
├── templates/                       # Templates (landing page)
└── requirements.txt
```

## 🚀 Key Features

- **API-First Design**: RESTful API for mobile app consumption
- **Modular Architecture**: Platform-agnostic core with platform-specific adapters
- **Full CRUD Operations**: Complete Create, Read, Update, Delete support
- **Sentiment Analysis**: AI-powered sentiment analysis for social media comments
- **Auto-Response Generation**: Intelligent response generation based on sentiment
- **Token Authentication**: Secure token-based authentication for mobile apps
- **Comprehensive Documentation**: API documentation with drf-yasg
- **Pagination Support**: Efficient pagination for list endpoints
- **Filtering & Search**: Advanced filtering and search capabilities

## 📱 Mobile App Support

This project is designed to serve mobile applications with:
- JSON-only responses
- Proper HTTP status codes (200, 201, 400, 401, 404, 500)
- Token-based authentication
- CORS configuration for mobile development
- Standardized response formats

### Standard API Response Format

**Success Response:**
```json
{
    "success": true,
    "data": {...},
    "message": "Operation successful"
}
```

**Error Response:**
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": {...}
    }
}
```

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd provokely
```

### 2. Create Virtual Environment
```bash
python -m venv pro_env
source pro_env/bin/activate  # On Windows: pro_env\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

## 📚 API Endpoints

### Core Endpoints
- `GET /api/v1/core/comments/` - List all comments
- `POST /api/v1/core/comments/` - Create a comment
- `GET /api/v1/core/comments/{id}/` - Retrieve a comment
- `PUT /api/v1/core/comments/{id}/` - Update a comment
- `DELETE /api/v1/core/comments/{id}/` - Delete a comment
- `POST /api/v1/core/comments/{id}/analyze_sentiment/` - Analyze sentiment
- `GET /api/v1/core/posts/` - List all posts
- `POST /api/v1/core/posts/` - Create a post
- `GET /api/v1/core/posts/statistics/` - Get statistics

### Instagram Endpoints
- `GET /api/v1/instagram/accounts/` - List Instagram accounts
- `POST /api/v1/instagram/accounts/` - Create Instagram account
- `GET /api/v1/instagram/accounts/{id}/` - Retrieve account
- `PUT /api/v1/instagram/accounts/{id}/` - Update account
- `DELETE /api/v1/instagram/accounts/{id}/` - Delete account
- `POST /api/v1/instagram/accounts/{id}/sync_posts/` - Sync posts
- `POST /api/v1/instagram/accounts/{id}/sync_comments/` - Sync comments
- `GET /api/v1/instagram/accounts/{id}/statistics/` - Get account stats
- `GET /api/v1/instagram/webhooks/` - List webhooks

### Authentication
- `POST /api/v1/auth/login/` - Login and get token
- `POST /api/v1/auth/logout/` - Logout

## 🔐 Authentication

The API uses token-based authentication. To authenticate:

1. Create a user account (superuser or via admin)
2. Obtain a token:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

3. Include the token in subsequent requests:
```bash
curl -H "Authorization: Token your_token_here" http://localhost:8000/api/v1/core/comments/
```

## 🎯 Development Principles

1. **Modular Design**: Never duplicate functionality across platforms
2. **API-First**: All endpoints return JSON with proper HTTP status codes
3. **CRUD Operations**: Every resource supports full CRUD operations
4. **Platform-Agnostic Core**: Sentiment analysis and response generation work across all platforms
5. **Configuration-Driven**: Platform-specific behavior controlled via config files
6. **Django Best Practices**: Follow Django conventions and patterns

## 📦 Adding New Platforms

To add a new platform (e.g., Facebook, YouTube):

1. Create new Django app: `python manage.py startapp facebook platforms/facebook`
2. Define platform-specific models in `platforms/facebook/models.py`
3. Create serializers in `platforms/facebook/serializers.py`
4. Implement API views in `platforms/facebook/views.py`
5. Create service layer in `platforms/facebook/services.py`
6. Add configuration in `platforms/facebook/config.py`
7. Register URLs in `platforms/facebook/urls.py`
8. Add to `INSTALLED_APPS` in `config/settings.py`
9. Include URLs in `config/urls.py`

The core sentiment analysis and response generation will work automatically!

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.
```

## 📝 TODO

- [ ] Implement Instagram Graph API integration
- [ ] Add advanced sentiment analysis with transformers
- [ ] Implement AI response generation with GPT/Claude
- [ ] Add webhook handling for real-time updates
- [ ] Implement background tasks with Celery
- [ ] Add caching with Redis
- [ ] Write comprehensive tests
- [ ] Add API rate limiting
- [ ] Implement user roles and permissions
- [ ] Add Facebook platform support
- [ ] Add YouTube platform support
- [ ] Add Twitter platform support

## 📄 License

[Your License Here]

## 👥 Contributors

[Your Name/Team]

---

**Built with Django REST Framework for Mobile Apps** 📱

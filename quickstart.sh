#!/bin/bash

echo "========================================="
echo "Provokely - Quick Start Script"
echo "========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "pro_env" ]; then
    echo "Creating virtual environment..."
    python -m venv pro_env
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source pro_env/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create migrations
echo ""
echo "Creating migrations..."
python manage.py makemigrations core
python manage.py makemigrations instagram

# Apply migrations
echo ""
echo "Applying migrations..."
python manage.py migrate

# Create superuser prompt
echo ""
echo "========================================="
echo "Setup complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Create a superuser: python manage.py createsuperuser"
echo "2. Create API token: python manage.py create_token <username>"
echo "3. Start server: python manage.py runserver"
echo "4. Visit: http://localhost:8000/admin/"
echo "5. API endpoints: http://localhost:8000/api/v1/"
echo ""
echo "API Documentation will be available at:"
echo "- Swagger UI: http://localhost:8000/api/docs/"
echo "- ReDoc: http://localhost:8000/api/redoc/"
echo ""

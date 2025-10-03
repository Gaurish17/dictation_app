# Simple Makefile for Suyog Flask App

.PHONY: setup install run dev prod clean help activate

setup:
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	mkdir -p uploads typing_passages instance

activate:
	@echo "To activate virtual environment, run: source venv/bin/activate"

install:
	./venv/bin/pip install -r requirements.txt

dev:
	@echo "Starting app in development mode..."
	bash -c "source venv/bin/activate && python app.py"

run:
	@echo "Starting app..."
	bash -c "source venv/bin/activate && python app.py"

prod:
	@echo "Starting with gunicorn..."
	bash -c "source venv/bin/activate && gunicorn --bind 0.0.0.0:5000 --workers 2 app:app"

init-db:
	bash -c "source venv/bin/activate && python -c 'from app import init_db; init_db()'"

clean:
	rm -rf venv __pycache__ *.pyc

# Production deployment
deploy-prep:
@echo "Preparing for production deployment..."
cp .env.production .env
@echo "✅ Environment file copied"
@echo "⚠️  Remember to update .env with your actual values!"

deploy-zip:
@echo "Creating deployment package..."
zip -r dictation_app_deploy.zip . -x "venv/*" "__pycache__/*" "*.pyc" ".git/*" "*.db" "instance/*"
@echo "✅ Deployment package created: dictation_app_deploy.zip"

test-wsgi:
@echo "Testing WSGI application..."
bash -c "source venv/bin/activate && python wsgi.py"

help:
@echo "Available commands:"
@echo ""
@echo "Development:"
@echo "  make setup     - Create venv and install dependencies"
@echo "  make activate  - Show how to activate venv manually"
@echo "  make install   - Install/update dependencies"
@echo "  make dev       - Run in development mode"
@echo "  make run       - Run app"
@echo "  make init-db   - Initialize database"
@echo ""
@echo "Production:"
@echo "  make prod      - Run with gunicorn server"
@echo "  make deploy-prep - Prepare for deployment"
@echo "  make deploy-zip  - Create deployment package"
@echo "  make test-wsgi   - Test WSGI application"
@echo ""
@echo "Maintenance:"
@echo "  make clean     - Remove venv and cache files"

#!/bin/bash

# Hostinger VPS Deployment Script for Fairy Dance Studio
# Run this on your Hostinger VPS with Ubuntu 24.04 + Docker template

set -e  # Exit on error

echo "🚀 Starting Fairy Dance Studio Deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please use Hostinger's Docker template or install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Installing..."
    sudo apt-get update
    sudo apt-get install -y docker-compose-plugin
fi

# Clone repository if not exists
if [ ! -d "fairy" ]; then
    echo "📦 Cloning repository..."
    read -p "Enter your GitHub repository URL: " REPO_URL
    git clone "$REPO_URL" fairy
fi

cd fairy

# Create production environment file if not exists
if [ ! -f ".env.production" ]; then
    echo "📝 Creating production environment file..."
    cp .env.example .env.production

    # Generate secret keys
    echo "🔐 Generating security keys..."
    if [ -f "backend/generate_secret_key.py" ]; then
        python3 backend/generate_secret_key.py > keys.txt
        SECRET_KEY=$(grep "SECRET_KEY" keys.txt | cut -d'=' -f2)
        JWT_SECRET_KEY=$(grep "JWT_SECRET_KEY" keys.txt | cut -d'=' -f2)
        rm keys.txt
    else
        # Fallback key generation
        SECRET_KEY=$(openssl rand -hex 32)
        JWT_SECRET_KEY=$(openssl rand -hex 32)
    fi

    # Update .env.production with generated keys
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env.production
    sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET_KEY/" .env.production

    echo "⚠️  Please edit .env.production to set:"
    echo "   - Your domain name in ALLOWED_HOSTS"
    echo "   - Database password (DB_PASSWORD)"
    echo "   - Admin credentials"
    echo ""
    read -p "Press Enter after editing .env.production..."
fi

# Update nginx configuration
echo "🔧 Configuring Nginx..."
read -p "Enter your domain name (e.g., example.com): " DOMAIN
if [ ! -z "$DOMAIN" ]; then
    # Backup original nginx config
    cp nginx/nginx.conf nginx/nginx.conf.backup
    # Replace placeholder with actual domain
    sed -i "s/yourdomain.com/$DOMAIN/g" nginx/nginx.conf
fi

# Pull and build Docker images
echo "🐳 Building Docker containers..."
docker-compose -f docker-compose.prod.yml build

# Start services
echo "🚀 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for database to be ready
echo "⏳ Waiting for database..."
sleep 10

# Run migrations
echo "📊 Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput

# Create superuser if requested
read -p "Do you want to create a superuser account? (y/n): " CREATE_SUPERUSER
if [ "$CREATE_SUPERUSER" = "y" ]; then
    docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
fi

# Install SSL certificate
read -p "Do you want to set up SSL with Let's Encrypt? (y/n): " SETUP_SSL
if [ "$SETUP_SSL" = "y" ]; then
    echo "🔒 Setting up SSL..."
    sudo apt-get update
    sudo apt-get install -y certbot python3-certbot-nginx
    sudo certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN"
fi

# Show status
echo ""
echo "✅ Deployment complete!"
echo ""
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "📌 Your application is available at:"
if [ "$SETUP_SSL" = "y" ]; then
    echo "   Frontend: https://$DOMAIN"
    echo "   Admin: https://$DOMAIN/admin"
    echo "   API Docs: https://$DOMAIN/api/schema/swagger-ui/"
else
    echo "   Frontend: http://$DOMAIN"
    echo "   Admin: http://$DOMAIN/admin"
    echo "   API Docs: http://$DOMAIN/api/schema/swagger-ui/"
fi

echo ""
echo "📚 Useful commands:"
echo "   View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   Restart: docker-compose -f docker-compose.prod.yml restart"
echo "   Stop: docker-compose -f docker-compose.prod.yml down"
echo "   Backup DB: docker-compose -f docker-compose.prod.yml exec db pg_dump -U fairy_user fairy_db > backup.sql"
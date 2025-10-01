# Fairy Dance Studio Management System

A comprehensive web application for managing dance studio operations including student enrollment, class scheduling, attendance tracking, and invoicing.

## Features

- **Student & Guardian Management** - Track students, guardians, and billing contacts with Account-based architecture
- **Class Scheduling** - Manage dance classes, terms, and enrollments
- **Attendance Tracking** - Mark and monitor class attendance
- **Financial Management** - Generate invoices and track payments
- **Parent Portal** - Self-service access for parents
- **Multi-Role Support** - Admin, staff, teacher, and parent roles

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework, PostgreSQL
- **Frontend**: React 19, Vite, Tailwind CSS
- **Infrastructure**: Docker, Nginx, Redis
- **Security**: JWT authentication, HTTPS, input sanitization

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fairy.git
cd fairy
```

2. Copy environment template:
```bash
cp .env.example .env
```

3. Edit `.env` with your configuration

4. Start services:
```bash
docker-compose up -d
```

5. Run migrations:
```bash
docker-compose exec backend python manage.py migrate
```

6. Create admin user:
```bash
docker-compose exec backend python manage.py createsuperuser
```

7. Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api
- Admin Panel: http://localhost:8000/admin

## Production Deployment

See [HOSTINGER_DEPLOYMENT.md](./HOSTINGER_DEPLOYMENT.md) for detailed production deployment instructions.

For quick deployment on Hostinger VPS with Docker:
```bash
./scripts/hostinger-deploy.sh
```

## Environment Variables

Key environment variables (see `.env.example` for full list):

- `SECRET_KEY` - Django secret key (generate with `python backend/generate_secret_key.py`)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD` - Database credentials
- `ALLOWED_HOSTS` - Comma-separated list of allowed hostnames
- `DEBUG` - Set to False in production

## API Documentation

When running locally, OpenAPI documentation is available at:
http://localhost:8000/api/schema/swagger-ui/

## Security

- All user input is sanitized using bleach
- HTTPS enforced in production
- JWT tokens stored in httpOnly cookies
- Regular security updates via GitHub Dependabot

See [SECURITY_CHECKLIST.md](./SECURITY_CHECKLIST.md) for deployment security guidelines.

## License

Proprietary - All rights reserved

## Support

For issues and questions, please contact the development team.
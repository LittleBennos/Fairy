# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2024-10-01

### Added
- Initial release of Fairy Dance Studio Management System
- Django REST API backend with PostgreSQL database
- React frontend with Tailwind CSS
- Docker containerization for easy deployment
- Account-based architecture for flexible enrollment management
- Student, Guardian, and BillingContact management
- Class scheduling and enrollment system
- Attendance tracking functionality
- Invoice generation and payment tracking
- JWT authentication with httpOnly cookies
- Input sanitization for security
- Comprehensive API documentation with OpenAPI
- Production-ready deployment configuration
- Hostinger VPS deployment guide and scripts

### Security
- Implemented bleach for HTML sanitization
- Added HTTPS enforcement for production
- Configured secure cookie settings
- Added rate limiting on API endpoints
- Implemented CORS protection
- Added Content Security Policy headers

### Infrastructure
- Docker Compose for development and production
- Nginx reverse proxy configuration
- Redis caching support
- GitHub Actions for CI/CD
- Automated security scanning

[1.0.0]: https://github.com/LittleBennos/Fairy/releases/tag/v1.0.0
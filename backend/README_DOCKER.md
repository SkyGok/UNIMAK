# Docker Deployment Guide

## Quick Start

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** with your configuration (especially SECRET_KEY and DB_PASSWORD)

3. **Start services:**
   ```bash
   docker-compose up -d --build
   ```

4. **Check logs:**
   ```bash
   docker-compose logs -f
   ```

5. **Create admin user:**
   ```bash
   docker-compose exec web python3
   ```
   
   Then in Python:
   ```python
   from db import Database
   from werkzeug.security import generate_password_hash
   
   db = Database()
   password_hash = generate_password_hash('your-secure-password')
   db.execute(
       "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
       'admin', password_hash, 'admin'
   )
   ```

6. **Access application:**
   - Main: http://localhost:5000/df/
   - Admin: http://localhost:5000/df/admin (admin only)

## Services

- **web**: Flask application (port 5000)
- **db**: PostgreSQL database (port 5432)

## Volumes

- `postgres_data`: PostgreSQL data persistence
- `./uploads:/uploads`: Upload directory mounted from host

## Environment Variables

See `.env.example` for all available variables.

## Stopping Services

```bash
docker-compose down
```

## Removing Everything (including data)

```bash
docker-compose down -v
```

## Database Backup

```bash
docker-compose exec db pg_dump -U postgres unimak > backup.sql
```

## Database Restore

```bash
docker-compose exec -T db psql -U postgres unimak < backup.sql
```


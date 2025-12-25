# Conversion Summary: Flask to PostgreSQL with Docker

## ✅ Completed Changes

### 1. PostgreSQL Migration
- ✅ Created `db.py` wrapper for PostgreSQL compatibility
- ✅ Replaced all SQLite `?` placeholders with PostgreSQL `%s`
- ✅ Updated database connection to use PostgreSQL
- ✅ Created `init_db.sql` with PostgreSQL schema including `role` column

### 2. Docker Deployment
- ✅ Updated `Dockerfile` for PostgreSQL support
- ✅ Created `docker-compose.yml` with PostgreSQL service
- ✅ Configured volume mounts for uploads
- ✅ Added health checks for database

### 3. URL Base Path `/df`
- ✅ All routes prefixed with `/df`
- ✅ Updated all templates with `/df` prefix
- ✅ Updated redirects and form actions
- ✅ Updated file serving route: `/df/uploads/<path:filename>`

### 4. Media Uploads to `/uploads`
- ✅ Changed upload directory from `static/files/uploads` to `/uploads`
- ✅ Updated file serving route
- ✅ Updated all template image paths

### 5. Role-Based Access Control
- ✅ Added `role` column to users table (default: 'user')
- ✅ Created `admin_required` decorator
- ✅ Protected admin routes with `@admin_required`
- ✅ Admin button hidden in navigation for non-admin users
- ✅ Role stored in session on login

### 6. User ID Filtering
- ✅ Home page: Problems filtered by `user_id`
- ✅ Upload page: Projects filtered by user (non-admin)
- ✅ Info page: Problems filtered by `user_id`
- ✅ History page: Problem steps filtered by `user_id`
- ✅ Admin panel: Admins see all data (no filter)

## 📁 Files Modified

### Backend Files
- `app.py` - Complete rewrite for PostgreSQL, /df prefix, role-based access
- `db.py` - NEW: PostgreSQL database wrapper
- `helpers.py` - Added `admin_required` decorator, updated redirects
- `requirements.txt` - Added psycopg2-binary, python-dotenv
- `Dockerfile` - Updated for PostgreSQL
- `docker-compose.yml` - NEW: Docker Compose configuration
- `init_db.sql` - NEW: PostgreSQL schema

### Template Files
- `layout.html` - Updated links, hidden admin button for non-admins
- `admin.html` - Updated all routes to /df
- `upload.html` - Updated form action
- `partials/card_view.html` - Updated image paths
- `partials/card_view_table.html` - Updated image paths

## 🚀 Quick Start

### 1. Setup Environment
```bash
cd backend
cp .env.example .env
# Edit .env with your configuration
```

### 2. Start with Docker
```bash
docker-compose up -d --build
```

### 3. Create Admin User
```bash
docker-compose exec web python3
```

```python
from db import Database
from werkzeug.security import generate_password_hash

db = Database()
password_hash = generate_password_hash('admin123')
db.execute(
    "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
    'admin', password_hash, 'admin'
)
```

### 4. Access Application
- Main App: http://localhost:5000/df/
- Login: http://localhost:5000/df/login
- Admin Panel: http://localhost:5000/df/admin (admin only)

## 🔒 Security Features

1. **Role-Based Access**: Admin routes protected
2. **User Filtering**: All queries filter by user_id (except admin panel)
3. **Session Management**: Role stored in session
4. **Navigation Security**: Admin button only visible to admins

## 📝 Important Notes

1. **Database**: PostgreSQL is required (no longer SQLite)
2. **Uploads**: Files stored in `/uploads` (mounted volume in Docker)
3. **URLs**: All URLs must include `/df` prefix
4. **Roles**: Users default to 'user' role, must manually set 'admin'
5. **Environment**: Use `.env` file for configuration

## 🧪 Testing Checklist

- [ ] Docker containers start successfully
- [ ] Database connection works
- [ ] User registration creates user with 'user' role
- [ ] Login stores role in session
- [ ] Admin panel accessible only to admins
- [ ] Admin button hidden for non-admin users
- [ ] Home page shows only user's problems
- [ ] File uploads work and served from `/df/uploads`
- [ ] All routes accessible with `/df` prefix

## 🔧 Troubleshooting

### Database Connection
- Check `docker-compose.yml` environment variables
- Verify PostgreSQL container: `docker-compose ps`
- Check logs: `docker-compose logs db`

### Permission Issues
- Ensure `/uploads` directory has correct permissions
- Check Docker volume mounts

### Role Issues
- Verify user has `role='admin'` in database
- Clear browser cookies/session
- Check session contains role after login


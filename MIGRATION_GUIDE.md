# Migration Guide: SQLite to PostgreSQL with Docker

## Overview
This guide covers the migration from SQLite to PostgreSQL, Docker deployment, and role-based access control implementation.

## Changes Made

### 1. Database Migration (SQLite → PostgreSQL)
- **New Database Wrapper**: Created `db.py` with PostgreSQL-compatible interface
- **SQL Query Updates**: All `?` placeholders changed to `%s` for PostgreSQL
- **Schema Updates**: Added `role` column to `users` table
- **Indexes**: Added performance indexes on foreign keys and frequently queried columns

### 2. Docker Deployment
- **Dockerfile**: Updated for PostgreSQL support
- **docker-compose.yml**: Added PostgreSQL service with health checks
- **Volume Mounts**: Uploads directory mounted as volume
- **Environment Variables**: Database connection via environment variables

### 3. URL Base Path `/df`
- All routes now prefixed with `/df`
- Updated all templates to use `/df` prefix
- Updated redirects and form actions

### 4. Media Uploads to `/uploads`
- Changed from `static/files/uploads` to `/uploads`
- Updated file serving route: `/df/uploads/<path:filename>`
- Updated all template references to use new path

### 5. Role-Based Access Control
- **Role Column**: Added to `users` table (default: 'user')
- **Admin Decorator**: Created `admin_required` decorator in `helpers.py`
- **Admin Routes**: Protected with `@admin_required`
- **Navigation**: Admin button hidden for non-admin users
- **Session**: Role stored in session on login

### 6. User ID Filtering
- **Home Page**: Problems filtered by `user_id`
- **Upload Page**: Projects filtered by user (non-admin users only see their projects)
- **Info Page**: Problems filtered by `user_id`
- **History Page**: Problem steps filtered by `user_id`
- **Admin Panel**: Admins see all data (no user_id filter)

## File Structure

```
backend/
├── app.py              # Main application (updated for PostgreSQL)
├── db.py               # PostgreSQL database wrapper (NEW)
├── helpers.py           # Updated with admin_required decorator
├── Dockerfile          # Updated for PostgreSQL
├── docker-compose.yml  # Docker Compose configuration (NEW)
├── init_db.sql         # PostgreSQL schema (NEW)
├── requirements.txt    # Updated dependencies
└── templates/          # All templates updated with /df prefix
```

## Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Database Configuration
DB_HOST=db
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=unimak
DB_PORT=5432

# Application Configuration
SECRET_KEY=your-secret-key-here-change-in-production
UPLOADS_DIR=/uploads

# Or use DATABASE_URL (takes precedence)
DATABASE_URL=postgresql://postgres:postgres@db:5432/unimak
```

## Deployment Steps

### 1. Build and Start Containers
```bash
cd backend
docker-compose up -d --build
```

### 2. Initialize Database
The database schema is automatically initialized via `init_db.sql` when the PostgreSQL container starts.

### 3. Create Admin User
```bash
docker-compose exec web python3
```

Then in Python:
```python
from db import Database
from werkzeug.security import generate_password_hash

db = Database()
password_hash = generate_password_hash('your-admin-password')
db.execute(
    "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
    'admin', password_hash, 'admin'
)
```

### 4. Access Application
- Application URL: `http://localhost:5000/df/`
- Login: `http://localhost:5000/df/login`
- Admin Panel: `http://localhost:5000/df/admin` (admin only)

## Database Schema Changes

### Users Table
```sql
ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin'));
```

### Indexes Added
```sql
CREATE INDEX idx_problems_user_id ON problems(user_id);
CREATE INDEX idx_problems_project_id ON problems(project_id);
CREATE INDEX idx_problem_components_problem_id ON problem_components(problem_id);
CREATE INDEX idx_problem_steps_problem_id ON problem_steps(problem_id);
CREATE INDEX idx_users_role ON users(role);
```

## Route Changes

| Old Route | New Route |
|-----------|-----------|
| `/` | `/df/` |
| `/login` | `/df/login` |
| `/register` | `/df/register` |
| `/upload` | `/df/upload` |
| `/admin` | `/df/admin` (admin only) |
| `/info` | `/df/info` |
| `/history` | `/df/history` |

## Security Updates

1. **Role-Based Access**: Admin routes protected with `@admin_required`
2. **User Filtering**: All user-facing queries filter by `user_id`
3. **Session Security**: Role stored in session, checked on each request
4. **Navigation**: Admin button only visible to admins

## Testing Checklist

- [ ] Docker containers start successfully
- [ ] Database connection works
- [ ] User registration creates user with 'user' role
- [ ] Login stores role in session
- [ ] Admin panel accessible only to admins
- [ ] Admin button hidden for non-admin users
- [ ] Home page shows only user's problems
- [ ] Upload page filters projects by user (non-admin)
- [ ] File uploads work and are served from `/df/uploads`
- [ ] All routes accessible with `/df` prefix

## Troubleshooting

### Database Connection Issues
- Check `docker-compose.yml` environment variables
- Verify PostgreSQL container is healthy: `docker-compose ps`
- Check logs: `docker-compose logs db`

### Permission Issues
- Ensure `/uploads` directory has correct permissions
- Check Docker volume mounts

### Role Not Working
- Verify user has `role='admin'` in database
- Check session contains role after login
- Clear browser cookies/session

## Migration from SQLite

If migrating existing SQLite data:

1. Export SQLite data:
```bash
sqlite3 unimak.db .dump > dump.sql
```

2. Convert SQLite dump to PostgreSQL format (manual editing required):
   - Remove SQLite-specific syntax
   - Convert `INTEGER PRIMARY KEY AUTOINCREMENT` to `SERIAL PRIMARY KEY`
   - Update `INSERT` statements if needed

3. Import to PostgreSQL:
```bash
docker-compose exec db psql -U postgres -d unimak -f /path/to/converted_dump.sql
```

4. Update user roles:
```sql
UPDATE users SET role = 'admin' WHERE username = 'your-admin-username';
```

## Production Considerations

1. **Change Default Passwords**: Update database passwords in production
2. **Set SECRET_KEY**: Use strong secret key in production
3. **SSL/TLS**: Configure HTTPS in production
4. **Backup Strategy**: Set up PostgreSQL backups
5. **Monitoring**: Add logging and monitoring
6. **Rate Limiting**: Consider adding rate limiting
7. **CSRF Protection**: Add Flask-WTF for CSRF tokens


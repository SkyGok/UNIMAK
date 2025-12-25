# Local Testing Guide

This guide will help you test the website locally before hosting.

## Option 1: Using Docker (Recommended - Easiest)

### Step 1: Create Environment File
Create a `.env` file in the `backend/` directory:

```bash
cd /home/gokhan/UNIMAK/WEB-4/backend
cat > .env << 'EOF'
DB_HOST=db
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=unimak
DB_PORT=5432
SECRET_KEY=dev-secret-key-change-in-production
UPLOADS_DIR=/uploads
FLASK_DEBUG=False
PORT=5000
EOF
```

### Step 2: Create uploads directory for Docker
```bash
mkdir -p uploads
```

### Step 3: Start Docker containers
```bash
docker-compose up -d --build
```

### Step 4: Wait for database to initialize
```bash
docker-compose logs -f db
```
Wait until you see "database system is ready to accept connections"

### Step 5: Create an admin user
```bash
docker-compose exec web python3
```

Then in Python:
```python
from db import Database
from werkzeug.security import generate_password_hash

db = Database()
password_hash = generate_password_hash('admin123')
db.execute(
    "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
    'admin', password_hash, 'admin'
)
exit()
```

### Step 6: Access the application
- **Main App**: http://localhost:5000/df/
- **Login**: http://localhost:5000/df/login (username: `admin`, password: `admin123`)
- **Admin Panel**: http://localhost:5000/df/admin

### Step 7: Stop containers when done
```bash
docker-compose down
```

---

## Option 2: Without Docker (Requires PostgreSQL)

### Step 1: Install PostgreSQL
```bash
# Arch Linux
sudo pacman -S postgresql
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Step 2: Create database and user
```bash
sudo -u postgres psql
```

In PostgreSQL:
```sql
CREATE DATABASE unimak;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE unimak TO postgres;
\q
```

### Step 3: Initialize database schema
```bash
cd /home/gokhan/UNIMAK/WEB-4/backend
sudo -u postgres psql -d unimak -f init_db.sql
```

### Step 4: Create .env file (for local PostgreSQL)
```bash
cat > .env << 'EOF'
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=unimak
DB_PORT=5432
SECRET_KEY=dev-secret-key-change-in-production
FLASK_DEBUG=True
PORT=5000
EOF
```

### Step 5: Activate virtual environment and install dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Step 6: Create admin user
```bash
python3
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
exit()
```

### Step 7: Run the application
```bash
python app.py
```

### Step 8: Access the application
- **Main App**: http://localhost:5000/df/
- **Login**: http://localhost:5000/df/login (username: `admin`, password: `admin123`)

---

## Troubleshooting

### Database connection errors
- Check if PostgreSQL is running: `systemctl status postgresql` (without Docker)
- Check Docker logs: `docker-compose logs db` (with Docker)
- Verify database credentials in `.env` file

### Permission errors
- Make sure uploads directory exists and is writable
- For Docker: `chmod 755 uploads`
- For local: The app will use `static/files/uploads` automatically

### Port already in use
- Change PORT in `.env` file
- Or stop the service using port 5000: `lsof -ti:5000 | xargs kill`

### Can't access admin panel
- Make sure you created a user with `role='admin'`
- Check session: logout and login again


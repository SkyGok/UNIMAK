# Fix for psycopg2-binary Installation Issue

## Problem
`psycopg2-binary` is trying to build from source because Python 3.13 wheels may not be available, requiring `pg_config`.

## Solution Options

### Option 1: Install PostgreSQL Development Libraries (Recommended)

**On Arch Linux:**
```bash
sudo pacman -S postgresql-libs
```

**On Ubuntu/Debian:**
```bash
sudo apt-get install libpq-dev
```

**On Fedora/RHEL:**
```bash
sudo dnf install postgresql-devel
```

Then install requirements:
```bash
cd backend
source venv/bin/activate  # or your venv path
pip install -r requirements.txt
```

### Option 2: Use Latest psycopg2-binary Version

Update `requirements.txt`:
```txt
psycopg2-binary>=2.9.9
```

Then:
```bash
pip install --upgrade pip
pip install psycopg2-binary --no-cache-dir
pip install -r requirements.txt
```

### Option 3: Use Docker (Easiest - No Local Installation Needed)

Since you're using Docker, you don't need to install psycopg2-binary locally:

```bash
cd backend
docker-compose up -d --build
```

The Docker container will handle all dependencies automatically.

### Option 4: Use psycopg (Version 3) - Modern Alternative

If psycopg2-binary continues to have issues, you can use the newer `psycopg` package:

Update `requirements.txt`:
```txt
psycopg[binary]>=3.1.0
```

Then update `db.py` to use psycopg3 syntax (different API, but more modern).

---

## Quick Fix for Your Current Issue

Since you're in a venv, try:

```bash
# Make sure you're in venv
source venv/bin/activate

# Install PostgreSQL dev libraries
sudo pacman -S postgresql-libs

# Then install requirements
pip install -r requirements.txt
```

Or simply use Docker - it handles everything automatically!



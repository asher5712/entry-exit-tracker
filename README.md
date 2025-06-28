# EntryExit Tracker

A Django 5.2 LTS web application for tracking entry and exit times of users (e.g., employees, visitors) via server-rendered pages (Django Template Language).

## Table of Contents

- [Features](#features)  
- [Tech Stack](#tech-stack)  
- [Prerequisites](#prerequisites)  
- [Installation](#installation)  
- [Configuration](#configuration)  
- [Database Migrations](#database-migrations)  
- [Running the Development Server](#running-the-development-server)  
- [URL Routes & Templates](#url-routes--templates)  
- [Usage](#usage)  
- [Running Tests](#running-tests)  
- [Deployment](#deployment)  
- [Contributing](#contributing)  
- [License](#license)  
- [Contact](#contact)  

## Features

- ▶️ User registration, login, logout (built-in auth)  
- ▶️ Manual “Entry” and “Exit” logging per user  
- ▶️ Dashboard with summary cards (today’s visits, average duration, etc.)  
- ▶️ Detailed log list with filters by user, date range, event type  
- ▶️ CSV export of filtered logs  
- ▶️ Server-rendered views using Django Template Language (DTL)  

## Tech Stack

- **Python:** 3.8+  
- **Django:** 5.2 LTS  
- **Database:** PostgreSQL (production) or SQLite (development)  
- **Templates:** Django Template Language, Bootstrap 5  
- **Front-end assets:** django-staticfiles  

## Prerequisites

- Python 3.8 or newer  
- pip (bundled with Python)  
- virtualenv (recommended)  
- PostgreSQL (for production deployments)  

## Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/yourusername/entryexit-tracker.git
   cd entryexit-tracker
   ```
2. **Create & activate a virtual environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate   # Windows: venv\Scripts\activate
    ```

3. **Install Python dependencies**
    ```bash
    pip install -r requirements.txt
    ```
   
## Configuration
1. **Copy the example environment file**
    ```bash
    cp .env.example .env
    ```

2. **Edit .env**
    ```dotenv
    SECRET_KEY=your_django_secret_key
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1
    DATABASE_NAME=your_database_name
    DATABASE_USER=your_databse_user
    DATABASE_PASSWORD=your_database_password
    DATABASE_HOST=localhost
    DATABASE_PORT=5432
    ```
   
3. **Settings**
   - Uses django-environ to load .env.
   - Static files served via STATIC_ROOT.

## Database Migrations
Apply migrations to create the database schema:
```bash
  python manage.py migrate
```

## Running the Development Server
```bash
  python manage.py runserver
```
Visit http://127.0.0.1:8000/ in your browser.

## Template Structure
```pgsql
templates/
├── entryexit/
│   ├── base.html
│   ├── delete_record.html
│   ├── edit_record.html
│   └── record_list.html
└── registration/
    ├── logged_out.html
    ├── login.html
    ├── password_change_done.html
    └── password_change_form.html
```
Forms use Django’s ModelForm; views are class-based (ListView, CreateView) or function-based for CSV export.

## Usage
1. **Create superuser**
    ```bash
    python manage.py createsuperuser
    ```
2. **Log in at `/accounts/login/`.**
3. **Dashboard shows today’s stats and buttons: “Log Entry” / “Log Exit.”**
4. **Log events by choosing a user and time (defaults to now).**
5. **View logs at `/logs/`; filter by user, date range, or event type.**
6. **Export logs to CSV via the “Export CSV” button on the list page.**

## Running Tests
Run Django’s test suite:
```bash
  python manage.py test
```

Optionally with coverage (if pytest and pytest-cov installed):
```bash
  pytest --cov=tracker
```

## Deployment
### Docker
1. Build & start
    ```bash
    docker-compose up --build -d
    ```
2. Migrate & collectstatic
    ```bash
    docker-compose exec web python manage.py migrate
    docker-compose exec web python manage.py collectstatic --noinput
    ```
3. Environment
   - Define .env for production settings.
   - Serve via Gunicorn + Nginx.

## VPS / Traditional
- Configure Gunicorn systemd service
- Use Nginx as reverse proxy + static files
- Enable HTTPS (e.g. Let's Encrypt)
- Set DEBUG=False and ALLOWED_HOSTS appropriately

## Contributing
1. Fork the repo
2. Create a branch: `git checkout -b feature/name`
3. Commit: `git commit -m "Add feature"`
4. Push: `git push origin feature/name`
5. Open a Pull Request

Please follow existing style, include tests for new features, and update documentation.

## License
Distributed under the MIT License. See [LICENSE](./LICENSE) for details.

## Contact
#### Your Name – Sher Ali
#### Project: [github.com/asher5712/entry-exit-tracker](https://github.com/asher5712/entry-exit-tracker)
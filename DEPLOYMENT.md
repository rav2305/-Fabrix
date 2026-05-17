# Fabrix Shop Manager Deployment Guide

## 1. Install Dependencies

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Configure Application Settings

Edit the constants at the top of `fabrix_shop_manager/config.py`:

- `SECRET_KEY`
- `DB_USERNAME`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `PUBLIC_BASE_URL`

The app builds the MySQL SQLAlchemy URI in code using those values.

## 3. Initialize and Run Migrations

```powershell
$env:FLASK_APP = "app.py"
flask db upgrade
```

If you need a new schema revision later:

```powershell
flask db migrate -m "describe your schema change"
flask db upgrade
```

## 4. Local Run

```powershell
python app.py
```

## 5. Render

- Create a Web Service
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn -c gunicorn.conf.py app:app`
- Update `fabrix_shop_manager/config.py` with your production MySQL values before deploy
- Run `flask db upgrade` once in a shell or as a pre-deploy step

## 6. Railway

- Add a Python service
- Add a MySQL service or external MySQL connection
- Update `fabrix_shop_manager/config.py` with the correct connection values
- Start command: `gunicorn -c gunicorn.conf.py app:app`
- Run `flask db upgrade`

## 7. PythonAnywhere

- Upload the project
- Create a virtual environment and install requirements
- Update `fabrix_shop_manager/config.py` with the server database values
- Point the WSGI file to `from wsgi import application`
- Run `flask db upgrade` from a Bash console

## 8. Concurrency Notes

- Stock writes and billing writes run inside database transactions
- Product rows are locked with `SELECT ... FOR UPDATE` during stock-sensitive operations
- Retries are enabled for transient deadlocks and lock wait timeouts
- Socket.IO broadcasts refresh events after successful commits only

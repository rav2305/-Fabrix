# Fabrix Shop Manager

Fabrix Shop Manager is a Flask-based shop management system for centralized inventory, billing, invoicing, dashboard reporting, and multi-device access.

## Current Stack

- Flask
- SQLAlchemy
- MySQL
- Flask-Migrate
- Flask-SocketIO
- HTML/CSS/Vanilla JS
- PWA support for mobile installation
- Desktop wrapper for PC usage

## Core Features

- Inventory management
- Billing and POS
- Invoice generation
- GST and discount calculations
- Excel inventory upload
- Dashboard and reports
- Real-time stock synchronization across devices

## Multi-Device Usage

The application is designed around one centralized backend and one shared MySQL database. Mobile, desktop, and browser clients all connect to the same backend, so stock updates and billing changes can appear live across devices.

## Run Locally

```powershell
py -3 -m pip install -r requirements.txt
flask --app wsgi db upgrade
py -3 app.py
```

## Build Desktop Wrapper

```powershell
.\build_desktop.ps1
```

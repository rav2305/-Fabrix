# Fabrix Shop Manager Handbook

This handbook captures what the project does, how it works, and the progress completed in the May 17, 2026 MySQL and real-time sync upgrade.

## What the Project Does

Fabrix Shop Manager is a centralized shop operations platform for fabric and garment retail. It supports:

- Inventory management with live stock quantities, purchase price, and selling price
- Billing and POS invoice generation
- GST, discount, subtotal, total, and profit calculations
- Invoice viewing, PDF export, and WhatsApp sharing
- Excel-based inventory bulk upload
- Dashboard reporting for daily sales and profit
- Multi-device access from mobile PWA, desktop wrapper, and browser clients

## How the Project Works Now

The application now follows a client-server architecture:

- One Flask backend serves all clients
- One MySQL database stores all shared business data
- Browser, desktop, and mobile clients use REST APIs for reads and writes
- Flask-SocketIO broadcasts stock, dashboard, and billing events to every connected client
- Frontend pages listen for socket events and refresh their data automatically without reloads

### Backend Structure

- `app.py`: runtime entrypoint using `socketio.run()`
- `fabrix_shop_manager/config.py`: in-code MySQL-only application settings
- `fabrix_shop_manager/extensions.py`: SQLAlchemy, Flask-Migrate, Flask-SocketIO setup
- `fabrix_shop_manager/models/`: products, invoices, invoice items
- `fabrix_shop_manager/services/`: inventory, billing, dashboard, reporting, sync logic
- `fabrix_shop_manager/blueprints/`: web pages and REST APIs
- `fabrix_shop_manager/sockets/events.py`: Socket.IO connection handlers
- `migrations/`: Alembic migration assets for future schema evolution

### Data Flow

1. A user updates stock, adds inventory, or creates a bill.
2. The request hits a Flask API endpoint.
3. A service layer runs the change inside a retry-safe database transaction.
4. MySQL commits the shared change centrally.
5. Flask-SocketIO emits refresh events to all connected devices.
6. Every dashboard, billing, and inventory screen refetches fresh data automatically.

## Progress Completed

### Completed Architecture Upgrade

- Replaced SQLite runtime usage with MySQL-only SQLAlchemy configuration
- Added Flask-Migrate and a migration-ready project layout
- Refactored the single-file Flask app into modular blueprints, services, models, and socket handlers
- Added production database pooling, `pool_pre_ping`, `pool_recycle`, and transaction retries
- Added REST APIs for inventory, billing, dashboard stats, and stock updates
- Added real-time synchronization with Flask-SocketIO and `eventlet`
- Updated the frontend to fetch through APIs and react to socket events without reloads
- Updated desktop wrapper to open the centralized deployment URL from shared in-code settings
- Added deployment support for Render, Railway, and PythonAnywhere

### Existing Business Features Preserved

- Invoice generation
- PDF download
- WhatsApp invoice sharing
- Excel uploads
- Dashboard reports
- Inventory search
- GST and discount calculations

## Current Deployment Model

- Mobile users open the hosted site or install it as a PWA shortcut
- Desktop users can open the hosted app in the browser or through `desktop_app.py`
- All clients hit the same Flask backend and the same MySQL database
- No client uses a local database file

## Next Operational Steps

1. Create the MySQL database and user.
2. Update the database and app constants in `fabrix_shop_manager/config.py`.
3. Install requirements.
4. Run Flask-Migrate upgrade commands.
5. Start the Socket.IO-enabled server locally or deploy it to a hosting platform.

Document updated on May 17, 2026 after the centralized multi-device sync migration.

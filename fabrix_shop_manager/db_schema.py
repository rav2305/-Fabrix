"""Database schema initialization."""
from sqlalchemy import text, inspect
from .extensions import db


def init_schema():
    """Create all required tables if they don't exist."""
    try:
        # Check if tables already exist
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if 'products' in existing_tables and 'invoices' in existing_tables and 'invoice_items' in existing_tables:
            print("✓ All database tables already exist")
            return
        
        with db.engine.begin() as connection:
            # 1. Create the Products Table
            if 'products' not in existing_tables:
                connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS products (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(120) NOT NULL,
                        price NUMERIC(10, 2) NOT NULL,
                        purchase_price NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
                        stock INTEGER NOT NULL DEFAULT 0,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """))
                
                # Index for fast product searches
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_products_name ON products(name)
                """))
                print("✓ Created products table")
            
            # 2. Create the Invoices Table
            if 'invoices' not in existing_tables:
                connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS invoices (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        invoice_number VARCHAR(64) UNIQUE NOT NULL,
                        date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        customer_name VARCHAR(120) NOT NULL,
                        customer_phone VARCHAR(32) DEFAULT NULL,
                        payment_mode VARCHAR(50) DEFAULT NULL,
                        subtotal NUMERIC(12, 2) NOT NULL,
                        discount_percent NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
                        discount_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
                        gst_percent NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
                        gst_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
                        total_amount NUMERIC(12, 2) NOT NULL,
                        total_profit NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """))
                
                # Indexes for fast invoice retrieval
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_invoices_invoice_number ON invoices(invoice_number)
                """))
                
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_invoices_date ON invoices(date)
                """))
                print("✓ Created invoices table")
            
            # 3. Create the Invoice Items Table
            if 'invoice_items' not in existing_tables:
                connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS invoice_items (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        invoice_id INTEGER NOT NULL,
                        product_id INTEGER DEFAULT NULL,
                        product_name VARCHAR(120) NOT NULL,
                        quantity INTEGER NOT NULL,
                        price NUMERIC(10, 2) NOT NULL,
                        purchase_price NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
                        total NUMERIC(12, 2) NOT NULL,
                        profit NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        CONSTRAINT fk_invoice FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
                        CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
                    )
                """))
                print("✓ Created invoice_items table")
            
            print("✓ All database tables created successfully")
    except Exception as e:
        print(f"⚠ Warning: Could not initialize schema: {e}")
        import traceback
        traceback.print_exc()

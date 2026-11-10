"""
Database Manager Service
Handles storage, listing, validation, and sample seeding of SQLite databases.
"""

import os
import shutil
import uuid
import sqlite3
from typing import List, Dict, Any, Optional
from backend.database.schema_extractor import DatabaseSchemaExtractor


class DatabaseManager:
    """Manages SQLite database storage, safe uploads, and metadata retrieval."""

    def __init__(self, storage_dir: str = "data/databases"):
        self.storage_dir = os.path.abspath(storage_dir)
        os.makedirs(self.storage_dir, exist_ok=True)
        self._ensure_sample_databases()

    def list_databases(self) -> List[Dict[str, Any]]:
        """List all valid SQLite databases in the storage directory."""
        db_list = []
        for file in os.listdir(self.storage_dir):
            if file.endswith((".db", ".sqlite", ".sqlite3")):
                file_path = os.path.join(self.storage_dir, file)
                size_bytes = os.path.getsize(file_path)
                try:
                    extractor = DatabaseSchemaExtractor(file_path)
                    tables = extractor.get_tables()
                    db_list.append({
                        "id": file,
                        "name": file,
                        "path": file_path,
                        "size_bytes": size_bytes,
                        "table_count": len(tables),
                        "tables": tables
                    })
                except Exception as e:
                    # Not a valid sqlite file or corrupted
                    continue
        return sorted(db_list, key=lambda x: x["name"])

    def get_database_path(self, database_id: str) -> str:
        """Resolve database path safely preventing directory traversal."""
        safe_name = os.path.basename(database_id)
        path = os.path.join(self.storage_dir, safe_name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Database '{database_id}' not found.")
        return path

    def save_uploaded_file(self, filename: str, file_bytes: bytes) -> Dict[str, Any]:
        """Validate and securely save an uploaded SQLite database."""
        # Validate extension
        clean_filename = os.path.basename(filename)
        ext = os.path.splitext(clean_filename)[1].lower()
        if ext not in [".db", ".sqlite", ".sqlite3"]:
            raise ValueError(f"Invalid file extension '{ext}'. Only .db, .sqlite, .sqlite3 allowed.")

        # Max size check (e.g. 100 MB)
        if len(file_bytes) > 100 * 1024 * 1024:
            raise ValueError("Database file exceeds maximum allowed size of 100 MB.")

        # Create unique filename if conflict exists
        target_path = os.path.join(self.storage_dir, clean_filename)
        if os.path.exists(target_path):
            base, ext = os.path.splitext(clean_filename)
            unique_name = f"{base}_{uuid.uuid4().hex[:6]}{ext}"
            target_path = os.path.join(self.storage_dir, unique_name)
            clean_filename = unique_name

        with open(target_path, "wb") as f:
            f.write(file_bytes)

        # Validate that it is indeed a readable SQLite database
        try:
            extractor = DatabaseSchemaExtractor(target_path)
            tables = extractor.get_tables()
        except Exception as e:
            # Clean up invalid file
            if os.path.exists(target_path):
                os.remove(target_path)
            raise ValueError(f"Uploaded file is not a valid SQLite database: {str(e)}")

        return {
            "id": clean_filename,
            "name": clean_filename,
            "path": target_path,
            "size_bytes": os.path.getsize(target_path),
            "table_count": len(tables),
            "tables": tables
        }

    def _ensure_sample_databases(self):
        """Seed rich realistic sample databases across varied domain schemas."""
        uni_db = os.path.join(self.storage_dir, "university.db")
        if not os.path.exists(uni_db):
            self._create_university_db(uni_db)

        ecom_db = os.path.join(self.storage_dir, "ecommerce.db")
        if not os.path.exists(ecom_db):
            self._create_ecommerce_db(ecom_db)

        hosp_db = os.path.join(self.storage_dir, "hospital_management.db")
        if not os.path.exists(hosp_db):
            from scripts.create_multi_table_databases import create_hospital_db
            create_hospital_db()

        bank_db = os.path.join(self.storage_dir, "fintech_banking.db")
        if not os.path.exists(bank_db):
            from scripts.create_multi_table_databases import create_fintech_db
            create_fintech_db()

        sc_db = os.path.join(self.storage_dir, "supply_chain.db")
        if not os.path.exists(sc_db):
            from scripts.create_multi_table_databases import create_supply_chain_db
            create_supply_chain_db()

        air_db = os.path.join(self.storage_dir, "airline_flight_ops.db")
        if not os.path.exists(air_db):
            from scripts.create_multi_table_databases import create_airline_db
            create_airline_db()

        hotel_db = os.path.join(self.storage_dir, "hotel_resort.db")
        if not os.path.exists(hotel_db):
            from scripts.create_multi_table_databases import create_hotel_resort_db
            create_hotel_resort_db()

        stream_db = os.path.join(self.storage_dir, "streaming_entertainment.db")
        if not os.path.exists(stream_db):
            from scripts.create_more_datasets import create_streaming_db
            create_streaming_db()

        ride_db = os.path.join(self.storage_dir, "rideshare_mobility.db")
        if not os.path.exists(ride_db):
            from scripts.create_more_datasets import create_rideshare_db
            create_rideshare_db()

        re_db = os.path.join(self.storage_dir, "real_estate_property.db")
        if not os.path.exists(re_db):
            from scripts.create_more_datasets import create_real_estate_db
            create_real_estate_db()

        tel_db = os.path.join(self.storage_dir, "telecom_network_ops.db")
        if not os.path.exists(tel_db):
            from scripts.create_more_datasets import create_telecom_db
            create_telecom_db()

        energy_db = os.path.join(self.storage_dir, "smart_energy_grid.db")
        if not os.path.exists(energy_db):
            from scripts.create_more_datasets import create_smart_energy_db
            create_smart_energy_db()

        crypto_db = os.path.join(self.storage_dir, "crypto_exchange_market.db")
        if not os.path.exists(crypto_db):
            from scripts.create_more_datasets import create_crypto_market_db
            create_crypto_market_db()

        git_db = os.path.join(self.storage_dir, "software_dev_git_tracker.db")
        if not os.path.exists(git_db):
            from scripts.create_more_datasets import create_git_tracker_db
            create_git_tracker_db()

        esports_db = os.path.join(self.storage_dir, "gaming_esports_league.db")
        if not os.path.exists(esports_db):
            from scripts.create_even_more_datasets import create_esports_db
            create_esports_db()

        log_db = os.path.join(self.storage_dir, "logistics_warehouse_inventory.db")
        if not os.path.exists(log_db):
            from scripts.create_even_more_datasets import create_logistics_warehouse_db
            create_logistics_warehouse_db()

        clin_db = os.path.join(self.storage_dir, "healthcare_clinical_trials.db")
        if not os.path.exists(clin_db):
            from scripts.create_even_more_datasets import create_clinical_trials_db
            create_clinical_trials_db()

        ins_db = os.path.join(self.storage_dir, "fintech_insurance_claims.db")
        if not os.path.exists(ins_db):
            from scripts.create_even_more_datasets import create_insurance_claims_db
            create_insurance_claims_db()

        cloud_db = os.path.join(self.storage_dir, "cloud_devops_infrastructure.db")
        if not os.path.exists(cloud_db):
            from scripts.create_even_more_datasets import create_cloud_devops_db
            create_cloud_devops_db()

        food_db = os.path.join(self.storage_dir, "restaurant_food_delivery.db")
        if not os.path.exists(food_db):
            from scripts.create_even_more_datasets import create_food_delivery_db
            create_food_delivery_db()

        transit_db = os.path.join(self.storage_dir, "smart_city_transportation.db")
        if not os.path.exists(transit_db):
            from scripts.create_even_more_datasets import create_smart_city_transit_db
            create_smart_city_transit_db()

        music_db = os.path.join(self.storage_dir, "digital_music_streaming.db")
        if not os.path.exists(music_db):
            from scripts.create_even_more_datasets import create_digital_music_db
            create_digital_music_db()

    def _create_university_db(self, path: str):
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        cur.executescript("""
            CREATE TABLE departments (
                department_id INTEGER PRIMARY KEY,
                department_name TEXT NOT NULL,
                building TEXT NOT NULL,
                budget REAL NOT NULL
            );

            CREATE TABLE instructors (
                instructor_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                department_id INTEGER NOT NULL,
                salary REAL NOT NULL,
                FOREIGN KEY (department_id) REFERENCES departments(department_id)
            );

            CREATE TABLE students (
                student_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                department_id INTEGER NOT NULL,
                gpa REAL NOT NULL,
                FOREIGN KEY (department_id) REFERENCES departments(department_id)
            );

            CREATE TABLE courses (
                course_id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                department_id INTEGER NOT NULL,
                credits INTEGER NOT NULL,
                FOREIGN KEY (department_id) REFERENCES departments(department_id)
            );

            CREATE TABLE enrollments (
                enrollment_id INTEGER PRIMARY KEY,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                grade TEXT,
                score INTEGER NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (course_id) REFERENCES courses(course_id)
            );

            INSERT INTO departments VALUES
                (1, 'Computer Science', 'Turing Hall', 1200000.0),
                (2, 'Mathematics', 'Euler Hall', 850000.0),
                (3, 'Physics', 'Newton Hall', 950000.0),
                (4, 'Chemistry', 'Curie Hall', 750000.0);

            INSERT INTO instructors VALUES
                (101, 'Dr. Alan Smith', 1, 95000.0),
                (102, 'Dr. Sarah Connor', 1, 92000.0),
                (103, 'Dr. John Nash', 2, 88000.0),
                (104, 'Dr. Richard Feynman', 3, 105000.0),
                (105, 'Dr. Marie Curie', 4, 98000.0);

            INSERT INTO students VALUES
                (1, 'Alice Johnson', 21, 1, 3.85),
                (2, 'Bob Williams', 22, 1, 3.42),
                (3, 'Charlie Brown', 20, 2, 3.91),
                (4, 'Diana Prince', 23, 3, 3.75),
                (5, 'Evan Wright', 21, 2, 3.10),
                (6, 'Fiona Gallagher', 22, 4, 3.65),
                (7, 'George Clark', 19, 1, 3.50),
                (8, 'Hannah Abbott', 20, 3, 3.80);

            INSERT INTO courses VALUES
                (201, 'Database Systems', 1, 4),
                (202, 'Algorithms', 1, 4),
                (203, 'Linear Algebra', 2, 3),
                (204, 'Quantum Mechanics', 3, 4),
                (205, 'Organic Chemistry', 4, 4);

            INSERT INTO enrollments VALUES
                (1, 1, 201, 'A', 92),
                (2, 1, 202, 'A', 95),
                (3, 2, 201, 'B', 84),
                (4, 3, 203, 'A', 98),
                (5, 4, 204, 'A', 91),
                (6, 5, 203, 'C', 72),
                (7, 6, 205, 'B', 88),
                (8, 7, 201, 'B', 86),
                (9, 8, 204, 'A', 94),
                (10, 2, 202, 'B', 81);
        """)
        conn.commit()
        conn.close()

    def _create_ecommerce_db(self, path: str):
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        cur.executescript("""
            CREATE TABLE customers (
                customer_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                city TEXT NOT NULL,
                country TEXT NOT NULL
            );

            CREATE TABLE categories (
                category_id INTEGER PRIMARY KEY,
                category_name TEXT NOT NULL
            );

            CREATE TABLE products (
                product_id INTEGER PRIMARY KEY,
                product_name TEXT NOT NULL,
                category_id INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                stock_quantity INTEGER NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories(category_id)
            );

            CREATE TABLE orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                order_date TEXT NOT NULL,
                total_amount REAL NOT NULL,
                status TEXT COLLATE NOCASE NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            );

            CREATE TABLE order_items (
                order_item_id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            );

            INSERT INTO categories VALUES
                (1, 'Electronics'),
                (2, 'Books'),
                (3, 'Home & Kitchen'),
                (4, 'Apparel');

            INSERT INTO customers VALUES
                (1, 'Michael Scott', 'michael@dunder.com', 'Scranton', 'USA'),
                (2, 'Jim Halpert', 'jim@dunder.com', 'Philadelphia', 'USA'),
                (3, 'Pam Beesly', 'pam@dunder.com', 'Scranton', 'USA'),
                (4, 'Dwight Schrute', 'dwight@dunder.com', 'Scranton', 'USA'),
                (5, 'Ryan Howard', 'ryan@ny.com', 'New York', 'USA');

            INSERT INTO products VALUES
                (101, 'Noise Cancelling Headphones', 1, 199.99, 45),
                (102, 'Mechanical Keyboard', 1, 129.50, 80),
                (103, 'AI Programming in Python', 2, 49.99, 120),
                (104, 'Espresso Maker', 3, 249.00, 25),
                (105, 'Cotton T-Shirt', 4, 19.99, 200),
                (106, 'Ergonomic Desk Chair', 3, 319.00, 15);

            INSERT INTO orders VALUES
                (1001, 1, '2026-01-15', 399.98, 'Delivered'),
                (1002, 2, '2026-02-10', 129.50, 'Delivered'),
                (1003, 3, '2026-02-14', 49.99, 'Shipped'),
                (1004, 4, '2026-02-20', 568.00, 'Processing'),
                (1005, 1, '2026-03-01', 249.00, 'Delivered');

            INSERT INTO order_items VALUES
                (1, 1001, 101, 2, 199.99),
                (2, 1002, 102, 1, 129.50),
                (3, 1003, 103, 1, 49.99),
                (4, 1004, 104, 1, 249.00),
                (5, 1004, 106, 1, 319.00),
                (6, 1005, 104, 1, 249.00);
        """)
        conn.commit()
        conn.close()


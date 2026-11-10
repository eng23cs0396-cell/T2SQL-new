"""
Multi-Table Database Generator for Text-to-SQL Testing
Creates 5 realistic, relational SQLite databases with varying table counts:
1. hospital_management.db  (4 tables)
2. fintech_banking.db       (4 tables)
3. supply_chain.db          (5 tables)
4. airline_flight_ops.db    (6 tables)
5. hotel_resort.db          (7 tables)

All databases include:
- Strict SQLite schema with PRIMARY KEYs, FOREIGN KEYs, NOT NULL constraints.
- Realistically populated rows with diverse values (dates, numerics, strings, nulls, codes).
- Support for complex SQL querying (multi-table JOINs, GROUP BY HAVING, subqueries, CTEs, window aggregations).
"""

import os
import sqlite3

DATA_DIR = os.path.abspath("data/databases")
os.makedirs(DATA_DIR, exist_ok=True)


def create_hospital_db():
    """Database 1: 4 tables (departments, doctors, patients, appointments)"""
    path = os.path.join(DATA_DIR, "hospital_management.db")
    if os.path.exists(path):
        os.remove(path)
    
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE departments (
            dept_id INTEGER PRIMARY KEY,
            dept_name TEXT NOT NULL,
            head_physician TEXT NOT NULL,
            budget REAL NOT NULL,
            building_wing TEXT NOT NULL
        );

        CREATE TABLE doctors (
            doctor_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            dept_id INTEGER NOT NULL,
            specialty TEXT NOT NULL,
            hire_date TEXT NOT NULL,
            salary REAL NOT NULL,
            years_experience INTEGER NOT NULL,
            FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        );

        CREATE TABLE patients (
            patient_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            blood_type TEXT NOT NULL,
            city TEXT NOT NULL,
            insurance_provider TEXT NOT NULL
        );

        CREATE TABLE appointments (
            appointment_id INTEGER PRIMARY KEY,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT COLLATE NOCASE NOT NULL,
            billing_amount REAL NOT NULL,
            follow_up_required INTEGER NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
        );

        -- Seed Departments
        INSERT INTO departments VALUES
            (1, 'Cardiology', 'Dr. Marcus Vance', 1500000.0, 'East Wing'),
            (2, 'Neurology', 'Dr. Helena Ray', 1800000.0, 'North Wing'),
            (3, 'Pediatrics', 'Dr. Chloe Adams', 1200000.0, 'West Wing'),
            (4, 'Orthopedics', 'Dr. Derek Stone', 1400000.0, 'South Wing'),
            (5, 'Oncology', 'Dr. Samuel Green', 2100000.0, 'Central Tower');

        -- Seed Doctors
        INSERT INTO doctors VALUES
            (101, 'Marcus', 'Vance', 1, 'Invasive Cardiology', '2015-03-12', 260000.0, 18),
            (102, 'Emily', 'Chen', 1, 'Electrophysiology', '2019-07-01', 210000.0, 9),
            (103, 'Helena', 'Ray', 2, 'Neurosurgery', '2012-11-15', 320000.0, 22),
            (104, 'Lucas', 'Perez', 2, 'Stroke Neurology', '2020-01-10', 195000.0, 7),
            (105, 'Chloe', 'Adams', 3, 'Pediatric Cardiology', '2016-08-20', 185000.0, 14),
            (106, 'Benjamin', 'Foster', 3, 'General Pediatrics', '2021-04-05', 160000.0, 5),
            (107, 'Derek', 'Stone', 4, 'Spine Surgery', '2014-06-30', 290000.0, 19),
            (108, 'Jessica', 'Miller', 4, 'Sports Medicine', '2018-09-15', 205000.0, 10),
            (109, 'Samuel', 'Green', 5, 'Radiation Oncology', '2011-02-18', 310000.0, 24),
            (110, 'Aria', 'Novak', 5, 'Hematology Oncology', '2022-03-01', 190000.0, 6);

        -- Seed Patients
        INSERT INTO patients VALUES
            (1, 'Arthur', 'Pendelton', 64, 'M', 'O+', 'Chicago', 'BlueCross'),
            (2, 'Grace', 'Hopper', 42, 'F', 'A-', 'Evanston', 'Aetna'),
            (3, 'Victor', 'Hugo', 71, 'M', 'B+', 'Naperville', 'Medicare'),
            (4, 'Maya', 'Angelou', 58, 'F', 'AB+', 'Chicago', 'UnitedHealth'),
            (5, 'Leo', 'Tolstoy', 82, 'M', 'O-', 'Oak Park', 'Medicare'),
            (6, 'Ada', 'Lovelace', 31, 'F', 'A+', 'Chicago', 'BlueCross'),
            (7, 'Isaac', 'Newton', 49, 'M', 'B-', 'Aurora', 'Cigna'),
            (8, 'Marie', 'Curie', 67, 'F', 'AB-', 'Chicago', 'Aetna'),
            (9, 'Charles', 'Darwin', 55, 'M', 'O+', 'Schaumburg', 'UnitedHealth'),
            (10, 'Rosalind', 'Franklin', 39, 'F', 'A-', 'Chicago', 'BlueCross'),
            (11, 'Nikola', 'Tesla', 52, 'M', 'B+', 'Joliet', 'Humana'),
            (12, 'Florence', 'Nightingale', 45, 'F', 'O+', 'Chicago', 'Cigna'),
            (13, 'Albert', 'Einstein', 76, 'M', 'A+', 'Evanston', 'Medicare'),
            (14, 'Jane', 'Austen', 28, 'F', 'B-', 'Naperville', 'UnitedHealth'),
            (15, 'Ernest', 'Hemingway', 61, 'M', 'O-', 'Chicago', 'BlueCross');

        -- Seed Appointments
        INSERT INTO appointments VALUES
            (1001, 1, 101, '2026-01-10', 'Chest Pain Follow-up', 'Completed', 450.0, 1),
            (1002, 2, 103, '2026-01-12', 'Persistent Migraine Consultation', 'Completed', 600.0, 0),
            (1003, 3, 107, '2026-01-15', 'Knee Joint Replacement Evaluation', 'Completed', 850.0, 1),
            (1004, 4, 109, '2026-01-18', 'Biopsy Review', 'Completed', 1200.0, 1),
            (1005, 5, 102, '2026-01-22', 'Arrhythmia Monitoring', 'Completed', 550.0, 1),
            (1006, 6, 105, '2026-02-01', 'Congenital Heart Screening', 'Completed', 400.0, 0),
            (1007, 7, 108, '2026-02-05', 'Rotator Cuff Tear Exam', 'Completed', 350.0, 1),
            (1008, 8, 110, '2026-02-09', 'Anemia Workup', 'Completed', 750.0, 1),
            (1009, 9, 104, '2026-02-14', 'Post-Stroke Rehabilitation Check', 'Completed', 500.0, 0),
            (1010, 10, 101, '2026-02-18', 'Coronary Angiography Planning', 'Completed', 950.0, 1),
            (1011, 11, 103, '2026-02-23', 'Lumbar Spine MRI Follow-up', 'Completed', 650.0, 0),
            (1012, 12, 106, '2026-03-02', 'Asthma Control Review', 'Completed', 250.0, 0),
            (1013, 13, 107, '2026-03-08', 'Hip Arthroscopy Consultation', 'Completed', 800.0, 1),
            (1014, 14, 108, '2026-03-15', 'Ankle Sprain Treatment', 'Completed', 300.0, 0),
            (1015, 15, 109, '2026-03-20', 'Chemotherapy Cycle 2', 'Completed', 2200.0, 1),
            (1016, 1, 102, '2026-04-02', 'Pacemaker Check', 'Scheduled', 400.0, 0),
            (1017, 3, 108, '2026-04-05', 'Physical Therapy Assessment', 'Scheduled', 300.0, 0),
            (1018, 5, 101, '2026-04-10', 'Echocardiogram Review', 'Scheduled', 650.0, 1),
            (1019, 7, 104, '2026-04-12', 'Neuropathy Treatment', 'Cancelled', 0.0, 0),
            (1020, 9, 110, '2026-04-15', 'Bone Marrow Biopsy Follow-up', 'Scheduled', 1100.0, 1);
    """)
    conn.commit()
    conn.close()
    print("[CREATED] hospital_management.db (4 tables)")


def create_fintech_db():
    """Database 2: 4 tables (branches, customers, accounts, transactions)"""
    path = os.path.join(DATA_DIR, "fintech_banking.db")
    if os.path.exists(path):
        os.remove(path)

    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE branches (
            branch_id INTEGER PRIMARY KEY,
            branch_name TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            assets REAL NOT NULL,
            manager_name TEXT NOT NULL
        );

        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            city TEXT NOT NULL,
            credit_score INTEGER NOT NULL,
            monthly_income REAL NOT NULL,
            joined_date TEXT NOT NULL
        );

        CREATE TABLE accounts (
            account_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            branch_id INTEGER NOT NULL,
            account_type TEXT COLLATE NOCASE NOT NULL,
            balance REAL NOT NULL,
            interest_rate REAL NOT NULL,
            status TEXT COLLATE NOCASE NOT NULL,
            opened_date TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
        );

        CREATE TABLE transactions (
            transaction_id INTEGER PRIMARY KEY,
            account_id INTEGER NOT NULL,
            txn_type TEXT NOT NULL,
            amount REAL NOT NULL,
            txn_date TEXT NOT NULL,
            merchant TEXT,
            status TEXT NOT NULL,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id)
        );

        -- Seed Branches
        INSERT INTO branches VALUES
            (1, 'Downtown Financial Center', 'New York', 'NY', 850000000.0, 'Evelyn Reed'),
            (2, 'Silicon Valley Tech Branch', 'San Francisco', 'CA', 620000000.0, 'David Kim'),
            (3, 'Midwest Commercial Hub', 'Chicago', 'IL', 430000000.0, 'Sarah Jenkins'),
            (4, 'Sunbelt Metro Branch', 'Austin', 'TX', 310000000.0, 'Carlos Ramirez');

        -- Seed Customers
        INSERT INTO customers VALUES
            (101, 'Alexander', 'Hamilton', 'alex@nyfinance.com', 'New York', 785, 14500.0, '2021-01-15'),
            (102, 'Beatrix', 'Potter', 'beatrix@books.org', 'San Francisco', 740, 9200.0, '2022-03-22'),
            (103, 'Cornelius', 'Vanderbilt', 'cornelius@steam.com', 'New York', 820, 28000.0, '2020-05-10'),
            (104, 'Daphne', 'Bridgerton', 'daphne@mayfair.co', 'Chicago', 690, 7100.0, '2023-08-01'),
            (105, 'Edward', 'Snow', 'ed@tundra.net', 'Austin', 620, 5400.0, '2024-02-18'),
            (106, 'Fatima', 'Al-Mansoor', 'fatima@desert.ae', 'San Francisco', 805, 19000.0, '2021-11-05'),
            (107, 'Gregory', 'House', 'house@diagnostics.edu', 'New York', 710, 16000.0, '2022-09-14'),
            (108, 'Helena', 'Troy', 'helena@spartan.gr', 'Chicago', 760, 11500.0, '2023-01-20'),
            (109, 'Ivan', 'Petrov', 'ivan@siberia.ru', 'Austin', 645, 6200.0, '2023-10-11'),
            (110, 'Julia', 'Child', 'julia@culinary.com', 'San Francisco', 795, 13800.0, '2021-06-30');

        -- Seed Accounts
        INSERT INTO accounts VALUES
            (2001, 101, 1, 'Checking', 34500.0, 0.01, 'Active', '2021-01-15'),
            (2002, 101, 1, 'Investment', 185000.0, 0.045, 'Active', '2021-03-10'),
            (2003, 102, 2, 'Checking', 12800.0, 0.01, 'Active', '2022-03-22'),
            (2004, 102, 2, 'Savings', 45000.0, 0.035, 'Active', '2022-04-01'),
            (2005, 103, 1, 'Checking', 92000.0, 0.01, 'Active', '2020-05-10'),
            (2006, 103, 1, 'Investment', 850000.0, 0.05, 'Active', '2020-06-01'),
            (2007, 104, 3, 'Checking', 4800.0, 0.01, 'Active', '2023-08-01'),
            (2008, 105, 4, 'Checking', 2100.0, 0.01, 'Active', '2024-02-18'),
            (2009, 106, 2, 'Checking', 54000.0, 0.01, 'Active', '2021-11-05'),
            (2010, 106, 2, 'Investment', 310000.0, 0.048, 'Active', '2021-12-15'),
            (2011, 107, 1, 'Checking', 18900.0, 0.01, 'Active', '2022-09-14'),
            (2012, 107, 1, 'Savings', 62000.0, 0.038, 'Active', '2022-10-01'),
            (2013, 108, 3, 'Checking', 22500.0, 0.01, 'Active', '2023-01-20'),
            (2014, 108, 3, 'Savings', 78000.0, 0.04, 'Active', '2023-02-15'),
            (2015, 109, 4, 'Checking', 6500.0, 0.01, 'Active', '2023-10-11'),
            (2016, 110, 2, 'Checking', 28400.0, 0.01, 'Active', '2021-06-30'),
            (2017, 110, 2, 'Savings', 95000.0, 0.042, 'Active', '2021-07-20');

        -- Seed Transactions
        INSERT INTO transactions VALUES
            (5001, 2001, 'Debit', 2500.0, '2026-01-05', 'Equinox Fitness', 'Completed'),
            (5002, 2001, 'Credit', 14500.0, '2026-01-15', 'Payroll Direct Deposit', 'Completed'),
            (5003, 2002, 'Credit', 4200.0, '2026-01-20', 'Dividend Payout', 'Completed'),
            (5004, 2003, 'Debit', 180.50, '2026-01-22', 'Whole Foods', 'Completed'),
            (5005, 2003, 'Debit', 1250.0, '2026-02-01', 'Apartment Rent', 'Completed'),
            (5006, 2005, 'Debit', 15000.0, '2026-02-03', 'Tesla Supercharger & Service', 'Completed'),
            (5007, 2006, 'Credit', 18500.0, '2026-02-10', 'Capital Gains Distribution', 'Completed'),
            (5008, 2007, 'Debit', 85.00, '2026-02-12', 'Target', 'Completed'),
            (5009, 2008, 'Debit', 450.0, '2026-02-15', 'Geico Insurance', 'Completed'),
            (5010, 2009, 'Credit', 19000.0, '2026-02-28', 'Consulting Retainer', 'Completed'),
            (5011, 2010, 'Debit', 50000.0, '2026-03-01', 'Venture Syndicate Transfer', 'Completed'),
            (5012, 2011, 'Debit', 340.0, '2026-03-05', 'Barnes & Noble Books', 'Completed'),
            (5013, 2012, 'Credit', 2300.0, '2026-03-10', 'Interest Credit', 'Completed'),
            (5014, 2013, 'Debit', 1850.0, '2026-03-15', 'Delta Airlines', 'Completed'),
            (5015, 2014, 'Credit', 3120.0, '2026-03-20', 'Bonus Deposit', 'Completed'),
            (5016, 2016, 'Debit', 120.0, '2026-03-25', 'Trader Joes', 'Completed'),
            (5017, 2017, 'Credit', 4000.0, '2026-03-28', 'Quarterly Royalties', 'Completed'),
            (5018, 2001, 'Debit', 3100.0, '2026-04-01', 'Manhattan Co-op Dues', 'Completed'),
            (5019, 2004, 'Debit', 2500.0, '2026-04-03', 'Tuition Fee Transfer', 'Completed'),
            (5020, 2009, 'Debit', 1200.0, '2026-04-05', 'Apple Store Online', 'Completed');
    """)
    conn.commit()
    conn.close()
    print("[CREATED] fintech_banking.db (4 tables)")


def create_supply_chain_db():
    """Database 3: 5 tables (suppliers, warehouses, products, inventory, purchase_orders)"""
    path = os.path.join(DATA_DIR, "supply_chain.db")
    if os.path.exists(path):
        os.remove(path)

    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE suppliers (
            supplier_id INTEGER PRIMARY KEY,
            company_name TEXT NOT NULL,
            contact_name TEXT NOT NULL,
            country TEXT NOT NULL,
            rating REAL NOT NULL,
            payment_terms TEXT NOT NULL
        );

        CREATE TABLE warehouses (
            warehouse_id INTEGER PRIMARY KEY,
            warehouse_name TEXT NOT NULL,
            city TEXT NOT NULL,
            country TEXT NOT NULL,
            capacity_sqft INTEGER NOT NULL,
            operating_cost_monthly REAL NOT NULL
        );

        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            unit_cost REAL NOT NULL,
            unit_price REAL NOT NULL,
            supplier_id INTEGER NOT NULL,
            lead_time_days INTEGER NOT NULL,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
        );

        CREATE TABLE inventory (
            inventory_id INTEGER PRIMARY KEY,
            warehouse_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity_on_hand INTEGER NOT NULL,
            reorder_level INTEGER NOT NULL,
            last_restocked_date TEXT NOT NULL,
            FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );

        CREATE TABLE purchase_orders (
            po_id INTEGER PRIMARY KEY,
            supplier_id INTEGER NOT NULL,
            warehouse_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            order_date TEXT NOT NULL,
            delivery_status TEXT NOT NULL,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
            FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );

        -- Seed Suppliers
        INSERT INTO suppliers VALUES
            (1, 'Precision Optics GmbH', 'Klaus Weber', 'Germany', 4.8, 'Net 30'),
            (2, 'Shenzhen Micro Devices', 'Wei Zhang', 'China', 4.5, 'Net 60'),
            (3, 'Kyoto Sensor Corp', 'Kenji Sato', 'Japan', 4.9, 'Net 30'),
            (4, 'Nordic Industrial Materials', 'Astrid Lind', 'Sweden', 4.6, 'Net 45'),
            (5, 'Apex Polymer Solutions', 'Robert Taylor', 'USA', 4.3, 'Net 30'),
            (6, 'Bengal Semiconductor Ltd', 'Priya Sharma', 'India', 4.4, 'Net 60');

        -- Seed Warehouses
        INSERT INTO warehouses VALUES
            (10, 'Rotterdam Euro Hub', 'Rotterdam', 'Netherlands', 120000, 85000.0),
            (20, 'Chicago Logistics Terminal', 'Chicago', 'USA', 250000, 140000.0),
            (30, 'Singapore Gateway Depot', 'Singapore', 'Singapore', 180000, 110000.0),
            (40, 'Tokyo Central Facility', 'Tokyo', 'Japan', 95000, 75000.0);

        -- Seed Products
        INSERT INTO products VALUES
            (101, 'Industrial Laser Sensor', 'Sensors', 120.0, 240.0, 1, 14),
            (102, 'Microcontroller Unit MCU-8', 'Semiconductors', 15.0, 38.0, 2, 21),
            (103, 'High-Temp Thermal Probe', 'Sensors', 45.0, 95.0, 3, 10),
            (104, 'Titanium Alloy Fastener Kit', 'Hardware', 85.0, 160.0, 4, 30),
            (105, 'Conductive Polymer Sheet', 'Polymers', 30.0, 70.0, 5, 18),
            (106, 'FPGA Logic Core Processor', 'Semiconductors', 220.0, 480.0, 6, 25),
            (107, 'Optical Fiber Cable 100m', 'Networking', 60.0, 130.0, 1, 12),
            (108, 'Precision Pressure Transducer', 'Sensors', 140.0, 290.0, 3, 15),
            (109, 'Surface Mount Resistor Array', 'Components', 2.5, 8.0, 2, 7),
            (110, 'Heat Dissipation Heat Sink', 'Hardware', 18.0, 42.0, 4, 14);

        -- Seed Inventory
        INSERT INTO inventory VALUES
            (1, 10, 101, 450, 100, '2026-01-10'),
            (2, 10, 102, 3200, 800, '2026-01-15'),
            (3, 10, 104, 850, 200, '2026-01-20'),
            (4, 20, 101, 620, 150, '2026-01-22'),
            (5, 20, 103, 1100, 300, '2026-02-01'),
            (6, 20, 105, 2400, 500, '2026-02-05'),
            (7, 20, 106, 380, 100, '2026-02-10'),
            (8, 30, 102, 5500, 1200, '2026-02-15'),
            (9, 30, 106, 920, 200, '2026-02-18'),
            (10, 30, 107, 740, 150, '2026-02-25'),
            (11, 40, 103, 1800, 400, '2026-03-01'),
            (12, 40, 108, 630, 150, '2026-03-05'),
            (13, 40, 109, 15000, 3000, '2026-03-10'),
            (14, 20, 110, 1400, 350, '2026-03-12'),
            (15, 10, 108, 410, 100, '2026-03-18');

        -- Seed Purchase Orders
        INSERT INTO purchase_orders VALUES
            (10001, 1, 10, 101, 200, 24000.0, '2026-01-05', 'Delivered'),
            (10002, 2, 10, 102, 1500, 22500.0, '2026-01-10', 'Delivered'),
            (10003, 4, 10, 104, 400, 34000.0, '2026-01-15', 'Delivered'),
            (10004, 3, 20, 103, 600, 27000.0, '2026-01-25', 'Delivered'),
            (10005, 5, 20, 105, 1000, 30000.0, '2026-01-28', 'Delivered'),
            (10006, 6, 20, 106, 250, 55000.0, '2026-02-01', 'Delivered'),
            (10007, 2, 30, 102, 3000, 45000.0, '2026-02-10', 'Delivered'),
            (10008, 6, 30, 106, 500, 110000.0, '2026-02-12', 'Delivered'),
            (10009, 1, 30, 107, 400, 24000.0, '2026-02-20', 'Delivered'),
            (10010, 3, 40, 108, 300, 42000.0, '2026-02-28', 'Delivered'),
            (10011, 2, 40, 109, 8000, 20000.0, '2026-03-05', 'Delivered'),
            (10012, 1, 20, 101, 300, 36000.0, '2026-03-15', 'In Transit'),
            (10013, 6, 20, 106, 200, 44000.0, '2026-03-20', 'In Transit'),
            (10014, 4, 20, 110, 600, 10800.0, '2026-03-25', 'Processing'),
            (10015, 3, 10, 103, 500, 22500.0, '2026-04-01', 'Pending');
    """)
    conn.commit()
    conn.close()
    print("[CREATED] supply_chain.db (5 tables)")


def create_airline_db():
    """Database 4: 6 tables (airports, airlines, aircraft, flights, passengers, tickets)"""
    path = os.path.join(DATA_DIR, "airline_flight_ops.db")
    if os.path.exists(path):
        os.remove(path)

    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE airports (
            airport_code TEXT PRIMARY KEY,
            airport_name TEXT NOT NULL,
            city TEXT NOT NULL,
            country TEXT NOT NULL,
            timezone TEXT NOT NULL
        );

        CREATE TABLE airlines (
            airline_id INTEGER PRIMARY KEY,
            airline_name TEXT NOT NULL,
            iata_code TEXT UNIQUE NOT NULL,
            headquarters_country TEXT NOT NULL,
            founded_year INTEGER NOT NULL
        );

        CREATE TABLE aircraft (
            aircraft_id INTEGER PRIMARY KEY,
            model TEXT NOT NULL,
            manufacturer TEXT NOT NULL,
            seating_capacity INTEGER NOT NULL,
            airline_id INTEGER NOT NULL,
            in_service_since TEXT NOT NULL,
            FOREIGN KEY (airline_id) REFERENCES airlines(airline_id)
        );

        CREATE TABLE flights (
            flight_id INTEGER PRIMARY KEY,
            flight_number TEXT NOT NULL,
            airline_id INTEGER NOT NULL,
            aircraft_id INTEGER NOT NULL,
            origin_code TEXT NOT NULL,
            dest_code TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            arrival_time TEXT NOT NULL,
            base_fare REAL NOT NULL,
            distance_miles INTEGER NOT NULL,
            FOREIGN KEY (airline_id) REFERENCES airlines(airline_id),
            FOREIGN KEY (aircraft_id) REFERENCES aircraft(aircraft_id),
            FOREIGN KEY (origin_code) REFERENCES airports(airport_code),
            FOREIGN KEY (dest_code) REFERENCES airports(airport_code)
        );

        CREATE TABLE passengers (
            passenger_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            passport_number TEXT UNIQUE NOT NULL,
            nationality TEXT NOT NULL,
            frequent_flyer_tier TEXT NOT NULL
        );

        CREATE TABLE tickets (
            ticket_id INTEGER PRIMARY KEY,
            flight_id INTEGER NOT NULL,
            passenger_id INTEGER NOT NULL,
            seat_number TEXT NOT NULL,
            ticket_class TEXT COLLATE NOCASE NOT NULL,
            fare_paid REAL NOT NULL,
            booking_status TEXT COLLATE NOCASE NOT NULL,
            booking_timestamp TEXT NOT NULL,
            FOREIGN KEY (flight_id) REFERENCES flights(flight_id),
            FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id)
        );

        -- Seed Airports
        INSERT INTO airports VALUES
            ('JFK', 'John F. Kennedy International', 'New York', 'USA', 'America/New_York'),
            ('LHR', 'London Heathrow Airport', 'London', 'UK', 'Europe/London'),
            ('HND', 'Tokyo Haneda International', 'Tokyo', 'Japan', 'Asia/Tokyo'),
            ('CDG', 'Charles de Gaulle Airport', 'Paris', 'France', 'Europe/Paris'),
            ('ORD', 'OHare International Airport', 'Chicago', 'USA', 'America/Chicago'),
            ('SIN', 'Singapore Changi Airport', 'Singapore', 'Singapore', 'Asia/Singapore'),
            ('SFO', 'San Francisco International', 'San Francisco', 'USA', 'America/Los_Angeles'),
            ('DXB', 'Dubai International Airport', 'Dubai', 'UAE', 'Asia/Dubai');

        -- Seed Airlines
        INSERT INTO airlines VALUES
            (1, 'AeroGlobal Airways', 'AG', 'USA', 1985),
            (2, 'TransAtlantic British', 'TB', 'UK', 1974),
            (3, 'Nippon Sky Carriers', 'NS', 'Japan', 1968),
            (4, 'Air Republique', 'AR', 'France', 1980),
            (5, 'Pacific Horizon Air', 'PH', 'Singapore', 1995);

        -- Seed Aircraft
        INSERT INTO aircraft VALUES
            (501, 'Boeing 787-9', 'Boeing', 290, 1, '2018-05-12'),
            (502, 'Boeing 777-300ER', 'Boeing', 396, 1, '2016-10-20'),
            (503, 'Airbus A350-1000', 'Airbus', 366, 2, '2020-02-15'),
            (504, 'Airbus A380-800', 'Airbus', 480, 2, '2015-08-30'),
            (505, 'Boeing 787-8', 'Boeing', 242, 3, '2019-11-04'),
            (506, 'Airbus A350-900', 'Airbus', 325, 4, '2021-06-18'),
            (507, 'Airbus A350-900ULR', 'Airbus', 161, 5, '2022-01-25'),
            (508, 'Boeing 777-200LR', 'Boeing', 314, 5, '2017-04-10');

        -- Seed Flights
        INSERT INTO flights VALUES
            (101, 'AG-100', 1, 501, 'JFK', 'LHR', '08:30', '20:45', 680.0, 3451),
            (102, 'AG-205', 1, 502, 'JFK', 'HND', '11:15', '14:30', 1250.0, 6772),
            (103, 'TB-401', 2, 503, 'LHR', 'JFK', '14:00', '17:15', 720.0, 3451),
            (104, 'TB-880', 2, 504, 'LHR', 'SIN', '21:30', '17:45', 980.0, 6765),
            (105, 'NS-012', 3, 505, 'HND', 'SFO', '17:50', '11:20', 1100.0, 5160),
            (106, 'NS-055', 3, 505, 'HND', 'SIN', '09:40', '16:05', 650.0, 3290),
            (107, 'AR-310', 4, 506, 'CDG', 'JFK', '13:20', '16:00', 740.0, 3635),
            (108, 'AR-720', 4, 506, 'CDG', 'DXB', '15:45', '00:30', 610.0, 3258),
            (109, 'PH-021', 5, 507, 'SIN', 'JFK', '23:35', '06:00', 1650.0, 9537),
            (110, 'PH-108', 5, 508, 'SIN', 'LHR', '01:15', '07:55', 920.0, 6765),
            (111, 'AG-450', 1, 501, 'ORD', 'LHR', '18:10', '08:15', 710.0, 3953),
            (112, 'TB-215', 2, 503, 'LHR', 'DXB', '12:00', '22:10', 580.0, 3404);

        -- Seed Passengers
        INSERT INTO passengers VALUES
            (1, 'Liam', 'Gallagher', 'UK7721890', 'British', 'Gold'),
            (2, 'Sophia', 'Loren', 'IT4491203', 'Italian', 'Platinum'),
            (3, 'Hiroshi', 'Tanaka', 'JP9912044', 'Japanese', 'Diamond'),
            (4, 'Amara', 'Okonkwo', 'NG1124589', 'Nigerian', 'Silver'),
            (5, 'Carlos', 'Santana', 'US8841209', 'American', 'Gold'),
            (6, 'Elena', 'Rostova', 'FR3319082', 'French', 'Standard'),
            (7, 'Chen', 'Wei', 'CN6652390', 'Chinese', 'Platinum'),
            (8, 'David', 'Miller', 'US5543187', 'American', 'Diamond'),
            (9, 'Ananya', 'Deshmukh', 'IN2298714', 'Indian', 'Silver'),
            (10, 'Lucas', 'Silva', 'BR7710923', 'Brazilian', 'Standard');

        -- Seed Tickets
        INSERT INTO tickets VALUES
            (9001, 101, 1, '12A', 'Business', 2450.0, 'Confirmed', '2026-01-05 10:20:00'),
            (9002, 101, 5, '28C', 'Economy', 680.0, 'Confirmed', '2026-01-08 14:15:00'),
            (9003, 102, 3, '02A', 'First', 4800.0, 'Confirmed', '2026-01-12 09:30:00'),
            (9004, 102, 8, '15F', 'Business', 3100.0, 'Confirmed', '2026-01-14 18:45:00'),
            (9005, 103, 2, '01K', 'First', 5200.0, 'Confirmed', '2026-01-20 11:00:00'),
            (9006, 104, 4, '34D', 'Economy', 980.0, 'Confirmed', '2026-01-22 16:10:00'),
            (9007, 104, 9, '14B', 'Business', 2900.0, 'Confirmed', '2026-01-25 12:40:00'),
            (9008, 105, 3, '04E', 'Business', 3400.0, 'Confirmed', '2026-02-01 08:20:00'),
            (9009, 105, 7, '22A', 'Economy', 1100.0, 'Confirmed', '2026-02-03 17:50:00'),
            (9010, 106, 7, '16C', 'Business', 1850.0, 'Confirmed', '2026-02-08 13:15:00'),
            (9011, 107, 6, '31H', 'Economy', 740.0, 'Confirmed', '2026-02-12 10:05:00'),
            (9012, 108, 10, '25B', 'Economy', 610.0, 'Confirmed', '2026-02-15 15:30:00'),
            (9013, 109, 8, '03A', 'Business', 4200.0, 'Confirmed', '2026-02-20 20:00:00'),
            (9014, 110, 1, '18D', 'Business', 2800.0, 'Confirmed', '2026-02-25 09:10:00'),
            (9015, 111, 5, '35A', 'Economy', 710.0, 'Confirmed', '2026-03-01 11:45:00'),
            (9016, 112, 2, '02B', 'First', 4100.0, 'Confirmed', '2026-03-05 14:20:00'),
            (9017, 101, 8, '01A', 'First', 4900.0, 'Confirmed', '2026-03-10 16:50:00'),
            (9018, 102, 7, '19E', 'Economy', 1250.0, 'Confirmed', '2026-03-12 12:15:00');
    """)
    conn.commit()
    conn.close()
    print("[CREATED] airline_flight_ops.db (6 tables)")


def create_hotel_resort_db():
    """Database 5: 7 tables (resorts, room_types, rooms, guests, reservations, amenities, amenity_usage)"""
    path = os.path.join(DATA_DIR, "hotel_resort.db")
    if os.path.exists(path):
        os.remove(path)

    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE resorts (
            resort_id INTEGER PRIMARY KEY,
            resort_name TEXT NOT NULL,
            location TEXT NOT NULL,
            country TEXT NOT NULL,
            star_rating INTEGER NOT NULL,
            total_rooms INTEGER NOT NULL
        );

        CREATE TABLE room_types (
            type_id INTEGER PRIMARY KEY,
            type_name TEXT NOT NULL,
            max_occupancy INTEGER NOT NULL,
            base_price_night REAL NOT NULL,
            has_balcony INTEGER NOT NULL
        );

        CREATE TABLE rooms (
            room_id INTEGER PRIMARY KEY,
            resort_id INTEGER NOT NULL,
            room_number TEXT NOT NULL,
            type_id INTEGER NOT NULL,
            floor INTEGER NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (resort_id) REFERENCES resorts(resort_id),
            FOREIGN KEY (type_id) REFERENCES room_types(type_id)
        );

        CREATE TABLE guests (
            guest_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            country TEXT NOT NULL,
            loyalty_tier TEXT NOT NULL,
            total_spend REAL NOT NULL
        );

        CREATE TABLE reservations (
            reservation_id INTEGER PRIMARY KEY,
            guest_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            check_in_date TEXT NOT NULL,
            check_out_date TEXT NOT NULL,
            nights INTEGER NOT NULL,
            room_total REAL NOT NULL,
            payment_status TEXT COLLATE NOCASE NOT NULL,
            FOREIGN KEY (guest_id) REFERENCES guests(guest_id),
            FOREIGN KEY (room_id) REFERENCES rooms(room_id)
        );

        CREATE TABLE amenities (
            amenity_id INTEGER PRIMARY KEY,
            amenity_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price_per_use REAL NOT NULL,
            duration_minutes INTEGER NOT NULL
        );

        CREATE TABLE amenity_usage (
            usage_id INTEGER PRIMARY KEY,
            reservation_id INTEGER NOT NULL,
            amenity_id INTEGER NOT NULL,
            usage_date TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            total_charge REAL NOT NULL,
            FOREIGN KEY (reservation_id) REFERENCES reservations(reservation_id),
            FOREIGN KEY (amenity_id) REFERENCES amenities(amenity_id)
        );

        -- Seed Resorts
        INSERT INTO resorts VALUES
            (1, 'Azure Horizon Paradise', 'Maui', 'USA', 5, 120),
            (2, 'Alpine Grand Chalet', 'Zermatt', 'Switzerland', 5, 85),
            (3, 'Emerald Lagoon Sanctuary', 'Bora Bora', 'French Polynesia', 5, 60);

        -- Seed Room Types
        INSERT INTO room_types VALUES
            (101, 'Deluxe Ocean View', 2, 450.0, 1),
            (102, 'Executive Suite', 4, 850.0, 1),
            (103, 'Presidential Overwater Villa', 6, 2200.0, 1),
            (104, 'Classic Mountain Lodge', 2, 380.0, 0);

        -- Seed Rooms
        INSERT INTO rooms VALUES
            (201, 1, '101', 101, 1, 'Available'),
            (202, 1, '102', 101, 1, 'Occupied'),
            (203, 1, '201', 102, 2, 'Occupied'),
            (204, 1, '301', 103, 3, 'Occupied'),
            (205, 2, 'A1', 104, 1, 'Available'),
            (206, 2, 'A2', 104, 1, 'Occupied'),
            (207, 2, 'B1', 102, 2, 'Occupied'),
            (208, 2, 'C1', 103, 3, 'Available'),
            (209, 3, 'V01', 103, 1, 'Occupied'),
            (210, 3, 'V02', 103, 1, 'Occupied'),
            (211, 3, 'L01', 101, 1, 'Available'),
            (212, 3, 'L02', 101, 1, 'Occupied');

        -- Seed Guests
        INSERT INTO guests VALUES
            (1, 'Leonardo', 'DiCaprio', 'leo@green.org', 'USA', 'Diamond', 34500.0),
            (2, 'Charlotte', 'Casiraghi', 'charlotte@monaco.mc', 'Monaco', 'Platinum', 21800.0),
            (3, 'Roger', 'Federer', 'roger@basel.ch', 'Switzerland', 'Diamond', 41200.0),
            (4, 'Serena', 'Williams', 'serena@tennis.com', 'USA', 'Diamond', 29000.0),
            (5, 'Guillaume', 'Canet', 'guillaume@cinema.fr', 'France', 'Gold', 14500.0),
            (6, 'Keanu', 'Reeves', 'keanu@arch.ca', 'Canada', 'Platinum', 19800.0),
            (7, 'Amal', 'Clooney', 'amal@humanrights.org', 'UK', 'Diamond', 38000.0),
            (8, 'Hayao', 'Miyazaki', 'hayao@ghibli.jp', 'Japan', 'Gold', 12300.0);

        -- Seed Reservations
        INSERT INTO reservations VALUES
            (501, 1, 204, '2026-01-10', '2026-01-15', 5, 11000.0, 'Paid'),
            (502, 2, 203, '2026-01-12', '2026-01-16', 4, 3400.0, 'Paid'),
            (503, 3, 207, '2026-01-18', '2026-01-25', 7, 5950.0, 'Paid'),
            (504, 4, 209, '2026-02-01', '2026-02-08', 7, 15400.0, 'Paid'),
            (505, 5, 206, '2026-02-05', '2026-02-09', 4, 1520.0, 'Paid'),
            (506, 6, 202, '2026-02-14', '2026-02-20', 6, 2700.0, 'Paid'),
            (507, 7, 210, '2026-02-20', '2026-02-28', 8, 17600.0, 'Paid'),
            (508, 8, 212, '2026-03-01', '2026-03-05', 4, 1800.0, 'Paid'),
            (509, 1, 209, '2026-03-10', '2026-03-17', 7, 15400.0, 'Paid'),
            (510, 3, 204, '2026-03-20', '2026-03-25', 5, 11000.0, 'Pending');

        -- Seed Amenities
        INSERT INTO amenities VALUES
            (11, 'Full Body Balinese Massage', 'Spa', 280.0, 90),
            (12, 'Private Catamaran Sunset Cruise', 'Water Sports', 750.0, 180),
            (13, 'Helicopter Glacier Tour', 'Excursion', 1400.0, 60),
            (14, 'Michelin Chef Tasting Dinner', 'Dining', 450.0, 120),
            (15, 'Scuba Diving Manta Ray Safari', 'Water Sports', 320.0, 150),
            (16, 'Alpine Ski Private Guide', 'Winter Sports', 600.0, 240),
            (17, 'Vintage Wine Cellar Masterclass', 'Dining', 350.0, 90);

        -- Seed Amenity Usage
        INSERT INTO amenity_usage VALUES
            (7001, 501, 12, '2026-01-11', 1, 750.0),
            (7002, 501, 14, '2026-01-13', 2, 900.0),
            (7003, 502, 11, '2026-01-14', 2, 560.0),
            (7004, 503, 13, '2026-01-20', 1, 1400.0),
            (7005, 503, 16, '2026-01-22', 2, 1200.0),
            (7006, 504, 15, '2026-02-03', 2, 640.0),
            (7007, 504, 12, '2026-02-05', 1, 750.0),
            (7008, 505, 16, '2026-02-07', 1, 600.0),
            (7009, 506, 11, '2026-02-16', 1, 280.0),
            (7010, 507, 14, '2026-02-22', 2, 900.0),
            (7011, 507, 15, '2026-02-24', 2, 640.0),
            (7012, 508, 11, '2026-03-03', 1, 280.0),
            (7013, 509, 12, '2026-03-12', 1, 750.0),
            (7014, 509, 14, '2026-03-15', 2, 900.0);
    """)
    conn.commit()
    conn.close()
    print("[CREATED] hotel_resort.db (7 tables)")


if __name__ == "__main__":
    create_hospital_db()
    create_fintech_db()
    create_supply_chain_db()
    create_airline_db()
    create_hotel_resort_db()
    print("\nAll 5 multi-table databases successfully created in data/databases/!")

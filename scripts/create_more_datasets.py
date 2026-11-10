"""
Advanced Multi-Domain Dataset Generator for Text-to-SQL
Creates 7 additional realistic, relational SQLite databases:
1. streaming_entertainment.db  (4 tables)
2. rideshare_mobility.db        (5 tables)
3. real_estate_property.db      (5 tables)
4. telecom_network_ops.db       (6 tables)
5. smart_energy_grid.db         (6 tables)
6. crypto_exchange_market.db    (7 tables)
7. software_dev_git_tracker.db  (8 tables)
"""

import os
import sqlite3

DATA_DIR = os.path.abspath("data/databases")
os.makedirs(DATA_DIR, exist_ok=True)


def create_streaming_db():
    """1. streaming_entertainment.db (4 tables)"""
    path = os.path.join(DATA_DIR, "streaming_entertainment.db")
    if os.path.exists(path):
        os.remove(path)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE genres (
            genre_id INTEGER PRIMARY KEY,
            genre_name TEXT COLLATE NOCASE NOT NULL,
            target_audience TEXT COLLATE NOCASE NOT NULL
        );

        CREATE TABLE content_items (
            content_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            genre_id INTEGER NOT NULL,
            content_type TEXT COLLATE NOCASE NOT NULL,
            release_year INTEGER NOT NULL,
            duration_mins INTEGER NOT NULL,
            imdb_rating REAL NOT NULL,
            FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
        );

        CREATE TABLE subscribers (
            subscriber_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            plan_tier TEXT COLLATE NOCASE NOT NULL,
            monthly_fee REAL NOT NULL,
            country TEXT COLLATE NOCASE NOT NULL,
            signup_date TEXT NOT NULL
        );

        CREATE TABLE watch_history (
            watch_id INTEGER PRIMARY KEY,
            subscriber_id INTEGER NOT NULL,
            content_id INTEGER NOT NULL,
            watch_date TEXT NOT NULL,
            watch_duration_mins INTEGER NOT NULL,
            device_type TEXT COLLATE NOCASE NOT NULL,
            completed INTEGER NOT NULL,
            FOREIGN KEY (subscriber_id) REFERENCES subscribers(subscriber_id),
            FOREIGN KEY (content_id) REFERENCES content_items(content_id)
        );

        INSERT INTO genres VALUES
            (1, 'Sci-Fi', 'General Adult'),
            (2, 'Drama', 'Mature Adult'),
            (3, 'Comedy', 'All Ages'),
            (4, 'Action', 'Teens & Adults'),
            (5, 'Documentary', 'General Adult');

        INSERT INTO content_items VALUES
            (101, 'Quantum Odyssey', 1, 'Movie', 2024, 142, 8.7),
            (102, 'Silicon Dreams', 2, 'Series', 2023, 55, 8.4),
            (103, 'Laugh Protocol', 3, 'Movie', 2022, 98, 7.1),
            (104, 'Apex Velocity', 4, 'Movie', 2025, 126, 8.1),
            (105, 'Planet Coral: The Deep', 5, 'Series', 2024, 60, 9.1),
            (106, 'The Neural Heist', 1, 'Movie', 2023, 115, 7.9),
            (107, 'Wall Street Wolves', 2, 'Series', 2022, 50, 8.6),
            (108, 'Cyberpunk Seoul', 1, 'Series', 2024, 48, 8.3);

        INSERT INTO subscribers VALUES
            (1, 'Emma Watson', 'emma@ukstream.co.uk', 'Premium 4K', 19.99, 'UK', '2022-04-10'),
            (2, 'Liam Hemsworth', 'liam@aussie.net', 'Standard', 14.99, 'Australia', '2023-01-15'),
            (3, 'Zendaya Coleman', 'z@hollywood.com', 'Premium 4K', 19.99, 'USA', '2021-08-20'),
            (4, 'Pedro Pascal', 'pedro@chile.cl', 'Standard', 14.99, 'USA', '2023-06-05'),
            (5, 'Keanu Reeves', 'keanu@neo.ca', 'Basic', 9.99, 'Canada', '2024-02-12'),
            (6, 'Song Kang-ho', 'song@cinema.kr', 'Premium 4K', 19.99, 'South Korea', '2022-11-01');

        INSERT INTO watch_history VALUES
            (1001, 1, 101, '2026-01-10', 142, 'Smart TV', 1),
            (1002, 1, 105, '2026-01-15', 60, 'Tablet', 1),
            (1003, 2, 103, '2026-01-18', 95, 'Mobile', 1),
            (1004, 3, 101, '2026-01-20', 142, 'Smart TV', 1),
            (1005, 3, 102, '2026-01-22', 55, 'Smart TV', 1),
            (1006, 3, 105, '2026-01-28', 60, 'Smart TV', 1),
            (1007, 4, 104, '2026-02-02', 126, 'Console', 1),
            (1008, 4, 106, '2026-02-08', 80, 'Mobile', 0),
            (1009, 5, 108, '2026-02-14', 48, 'Laptop', 1),
            (1010, 6, 108, '2026-02-20', 48, 'Smart TV', 1),
            (1011, 6, 107, '2026-02-25', 50, 'Smart TV', 1),
            (1012, 1, 104, '2026-03-01', 126, 'Smart TV', 1);
    """)
    conn.commit()
    conn.close()
    print("[CREATED] streaming_entertainment.db (4 tables)")


def create_rideshare_db():
    """2. rideshare_mobility.db (5 tables)"""
    path = os.path.join(DATA_DIR, "rideshare_mobility.db")
    if os.path.exists(path):
        os.remove(path)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE cities (
            city_id INTEGER PRIMARY KEY,
            city_name TEXT COLLATE NOCASE NOT NULL,
            country TEXT COLLATE NOCASE NOT NULL,
            surge_multiplier REAL NOT NULL,
            is_active INTEGER NOT NULL
        );

        CREATE TABLE drivers (
            driver_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            vehicle_model TEXT NOT NULL,
            license_plate TEXT UNIQUE NOT NULL,
            rating REAL NOT NULL,
            total_trips INTEGER NOT NULL,
            city_id INTEGER NOT NULL,
            FOREIGN KEY (city_id) REFERENCES cities(city_id)
        );

        CREATE TABLE riders (
            rider_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            rating REAL NOT NULL,
            payment_method TEXT COLLATE NOCASE NOT NULL,
            joined_date TEXT NOT NULL
        );

        CREATE TABLE rides (
            ride_id INTEGER PRIMARY KEY,
            driver_id INTEGER NOT NULL,
            rider_id INTEGER NOT NULL,
            city_id INTEGER NOT NULL,
            request_time TEXT NOT NULL,
            distance_km REAL NOT NULL,
            duration_mins INTEGER NOT NULL,
            fare_amount REAL NOT NULL,
            status TEXT COLLATE NOCASE NOT NULL,
            FOREIGN KEY (driver_id) REFERENCES drivers(driver_id),
            FOREIGN KEY (rider_id) REFERENCES riders(rider_id),
            FOREIGN KEY (city_id) REFERENCES cities(city_id)
        );

        CREATE TABLE driver_payouts (
            payout_id INTEGER PRIMARY KEY,
            driver_id INTEGER NOT NULL,
            payout_date TEXT NOT NULL,
            net_earnings REAL NOT NULL,
            tips REAL NOT NULL,
            fuel_bonus REAL NOT NULL,
            FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
        );

        INSERT INTO cities VALUES
            (1, 'San Francisco', 'USA', 1.4, 1),
            (2, 'New York', 'USA', 1.6, 1),
            (3, 'London', 'UK', 1.3, 1),
            (4, 'Tokyo', 'Japan', 1.2, 1);

        INSERT INTO drivers VALUES
            (101, 'Marcus Thorne', 'Tesla Model 3', 'SF-7781', 4.92, 1420, 1),
            (102, 'Elena Rostova', 'Toyota Camry Hybrid', 'NY-9904', 4.88, 2850, 2),
            (103, 'James Sterling', 'Mercedes EQE', 'LON-4412', 4.95, 980, 3),
            (104, 'Kenji Takahashi', 'Toyota Prius Alpha', 'TK-2109', 4.97, 3100, 4),
            (105, 'Chloe Bennett', 'Hyundai Ioniq 5', 'SF-3321', 4.85, 750, 1);

        INSERT INTO riders VALUES
            (1, 'Alice Morgan', 'alice@sftech.io', 4.95, 'Apple Pay', '2023-02-10'),
            (2, 'Bruce Wayne', 'bruce@wayne.corp', 5.00, 'Corporate Card', '2021-05-15'),
            (3, 'Diana Prince', 'diana@amazon.gr', 4.98, 'Credit Card', '2022-09-01'),
            (4, 'Clark Kent', 'clark@dailyplanet.com', 4.90, 'Debit Card', '2023-11-20'),
            (5, 'Barry Allen', 'barry@centralcity.edu', 4.82, 'PayPal', '2024-01-05');

        INSERT INTO rides VALUES
            (501, 101, 1, 1, '2026-01-10 08:30:00', 12.5, 24, 38.50, 'Completed'),
            (502, 101, 2, 1, '2026-01-12 18:45:00', 8.2, 18, 29.00, 'Completed'),
            (503, 102, 2, 2, '2026-01-15 09:15:00', 15.0, 42, 65.00, 'Completed'),
            (504, 102, 4, 2, '2026-01-20 22:10:00', 6.4, 15, 24.50, 'Completed'),
            (505, 103, 3, 3, '2026-02-01 14:00:00', 18.2, 35, 52.00, 'Completed'),
            (506, 104, 5, 4, '2026-02-05 11:20:00', 22.0, 40, 78.00, 'Completed'),
            (507, 105, 1, 1, '2026-02-12 17:30:00', 5.5, 14, 18.00, 'Completed'),
            (508, 101, 3, 1, '2026-02-18 20:00:00', 14.0, 28, 44.00, 'Completed'),
            (509, 102, 5, 2, '2026-02-25 16:40:00', 9.8, 22, 32.50, 'Completed'),
            (510, 104, 2, 4, '2026-03-01 13:10:00', 11.5, 25, 41.00, 'Completed');

        INSERT INTO driver_payouts VALUES
            (1, 101, '2026-01-31', 2850.0, 420.0, 150.0),
            (2, 102, '2026-01-31', 3420.0, 510.0, 200.0),
            (3, 103, '2026-01-31', 2100.0, 310.0, 100.0),
            (4, 104, '2026-01-31', 3800.0, 600.0, 250.0),
            (5, 105, '2026-01-31', 1650.0, 220.0, 80.0);
    """)
    conn.commit()
    conn.close()
    print("[CREATED] rideshare_mobility.db (5 tables)")


def create_real_estate_db():
    """3. real_estate_property.db (5 tables)"""
    path = os.path.join(DATA_DIR, "real_estate_property.db")
    if os.path.exists(path):
        os.remove(path)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE agencies (
            agency_id INTEGER PRIMARY KEY,
            agency_name TEXT NOT NULL,
            city TEXT COLLATE NOCASE NOT NULL,
            commission_rate REAL NOT NULL,
            founded_year INTEGER NOT NULL
        );

        CREATE TABLE agents (
            agent_id INTEGER PRIMARY KEY,
            agency_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            license_number TEXT UNIQUE NOT NULL,
            sales_volume REAL NOT NULL,
            experience_years INTEGER NOT NULL,
            FOREIGN KEY (agency_id) REFERENCES agencies(agency_id)
        );

        CREATE TABLE properties (
            property_id INTEGER PRIMARY KEY,
            agent_id INTEGER NOT NULL,
            address TEXT NOT NULL,
            property_type TEXT COLLATE NOCASE NOT NULL,
            bedrooms INTEGER NOT NULL,
            bathrooms REAL NOT NULL,
            square_feet INTEGER NOT NULL,
            list_price REAL NOT NULL,
            status TEXT COLLATE NOCASE NOT NULL,
            FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
        );

        CREATE TABLE clients (
            client_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            budget_max REAL NOT NULL,
            preferred_type TEXT COLLATE NOCASE NOT NULL,
            is_preapproved INTEGER NOT NULL
        );

        CREATE TABLE property_offers (
            offer_id INTEGER PRIMARY KEY,
            property_id INTEGER NOT NULL,
            client_id INTEGER NOT NULL,
            offer_amount REAL NOT NULL,
            offer_date TEXT NOT NULL,
            status TEXT COLLATE NOCASE NOT NULL,
            FOREIGN KEY (property_id) REFERENCES properties(property_id),
            FOREIGN KEY (client_id) REFERENCES clients(client_id)
        );

        INSERT INTO agencies VALUES
            (1, 'Premier Manhattan Realty', 'New York', 0.05, 1998),
            (2, 'Pacific Coast Estates', 'San Francisco', 0.045, 2005),
            (3, 'Windy City Properties', 'Chicago', 0.055, 2010);

        INSERT INTO agents VALUES
            (101, 1, 'Victoria Sterling', 'NY-RE-88910', 48500000.0, 16),
            (102, 1, 'Julian Vance', 'NY-RE-77124', 32000000.0, 10),
            (103, 2, 'Seraphina Lin', 'CA-DRE-01992', 62000000.0, 14),
            (104, 3, 'David OConnor', 'IL-IDF-55410', 21500000.0, 8);

        INSERT INTO properties VALUES
            (1, 101, '432 Park Ave Penthouse 54B', 'Condo', 4, 4.5, 4200, 18500000.0, 'Active'),
            (2, 101, '120 W 72nd St Apt 8C', 'Apartment', 2, 2.0, 1450, 2400000.0, 'Pending'),
            (3, 102, '88 Greenwich St Loft 12', 'Condo', 1, 1.5, 950, 1350000.0, 'Sold'),
            (4, 103, '2800 Pacific Ave', 'Single Family', 5, 5.5, 5800, 14800000.0, 'Active'),
            (5, 103, '450 Mission St Unit 3201', 'Condo', 2, 2.5, 1800, 3100000.0, 'Sold'),
            (6, 104, '1300 N Lake Shore Dr 19A', 'Condo', 3, 3.0, 2600, 1850000.0, 'Active'),
            (7, 104, '445 W Wellington Ave', 'Townhouse', 4, 3.5, 3400, 2200000.0, 'Pending');

        INSERT INTO clients VALUES
            (1, 'Jonathan Gold', 'jgold@hedgecapital.com', 20000000.0, 'Condo', 1),
            (2, 'Maria Santos', 'maria@techventures.io', 4000000.0, 'Condo', 1),
            (3, 'Arthur Pendelton', 'arthur@illinois.edu', 2500000.0, 'Townhouse', 1),
            (4, 'Rachel Green', 'rachel@ralphlauren.com', 1500000.0, 'Apartment', 0);

        INSERT INTO property_offers VALUES
            (1001, 1, 1, 17800000.0, '2026-01-15', 'Pending'),
            (1002, 2, 2, 2350000.0, '2026-01-20', 'Accepted'),
            (1003, 3, 4, 1300000.0, '2026-01-25', 'Accepted'),
            (1004, 5, 2, 3050000.0, '2026-02-05', 'Accepted'),
            (1005, 7, 3, 2150000.0, '2026-02-14', 'Accepted');
    """)
    conn.commit()
    conn.close()
    print("[CREATED] real_estate_property.db (5 tables)")


def create_telecom_db():
    """4. telecom_network_ops.db (6 tables)"""
    path = os.path.join(DATA_DIR, "telecom_network_ops.db")
    if os.path.exists(path):
        os.remove(path)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE regions (
            region_id INTEGER PRIMARY KEY,
            region_name TEXT NOT NULL,
            state TEXT COLLATE NOCASE NOT NULL,
            pop_served INTEGER NOT NULL
        );

        CREATE TABLE cell_towers (
            tower_id INTEGER PRIMARY KEY,
            region_id INTEGER NOT NULL,
            tower_name TEXT NOT NULL,
            bandwidth_gbps REAL NOT NULL,
            frequency_band TEXT NOT NULL,
            status TEXT COLLATE NOCASE NOT NULL,
            FOREIGN KEY (region_id) REFERENCES regions(region_id)
        );

        CREATE TABLE plans (
            plan_id INTEGER PRIMARY KEY,
            plan_name TEXT NOT NULL,
            monthly_data_gb INTEGER NOT NULL,
            monthly_cost REAL NOT NULL,
            is_5g_enabled INTEGER NOT NULL
        );

        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            phone_number TEXT UNIQUE NOT NULL,
            plan_id INTEGER NOT NULL,
            region_id INTEGER NOT NULL,
            account_balance REAL NOT NULL,
            FOREIGN KEY (plan_id) REFERENCES plans(plan_id),
            FOREIGN KEY (region_id) REFERENCES regions(region_id)
        );

        CREATE TABLE call_records (
            cdr_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            tower_id INTEGER NOT NULL,
            call_type TEXT COLLATE NOCASE NOT NULL,
            duration_secs INTEGER NOT NULL,
            data_mb REAL NOT NULL,
            call_timestamp TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (tower_id) REFERENCES cell_towers(tower_id)
        );

        CREATE TABLE outage_incidents (
            incident_id INTEGER PRIMARY KEY,
            tower_id INTEGER NOT NULL,
            severity TEXT COLLATE NOCASE NOT NULL,
            downtime_minutes INTEGER NOT NULL,
            root_cause TEXT NOT NULL,
            incident_date TEXT NOT NULL,
            FOREIGN KEY (tower_id) REFERENCES cell_towers(tower_id)
        );

        INSERT INTO regions VALUES
            (1, 'Northeast Metro', 'NY', 8500000),
            (2, 'Bay Area Coastal', 'CA', 4200000),
            (3, 'Great Lakes North', 'IL', 2800000);

        INSERT INTO cell_towers VALUES
            (101, 1, 'Manhattan Midtown 5G-01', 100.0, '3.5 GHz (C-Band)', 'Online'),
            (102, 1, 'Brooklyn Heights Sub-04', 50.0, '1.9 GHz (PCS)', 'Online'),
            (103, 2, 'SoMa Tech Core 5G-08', 120.0, '28 GHz (mmWave)', 'Online'),
            (104, 2, 'Palo Alto Foothills 02', 40.0, '700 MHz (Low-Band)', 'Maintenance'),
            (105, 3, 'Chicago Loop Tower 5G-03', 90.0, '3.5 GHz (C-Band)', 'Online');

        INSERT INTO plans VALUES
            (1, 'Unlimited Ultra 5G', 500, 85.0, 1),
            (2, 'Essential Everyday', 50, 55.0, 1),
            (3, 'Basic Starter', 15, 35.0, 0);

        INSERT INTO customers VALUES
            (1, 'Alexander Bell', '212-555-0101', 1, 1, 0.0),
            (2, 'Hedy Lamarr', '415-555-0202', 1, 2, 15.50),
            (3, 'Guglielmo Marconi', '312-555-0303', 2, 3, 0.0),
            (4, 'Claude Shannon', '212-555-0404', 1, 1, 45.00),
            (5, 'Ada Lovelace', '415-555-0505', 2, 2, 0.0);

        INSERT INTO call_records VALUES
            (10001, 1, 101, 'Voice', 340, 0.0, '2026-01-10 10:15:00'),
            (10002, 1, 101, 'Data', 0, 1420.5, '2026-01-10 11:00:00'),
            (10003, 2, 103, 'Data', 0, 4850.0, '2026-01-12 14:30:00'),
            (10004, 3, 105, 'Voice', 520, 0.0, '2026-01-15 16:20:00'),
            (10005, 4, 101, 'Data', 0, 3100.0, '2026-01-18 09:45:00'),
            (10006, 5, 103, 'Voice', 180, 0.0, '2026-01-22 13:10:00');

        INSERT INTO outage_incidents VALUES
            (1, 104, 'Major', 180, 'Fiber cut during street excavation', '2026-01-08'),
            (2, 102, 'Minor', 35, 'Power supply backup switch failure', '2026-01-25');
    """)
    conn.commit()
    conn.close()
    print("[CREATED] telecom_network_ops.db (6 tables)")


def create_smart_energy_db():
    """5. smart_energy_grid.db (6 tables)"""
    path = os.path.join(DATA_DIR, "smart_energy_grid.db")
    if os.path.exists(path):
        os.remove(path)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE substations (
            substation_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            grid_zone TEXT COLLATE NOCASE NOT NULL,
            capacity_mw REAL NOT NULL,
            transformer_count INTEGER NOT NULL
        );

        CREATE TABLE energy_sources (
            source_id INTEGER PRIMARY KEY,
            source_name TEXT NOT NULL,
            source_type TEXT COLLATE NOCASE NOT NULL,
            cost_per_mwh REAL NOT NULL,
            carbon_intensity_kg REAL NOT NULL
        );

        CREATE TABLE generators (
            generator_id INTEGER PRIMARY KEY,
            substation_id INTEGER NOT NULL,
            source_id INTEGER NOT NULL,
            max_output_mw REAL NOT NULL,
            status TEXT COLLATE NOCASE NOT NULL,
            FOREIGN KEY (substation_id) REFERENCES substations(substation_id),
            FOREIGN KEY (source_id) REFERENCES energy_sources(source_id)
        );

        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            tariff_type TEXT COLLATE NOCASE NOT NULL,
            substation_id INTEGER NOT NULL,
            solar_installed INTEGER NOT NULL,
            FOREIGN KEY (substation_id) REFERENCES substations(substation_id)
        );

        CREATE TABLE meter_readings (
            reading_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            reading_time TEXT NOT NULL,
            kwh_consumed REAL NOT NULL,
            kwh_exported REAL NOT NULL,
            peak_kw REAL NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );

        CREATE TABLE grid_alerts (
            alert_id INTEGER PRIMARY KEY,
            substation_id INTEGER NOT NULL,
            alert_type TEXT COLLATE NOCASE NOT NULL,
            severity TEXT COLLATE NOCASE NOT NULL,
            alert_timestamp TEXT NOT NULL,
            FOREIGN KEY (substation_id) REFERENCES substations(substation_id)
        );

        INSERT INTO substations VALUES
            (1, 'Desert Sunrise Sub-01', 'Western Zone', 500.0, 4),
            (2, 'Coastal Wind Terminal 02', 'Pacific Zone', 650.0, 6),
            (3, 'Appalachian Hydro Hub 03', 'Eastern Zone', 400.0, 3);

        INSERT INTO energy_sources VALUES
            (101, 'Mojave Photovoltaic Array', 'Solar', 32.50, 0.0),
            (102, 'Pacific Offshore Wind Farm', 'Wind', 41.00, 0.0),
            (103, 'Columbia River Hydro Plant', 'Hydroelectric', 28.00, 0.0),
            (104, 'Clear Creek Peaker Plant', 'Natural Gas', 75.00, 420.0);

        INSERT INTO generators VALUES
            (201, 1, 101, 250.0, 'Online'),
            (202, 1, 104, 150.0, 'Standby'),
            (203, 2, 102, 400.0, 'Online'),
            (204, 3, 103, 300.0, 'Online');

        INSERT INTO customers VALUES
            (1, 'Apex Data Center West', 'Industrial', 1, 0),
            (2, 'BioMed Labs Pacific', 'Commercial', 2, 1),
            (3, 'Oakwood Residential Community', 'Residential', 3, 1),
            (4, 'Metro Light Rail Transit', 'Industrial', 2, 0);

        INSERT INTO meter_readings VALUES
            (1001, 1, '2026-01-15 12:00:00', 4200.0, 0.0, 4500.0),
            (1002, 2, '2026-01-15 12:00:00', 850.0, 120.0, 920.0),
            (1003, 3, '2026-01-15 12:00:00', 320.0, 85.0, 350.0),
            (1004, 4, '2026-01-15 12:00:00', 1900.0, 0.0, 2100.0),
            (1005, 1, '2026-01-15 18:00:00', 4450.0, 0.0, 4600.0),
            (1006, 2, '2026-01-15 18:00:00', 620.0, 10.0, 680.0);

        INSERT INTO grid_alerts VALUES
            (1, 1, 'Overfrequency', 'Low', '2026-01-10 13:45:00'),
            (2, 2, 'Transmission Line Congestion', 'Medium', '2026-01-18 17:30:00');
    """)
    conn.commit()
    conn.close()
    print("[CREATED] smart_energy_grid.db (6 tables)")


def create_crypto_market_db():
    """6. crypto_exchange_market.db (7 tables)"""
    path = os.path.join(DATA_DIR, "crypto_exchange_market.db")
    if os.path.exists(path):
        os.remove(path)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE assets (
            asset_symbol TEXT PRIMARY KEY,
            asset_name TEXT NOT NULL,
            asset_type TEXT COLLATE NOCASE NOT NULL,
            market_cap_billions REAL NOT NULL
        );

        CREATE TABLE trading_pairs (
            pair_symbol TEXT PRIMARY KEY,
            base_asset TEXT NOT NULL,
            quote_asset TEXT NOT NULL,
            min_lot_size REAL NOT NULL,
            taker_fee_pct REAL NOT NULL,
            FOREIGN KEY (base_asset) REFERENCES assets(asset_symbol),
            FOREIGN KEY (quote_asset) REFERENCES assets(asset_symbol)
        );

        CREATE TABLE traders (
            trader_id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            vip_level INTEGER NOT NULL,
            kyc_status TEXT COLLATE NOCASE NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE wallets (
            wallet_id INTEGER PRIMARY KEY,
            trader_id INTEGER NOT NULL,
            asset_symbol TEXT NOT NULL,
            balance REAL NOT NULL,
            locked_balance REAL NOT NULL,
            FOREIGN KEY (trader_id) REFERENCES traders(trader_id),
            FOREIGN KEY (asset_symbol) REFERENCES assets(asset_symbol)
        );

        CREATE TABLE limit_orders (
            order_id INTEGER PRIMARY KEY,
            trader_id INTEGER NOT NULL,
            pair_symbol TEXT NOT NULL,
            order_side TEXT COLLATE NOCASE NOT NULL,
            price REAL NOT NULL,
            quantity REAL NOT NULL,
            status TEXT COLLATE NOCASE NOT NULL,
            FOREIGN KEY (trader_id) REFERENCES traders(trader_id),
            FOREIGN KEY (pair_symbol) REFERENCES trading_pairs(pair_symbol)
        );

        CREATE TABLE trades (
            trade_id INTEGER PRIMARY KEY,
            pair_symbol TEXT NOT NULL,
            buyer_id INTEGER NOT NULL,
            seller_id INTEGER NOT NULL,
            price REAL NOT NULL,
            quantity REAL NOT NULL,
            trade_time TEXT NOT NULL,
            FOREIGN KEY (pair_symbol) REFERENCES trading_pairs(pair_symbol),
            FOREIGN KEY (buyer_id) REFERENCES traders(trader_id),
            FOREIGN KEY (seller_id) REFERENCES traders(trader_id)
        );

        CREATE TABLE transfers (
            transfer_id INTEGER PRIMARY KEY,
            trader_id INTEGER NOT NULL,
            asset_symbol TEXT NOT NULL,
            direction TEXT COLLATE NOCASE NOT NULL,
            amount REAL NOT NULL,
            status TEXT COLLATE NOCASE NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (trader_id) REFERENCES traders(trader_id),
            FOREIGN KEY (asset_symbol) REFERENCES assets(asset_symbol)
        );

        INSERT INTO assets VALUES
            ('BTC', 'Bitcoin', 'Layer 1', 1950.0),
            ('ETH', 'Ethereum', 'Smart Contract', 450.0),
            ('SOL', 'Solana', 'Layer 1', 95.0),
            ('USDT', 'Tether USD', 'Stablecoin', 120.0),
            ('USDC', 'USD Coin', 'Stablecoin', 40.0);

        INSERT INTO trading_pairs VALUES
            ('BTC/USDT', 'BTC', 'USDT', 0.0001, 0.001),
            ('ETH/USDT', 'ETH', 'USDT', 0.001, 0.001),
            ('SOL/USDC', 'SOL', 'USDC', 0.01, 0.0015);

        INSERT INTO traders VALUES
            (1, 'satoshi_quant', 5, 'Verified', '2021-02-10'),
            (2, 'vitalik_fan', 3, 'Verified', '2022-06-15'),
            (3, 'solana_speed', 2, 'Verified', '2023-08-20'),
            (4, 'whale_watcher', 4, 'Verified', '2022-11-04');

        INSERT INTO wallets VALUES
            (101, 1, 'BTC', 14.5, 2.0),
            (102, 1, 'USDT', 250000.0, 50000.0),
            (103, 2, 'ETH', 85.0, 10.0),
            (104, 2, 'USDT', 75000.0, 0.0),
            (105, 3, 'SOL', 650.0, 100.0),
            (106, 3, 'USDC', 45000.0, 5000.0),
            (107, 4, 'BTC', 42.0, 0.0),
            (108, 4, 'USDT', 1200000.0, 200000.0);

        INSERT INTO limit_orders VALUES
            (501, 1, 'BTC/USDT', 'Buy', 92500.0, 1.5, 'Open'),
            (502, 1, 'BTC/USDT', 'Sell', 98000.0, 2.0, 'Open'),
            (503, 2, 'ETH/USDT', 'Buy', 3350.0, 5.0, 'Filled'),
            (504, 3, 'SOL/USDC', 'Sell', 215.0, 25.0, 'Filled'),
            (505, 4, 'BTC/USDT', 'Buy', 94000.0, 3.0, 'Filled');

        INSERT INTO trades VALUES
            (9001, 'ETH/USDT', 2, 4, 3350.0, 5.0, '2026-01-20 14:32:00'),
            (9002, 'SOL/USDC', 1, 3, 215.0, 25.0, '2026-01-21 16:15:00'),
            (9003, 'BTC/USDT', 4, 1, 94000.0, 3.0, '2026-01-22 18:40:00');

        INSERT INTO transfers VALUES
            (801, 1, 'USDT', 'Deposit', 100000.0, 'Completed', '2026-01-05 10:00:00'),
            (802, 2, 'ETH', 'Withdrawal', 10.0, 'Completed', '2026-01-18 12:30:00'),
            (803, 4, 'BTC', 'Deposit', 20.0, 'Completed', '2026-01-19 09:15:00');
    """)
    conn.commit()
    conn.close()
    print("[CREATED] crypto_exchange_market.db (7 tables)")


def create_git_tracker_db():
    """7. software_dev_git_tracker.db (8 tables)"""
    path = os.path.join(DATA_DIR, "software_dev_git_tracker.db")
    if os.path.exists(path):
        os.remove(path)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE organizations (
            org_id INTEGER PRIMARY KEY,
            org_name TEXT NOT NULL,
            tier TEXT COLLATE NOCASE NOT NULL,
            seat_count INTEGER NOT NULL
        );

        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY,
            org_id INTEGER NOT NULL,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT COLLATE NOCASE NOT NULL,
            FOREIGN KEY (org_id) REFERENCES organizations(org_id)
        );

        CREATE TABLE repositories (
            repo_id INTEGER PRIMARY KEY,
            org_id INTEGER NOT NULL,
            repo_name TEXT NOT NULL,
            language TEXT COLLATE NOCASE NOT NULL,
            star_count INTEGER NOT NULL,
            is_private INTEGER NOT NULL,
            FOREIGN KEY (org_id) REFERENCES organizations(org_id)
        );

        CREATE TABLE branches (
            branch_id INTEGER PRIMARY KEY,
            repo_id INTEGER NOT NULL,
            branch_name TEXT NOT NULL,
            is_protected INTEGER NOT NULL,
            FOREIGN KEY (repo_id) REFERENCES repositories(repo_id)
        );

        CREATE TABLE commits (
            commit_id INTEGER PRIMARY KEY,
            repo_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            lines_added INTEGER NOT NULL,
            lines_deleted INTEGER NOT NULL,
            commit_date TEXT NOT NULL,
            FOREIGN KEY (repo_id) REFERENCES repositories(repo_id),
            FOREIGN KEY (author_id) REFERENCES users(user_id)
        );

        CREATE TABLE pull_requests (
            pr_id INTEGER PRIMARY KEY,
            repo_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            status TEXT COLLATE NOCASE NOT NULL,
            created_date TEXT NOT NULL,
            FOREIGN KEY (repo_id) REFERENCES repositories(repo_id),
            FOREIGN KEY (author_id) REFERENCES users(user_id)
        );

        CREATE TABLE code_reviews (
            review_id INTEGER PRIMARY KEY,
            pr_id INTEGER NOT NULL,
            reviewer_id INTEGER NOT NULL,
            verdict TEXT COLLATE NOCASE NOT NULL,
            FOREIGN KEY (pr_id) REFERENCES pull_requests(pr_id),
            FOREIGN KEY (reviewer_id) REFERENCES users(user_id)
        );

        CREATE TABLE ci_builds (
            build_id INTEGER PRIMARY KEY,
            commit_id INTEGER NOT NULL,
            workflow_name TEXT NOT NULL,
            status TEXT COLLATE NOCASE NOT NULL,
            duration_secs INTEGER NOT NULL,
            FOREIGN KEY (commit_id) REFERENCES commits(commit_id)
        );

        INSERT INTO organizations VALUES
            (1, 'DeepMind Core', 'Enterprise', 1500),
            (2, 'Anthropic Research', 'Enterprise', 850),
            (3, 'OpenAI Robotics', 'Enterprise', 1200);

        INSERT INTO users VALUES
            (101, 1, 'demis_h', 'Demis Hassabis', 'Admin'),
            (102, 1, 'pushmeet_k', 'Pushmeet Kohli', 'Maintainer'),
            (103, 1, 'koray_k', 'Koray Kavukcuoglu', 'Engineer'),
            (104, 2, 'dario_a', 'Dario Amodei', 'Admin'),
            (105, 3, 'wojciech_z', 'Wojciech Zaremba', 'Admin');

        INSERT INTO repositories VALUES
            (1, 1, 'alpha-tensor-v2', 'Python', 4500, 1),
            (2, 1, 'gemma-sql-pipeline', 'Rust', 1850, 0),
            (3, 2, 'claude-constitutional-eval', 'Python', 3200, 1),
            (4, 3, 'whisper-robotics-dsp', 'C++', 2700, 0);

        INSERT INTO branches VALUES
            (10, 1, 'main', 1),
            (11, 1, 'feature/sparse-attention', 0),
            (12, 2, 'main', 1),
            (13, 3, 'main', 1),
            (14, 4, 'main', 1);

        INSERT INTO commits VALUES
            (1001, 1, 102, 'Optimize tensor decomposition kernel', 340, 45, '2026-01-12'),
            (1002, 1, 103, 'Add fp16 benchmark suite', 120, 10, '2026-01-15'),
            (1003, 2, 101, 'Implement zero-copy AST parser in Rust', 580, 120, '2026-01-20'),
            (1004, 3, 104, 'Update safety red-team test harness', 210, 35, '2026-01-25'),
            (1005, 4, 105, 'Refactor low-latency audio stream buffer', 450, 95, '2026-02-01');

        INSERT INTO pull_requests VALUES
            (501, 1, 103, 'Sparse Attention Support', 'Merged', '2026-01-14'),
            (502, 2, 101, 'AST Rust Pipeline Integration', 'Merged', '2026-01-19'),
            (503, 3, 104, 'Constitutional Safety Checks v3', 'Merged', '2026-01-24'),
            (504, 4, 105, 'Low Latency DSP Audio Engine', 'Open', '2026-02-02');

        INSERT INTO code_reviews VALUES
            (1, 501, 102, 'Approved'),
            (2, 502, 102, 'Approved'),
            (3, 503, 104, 'Approved');

        INSERT INTO ci_builds VALUES
            (1, 1001, 'Continuous Integration / CUDA 13', 'Success', 145),
            (2, 1002, 'PyTorch Benchmark Runner', 'Success', 85),
            (3, 1003, 'Cargo Test & Clippy', 'Success', 65),
            (4, 1004, 'Red Team Safety Suite', 'Success', 310),
            (5, 1005, 'C++ Unit Tests', 'Running', 45);
    """)
    conn.commit()
    conn.close()
    print("[CREATED] software_dev_git_tracker.db (8 tables)")


if __name__ == "__main__":
    create_streaming_db()
    create_rideshare_db()
    create_real_estate_db()
    create_telecom_db()
    create_smart_energy_db()
    create_crypto_market_db()
    create_git_tracker_db()
    print("\nAll 7 new datasets successfully generated!")

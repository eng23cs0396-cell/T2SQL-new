"""
Creates 8 additional enterprise-grade relational SQLite databases across diverse domains:
1. gaming_esports_league.db (5 tables)
2. logistics_warehouse_inventory.db (6 tables)
3. healthcare_clinical_trials.db (5 tables)
4. fintech_insurance_claims.db (6 tables)
5. cloud_devops_infrastructure.db (7 tables)
6. restaurant_food_delivery.db (6 tables)
7. smart_city_transportation.db (6 tables)
8. digital_music_streaming.db (7 tables)
"""

import os
import sqlite3

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "databases")
os.makedirs(DATA_DIR, exist_ok=True)


def create_esports_db():
    db_path = os.path.join(DATA_DIR, "gaming_esports_league.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript("""
        DROP TABLE IF EXISTS player_stats;
        DROP TABLE IF EXISTS matches;
        DROP TABLE IF EXISTS tournaments;
        DROP TABLE IF EXISTS players;
        DROP TABLE IF EXISTS teams;

        CREATE TABLE teams (
            team_id INTEGER PRIMARY KEY,
            team_name TEXT NOT NULL COLLATE NOCASE,
            region TEXT NOT NULL COLLATE NOCASE,
            coach TEXT NOT NULL,
            founded_year INTEGER NOT NULL
        );

        CREATE TABLE players (
            player_id INTEGER PRIMARY KEY,
            team_id INTEGER NOT NULL,
            username TEXT NOT NULL COLLATE NOCASE,
            real_name TEXT NOT NULL,
            role TEXT NOT NULL COLLATE NOCASE,
            country TEXT NOT NULL COLLATE NOCASE,
            salary REAL NOT NULL,
            FOREIGN KEY (team_id) REFERENCES teams(team_id)
        );

        CREATE TABLE tournaments (
            tournament_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL COLLATE NOCASE,
            prize_pool REAL NOT NULL,
            tier TEXT NOT NULL COLLATE NOCASE,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL
        );

        CREATE TABLE matches (
            match_id INTEGER PRIMARY KEY,
            tournament_id INTEGER NOT NULL,
            team_a_id INTEGER NOT NULL,
            team_b_id INTEGER NOT NULL,
            winner_team_id INTEGER NOT NULL,
            match_date TEXT NOT NULL,
            duration_mins INTEGER NOT NULL,
            FOREIGN KEY (tournament_id) REFERENCES tournaments(tournament_id),
            FOREIGN KEY (team_a_id) REFERENCES teams(team_id),
            FOREIGN KEY (team_b_id) REFERENCES teams(team_id),
            FOREIGN KEY (winner_team_id) REFERENCES teams(team_id)
        );

        CREATE TABLE player_stats (
            stat_id INTEGER PRIMARY KEY,
            match_id INTEGER NOT NULL,
            player_id INTEGER NOT NULL,
            kills INTEGER NOT NULL,
            deaths INTEGER NOT NULL,
            assists INTEGER NOT NULL,
            damage_dealt INTEGER NOT NULL,
            FOREIGN KEY (match_id) REFERENCES matches(match_id),
            FOREIGN KEY (player_id) REFERENCES players(player_id)
        );

        INSERT INTO teams VALUES
            (1, 'Cloud9', 'North America', 'Reapered', 2013),
            (2, 'T1', 'Korea', 'KkOma', 2004),
            (3, 'G2 Esports', 'Europe', 'Dylan Falco', 2015),
            (4, 'EDward Gaming', 'China', 'KenZhu', 2013),
            (5, 'Fnatic', 'Europe', 'Nightshare', 2004);

        INSERT INTO players VALUES
            (101, 1, 'Blaber', 'Robert Huang', 'Jungler', 'USA', 280000.0),
            (102, 1, 'Fudge', 'Ibrahim Allami', 'Top', 'Australia', 240000.0),
            (103, 1, 'Berserker', 'Kim Min-cheol', 'ADC', 'Korea', 310000.0),
            (104, 2, 'Faker', 'Lee Sang-hyeok', 'Mid', 'Korea', 1500000.0),
            (105, 2, 'Gumayusi', 'Lee Min-hyeong', 'ADC', 'Korea', 450000.0),
            (106, 2, 'Zeus', 'Choi Woo-je', 'Top', 'Korea', 420000.0),
            (107, 3, 'Caps', 'Rasmus Winther', 'Mid', 'Denmark', 550000.0),
            (108, 3, 'BrokenBlade', 'Sergen Celik', 'Top', 'Germany', 320000.0),
            (109, 4, 'Meiko', 'Tian Ye', 'Support', 'China', 400000.0),
            (110, 5, 'Humanoid', 'Marek Brazda', 'Mid', 'Czech Republic', 380000.0);

        INSERT INTO tournaments VALUES
            (1, 'World Championship 2025', 2225000.0, 'S-Tier', '2025-10-01', '2025-11-05'),
            (2, 'Mid-Season Invitational 2025', 500000.0, 'A-Tier', '2025-05-10', '2025-05-28'),
            (3, 'Red Bull League of Its Own', 150000.0, 'B-Tier', '2025-12-15', '2025-12-18');

        INSERT INTO matches VALUES
            (1001, 1, 2, 3, 2, '2025-10-15', 38),
            (1002, 1, 1, 4, 4, '2025-10-16', 42),
            (1003, 1, 2, 4, 2, '2025-10-22', 45),
            (1004, 2, 3, 5, 3, '2025-05-12', 32),
            (1005, 2, 1, 2, 2, '2025-05-14', 36);

        INSERT INTO player_stats VALUES
            (1, 1001, 104, 7, 1, 9, 28500),
            (2, 1001, 105, 8, 2, 6, 31200),
            (3, 1001, 107, 3, 5, 4, 19400),
            (4, 1002, 101, 2, 4, 5, 14200),
            (5, 1002, 109, 1, 2, 14, 8500),
            (6, 1003, 104, 9, 0, 11, 34000),
            (7, 1003, 106, 5, 2, 8, 22400),
            (8, 1004, 107, 8, 1, 7, 29800),
            (9, 1004, 110, 4, 4, 3, 18500),
            (10, 1005, 104, 6, 2, 8, 26000);
    """)
    conn.commit()
    conn.close()
    print("Created gaming_esports_league.db (5 tables)")


def create_logistics_warehouse_db():
    db_path = os.path.join(DATA_DIR, "logistics_warehouse_inventory.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript("""
        DROP TABLE IF EXISTS outbound_orders;
        DROP TABLE IF EXISTS inbound_shipments;
        DROP TABLE IF EXISTS inventory_stock;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS storage_zones;
        DROP TABLE IF EXISTS warehouses;

        CREATE TABLE warehouses (
            warehouse_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL COLLATE NOCASE,
            city TEXT NOT NULL COLLATE NOCASE,
            state TEXT NOT NULL COLLATE NOCASE,
            total_capacity_sqft INTEGER NOT NULL,
            manager_name TEXT NOT NULL
        );

        CREATE TABLE storage_zones (
            zone_id INTEGER PRIMARY KEY,
            warehouse_id INTEGER NOT NULL,
            zone_code TEXT NOT NULL COLLATE NOCASE,
            temperature_type TEXT NOT NULL COLLATE NOCASE,
            rack_capacity INTEGER NOT NULL,
            FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)
        );

        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            sku TEXT UNIQUE NOT NULL COLLATE NOCASE,
            product_name TEXT NOT NULL COLLATE NOCASE,
            category TEXT NOT NULL COLLATE NOCASE,
            weight_kg REAL NOT NULL,
            unit_cost REAL NOT NULL
        );

        CREATE TABLE inventory_stock (
            stock_id INTEGER PRIMARY KEY,
            zone_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity_on_hand INTEGER NOT NULL,
            reorder_level INTEGER NOT NULL,
            FOREIGN KEY (zone_id) REFERENCES storage_zones(zone_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );

        CREATE TABLE inbound_shipments (
            shipment_id INTEGER PRIMARY KEY,
            warehouse_id INTEGER NOT NULL,
            supplier_name TEXT NOT NULL COLLATE NOCASE,
            received_date TEXT NOT NULL,
            total_pallets INTEGER NOT NULL,
            status TEXT NOT NULL COLLATE NOCASE,
            FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)
        );

        CREATE TABLE outbound_orders (
            order_id INTEGER PRIMARY KEY,
            warehouse_id INTEGER NOT NULL,
            destination_city TEXT NOT NULL COLLATE NOCASE,
            carrier TEXT NOT NULL COLLATE NOCASE,
            shipped_date TEXT NOT NULL,
            tracking_num TEXT NOT NULL,
            status TEXT NOT NULL COLLATE NOCASE,
            FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)
        );

        INSERT INTO warehouses VALUES
            (1, 'Midwest Logistics Hub', 'Chicago', 'IL', 250000, 'Marcus Vance'),
            (2, 'Pacific Gateway Facility', 'Seattle', 'WA', 180000, 'Elena Ramos'),
            (3, 'Lone Star Distribution', 'Dallas', 'TX', 320000, 'David Sterling'),
            (4, 'Sunbelt Center', 'Atlanta', 'GA', 210000, 'Chloe Bennett');

        INSERT INTO storage_zones VALUES
            (10, 1, 'Z-AMB-01', 'Ambient', 1200),
            (11, 1, 'Z-COLD-01', 'Refrigerated', 400),
            (12, 2, 'Z-AMB-02', 'Ambient', 950),
            (13, 2, 'Z-FRZ-01', 'Deep Freeze', 300),
            (14, 3, 'Z-AMB-03', 'Ambient', 1600),
            (15, 4, 'Z-AMB-04', 'Ambient', 1050);

        INSERT INTO products VALUES
            (501, 'SKU-ELEC-01', '4K Ultra HD Monitor', 'Electronics', 6.5, 210.0),
            (502, 'SKU-ELEC-02', 'Wireless Mechanical Keyboard', 'Electronics', 1.1, 45.0),
            (503, 'SKU-FOOD-01', 'Organic Cold Brew 12-Pack', 'Beverages', 4.8, 18.5),
            (504, 'SKU-FOOD-02', 'Artisan Cheddar Wheel', 'Perishables', 3.2, 24.0),
            (505, 'SKU-HOME-01', 'Ergonomic Desk Chair', 'Furniture', 18.0, 115.0),
            (506, 'SKU-MED-01', 'Vaccine Cold Storage Vial', 'Pharmaceuticals', 0.2, 85.0);

        INSERT INTO inventory_stock VALUES
            (1, 10, 501, 140, 50),
            (2, 10, 502, 380, 100),
            (3, 11, 504, 65, 80),
            (4, 12, 501, 85, 40),
            (5, 13, 506, 420, 150),
            (6, 14, 505, 95, 30),
            (7, 14, 502, 250, 75),
            (8, 15, 503, 520, 200);

        INSERT INTO inbound_shipments VALUES
            (201, 1, 'Apex Electronics Co.', '2026-02-10', 24, 'Completed'),
            (202, 1, 'Dairy Valley Farms', '2026-02-14', 12, 'Completed'),
            (203, 2, 'Global BioPharma Corp', '2026-02-16', 8, 'Processing'),
            (204, 3, 'Comfort Seat Makers', '2026-02-18', 30, 'Completed'),
            (205, 4, 'Green Mountain Roasters', '2026-02-20', 16, 'In Transit');

        INSERT INTO outbound_orders VALUES
            (301, 1, 'Detroit', 'FedEx', '2026-02-12', 'FX-99210-A', 'Delivered'),
            (302, 1, 'Milwaukee', 'UPS', '2026-02-15', 'UP-44102-B', 'Delivered'),
            (303, 2, 'Portland', 'DHL', '2026-02-17', 'DH-33019-C', 'Shipped'),
            (304, 3, 'Austin', 'FedEx', '2026-02-19', 'FX-77821-D', 'Delivered'),
            (305, 4, 'Charlotte', 'UPS', '2026-02-21', 'UP-55612-E', 'In Transit');
    """)
    conn.commit()
    conn.close()
    print("Created logistics_warehouse_inventory.db (6 tables)")


def create_clinical_trials_db():
    db_path = os.path.join(DATA_DIR, "healthcare_clinical_trials.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript("""
        DROP TABLE IF EXISTS patient_enrollments;
        DROP TABLE IF EXISTS trial_sites;
        DROP TABLE IF EXISTS investigational_drugs;
        DROP TABLE IF EXISTS clinical_studies;
        DROP TABLE IF EXISTS sponsors;

        CREATE TABLE sponsors (
            sponsor_id INTEGER PRIMARY KEY,
            company_name TEXT NOT NULL COLLATE NOCASE,
            headquarters TEXT NOT NULL COLLATE NOCASE,
            sponsor_type TEXT NOT NULL COLLATE NOCASE
        );

        CREATE TABLE clinical_studies (
            study_id INTEGER PRIMARY KEY,
            nct_number TEXT UNIQUE NOT NULL COLLATE NOCASE,
            sponsor_id INTEGER NOT NULL,
            title TEXT NOT NULL COLLATE NOCASE,
            phase TEXT NOT NULL COLLATE NOCASE,
            disease_indication TEXT NOT NULL COLLATE NOCASE,
            target_enrollment INTEGER NOT NULL,
            status TEXT NOT NULL COLLATE NOCASE,
            FOREIGN KEY (sponsor_id) REFERENCES sponsors(sponsor_id)
        );

        CREATE TABLE investigational_drugs (
            drug_id INTEGER PRIMARY KEY,
            study_id INTEGER NOT NULL,
            compound_code TEXT NOT NULL COLLATE NOCASE,
            generic_name TEXT NOT NULL COLLATE NOCASE,
            mechanism_of_action TEXT NOT NULL COLLATE NOCASE,
            dosage_form TEXT NOT NULL COLLATE NOCASE,
            FOREIGN KEY (study_id) REFERENCES clinical_studies(study_id)
        );

        CREATE TABLE trial_sites (
            site_id INTEGER PRIMARY KEY,
            study_id INTEGER NOT NULL,
            hospital_name TEXT NOT NULL COLLATE NOCASE,
            city TEXT NOT NULL COLLATE NOCASE,
            country TEXT NOT NULL COLLATE NOCASE,
            principal_investigator TEXT NOT NULL,
            FOREIGN KEY (study_id) REFERENCES clinical_studies(study_id)
        );

        CREATE TABLE patient_enrollments (
            enrollment_id INTEGER PRIMARY KEY,
            site_id INTEGER NOT NULL,
            patient_anon_id TEXT UNIQUE NOT NULL COLLATE NOCASE,
            enrollment_date TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL COLLATE NOCASE,
            completion_status TEXT NOT NULL COLLATE NOCASE,
            adverse_event_flag INTEGER NOT NULL,
            FOREIGN KEY (site_id) REFERENCES trial_sites(site_id)
        );

        INSERT INTO sponsors VALUES
            (1, 'Pfizer Oncology', 'New York, NY', 'Pharmaceutical'),
            (2, 'Novartis Institutes', 'Basel, Switzerland', 'Biotechnology'),
            (3, 'Johns Hopkins Medicine', 'Baltimore, MD', 'Academic Medical Center'),
            (4, 'Genentech Bio', 'South San Francisco, CA', 'Biotechnology');

        INSERT INTO clinical_studies VALUES
            (101, 'NCT05510101', 1, 'Evaluation of CDK4/6 Inhibitor in HER2+ Breast Cancer', 'Phase III', 'Breast Cancer', 450, 'Recruiting'),
            (102, 'NCT05520202', 1, 'Novel Immunotherapy for Refractory Melanoma', 'Phase II', 'Melanoma', 120, 'Active'),
            (103, 'NCT05530303', 2, 'CAR-T Cell Therapy in Relapsed Multiple Myeloma', 'Phase II', 'Multiple Myeloma', 80, 'Recruiting'),
            (104, 'NCT05540404', 3, 'Biomarker-Guided Treatment for Glioblastoma', 'Phase I', 'Glioblastoma', 40, 'Completed'),
            (105, 'NCT05550505', 4, 'Bispecific Antibody in B-cell Non-Hodgkin Lymphoma', 'Phase III', 'Lymphoma', 300, 'Active');

        INSERT INTO investigational_drugs VALUES
            (1, 101, 'PF-07220063', 'Palbociclib Derivative', 'CDK4/6 Kinase Inhibitor', 'Oral Tablet'),
            (2, 102, 'PF-06801591', 'Sasanlimab', 'PD-1 Monoclonal Antibody', 'Intravenous Infusion'),
            (3, 103, 'NVS-CART-99', 'Tisagenlecleucel NextGen', 'CAR-T Cell Therapy', 'Autologous Cell Infusion'),
            (4, 104, 'JHM-GLIO-04', 'Temozolomide Synergist', 'DNA Alkylating Enhancer', 'Oral Capsule'),
            (5, 105, 'GEN-BSAB-12', 'Mosunetuzumab Plus', 'CD20xCD3 T-Cell Engager', 'Subcutaneous Injection');

        INSERT INTO trial_sites VALUES
            (501, 101, 'Memorial Sloan Kettering Cancer Center', 'New York', 'USA', 'Dr. Lisa Callahan'),
            (502, 101, 'MD Anderson Cancer Center', 'Houston', 'USA', 'Dr. Robert Chen'),
            (503, 102, 'Dana-Farber Cancer Institute', 'Boston', 'USA', 'Dr. Angela Rossi'),
            (504, 103, 'Charite Universitatsmedizin', 'Berlin', 'Germany', 'Dr. Hans Gruber'),
            (505, 104, 'Johns Hopkins Hospital', 'Baltimore', 'USA', 'Dr. Victor Frank'),
            (506, 105, 'Mayo Clinic Comprehensive Center', 'Rochester', 'USA', 'Dr. Sarah Sterling');

        INSERT INTO patient_enrollments VALUES
            (1, 501, 'PT-1001', '2025-01-15', 54, 'Female', 'Completed', 0),
            (2, 501, 'PT-1002', '2025-01-20', 62, 'Female', 'Active', 0),
            (3, 501, 'PT-1003', '2025-02-01', 49, 'Female', 'Withdrawn', 1),
            (4, 502, 'PT-1004', '2025-01-18', 58, 'Female', 'Active', 0),
            (5, 502, 'PT-1005', '2025-02-05', 66, 'Female', 'Completed', 0),
            (6, 503, 'PT-2001', '2025-03-01', 51, 'Male', 'Active', 1),
            (7, 503, 'PT-2002', '2025-03-10', 44, 'Female', 'Active', 0),
            (8, 504, 'PT-3001', '2025-02-12', 68, 'Male', 'Active', 0),
            (9, 505, 'PT-4001', '2024-06-10', 55, 'Male', 'Completed', 0),
            (10, 506, 'PT-5001', '2025-01-05', 60, 'Male', 'Completed', 0);
    """)
    conn.commit()
    conn.close()
    print("Created healthcare_clinical_trials.db (5 tables)")


def create_insurance_claims_db():
    db_path = os.path.join(DATA_DIR, "fintech_insurance_claims.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript("""
        DROP TABLE IF EXISTS claim_payments;
        DROP TABLE IF EXISTS claims;
        DROP TABLE IF EXISTS adjusters;
        DROP TABLE IF EXISTS insured_assets;
        DROP TABLE IF EXISTS insurance_policies;
        DROP TABLE IF EXISTS policyholders;

        CREATE TABLE policyholders (
            policyholder_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            credit_tier TEXT NOT NULL COLLATE NOCASE,
            city TEXT NOT NULL COLLATE NOCASE,
            state TEXT NOT NULL COLLATE NOCASE
        );

        CREATE TABLE insurance_policies (
            policy_id INTEGER PRIMARY KEY,
            policyholder_id INTEGER NOT NULL,
            policy_type TEXT NOT NULL COLLATE NOCASE,
            coverage_limit REAL NOT NULL,
            deductible REAL NOT NULL,
            premium_annual REAL NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            status TEXT NOT NULL COLLATE NOCASE,
            FOREIGN KEY (policyholder_id) REFERENCES policyholders(policyholder_id)
        );

        CREATE TABLE insured_assets (
            asset_id INTEGER PRIMARY KEY,
            policy_id INTEGER NOT NULL,
            asset_type TEXT NOT NULL COLLATE NOCASE,
            asset_identifier TEXT NOT NULL COLLATE NOCASE,
            estimated_value REAL NOT NULL,
            FOREIGN KEY (policy_id) REFERENCES insurance_policies(policy_id)
        );

        CREATE TABLE adjusters (
            adjuster_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            license_state TEXT NOT NULL COLLATE NOCASE,
            experience_years INTEGER NOT NULL,
            open_cases_count INTEGER NOT NULL
        );

        CREATE TABLE claims (
            claim_id INTEGER PRIMARY KEY,
            policy_id INTEGER NOT NULL,
            adjuster_id INTEGER NOT NULL,
            incident_date TEXT NOT NULL,
            file_date TEXT NOT NULL,
            claim_amount REAL NOT NULL,
            settlement_amount REAL NOT NULL,
            status TEXT NOT NULL COLLATE NOCASE,
            FOREIGN KEY (policy_id) REFERENCES insurance_policies(policy_id),
            FOREIGN KEY (adjuster_id) REFERENCES adjusters(adjuster_id)
        );

        CREATE TABLE claim_payments (
            payment_id INTEGER PRIMARY KEY,
            claim_id INTEGER NOT NULL,
            payment_date TEXT NOT NULL,
            amount REAL NOT NULL,
            payment_method TEXT NOT NULL COLLATE NOCASE,
            FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
        );

        INSERT INTO policyholders VALUES
            (1, 'Anthony', 'Scaramucci', 'anthony.s@example.com', 'Excellent', 'Miami', 'FL'),
            (2, 'Brenda', 'Callahan', 'brenda.c@example.com', 'Good', 'Austin', 'TX'),
            (3, 'Carlos', 'Santana', 'carlos.s@example.com', 'Excellent', 'San Francisco', 'CA'),
            (4, 'Danielle', 'Rousseau', 'danielle.r@example.com', 'Fair', 'Seattle', 'WA'),
            (5, 'Ethan', 'Hunt', 'ethan.h@example.com', 'Good', 'Chicago', 'IL');

        INSERT INTO insurance_policies VALUES
            (101, 1, 'Commercial Auto', 500000.0, 2500.0, 4800.0, '2025-01-01', '2026-01-01', 'Active'),
            (102, 1, 'Property & Casualty', 1200000.0, 5000.0, 7200.0, '2025-03-01', '2026-03-01', 'Active'),
            (103, 2, 'Homeowners', 450000.0, 1500.0, 2100.0, '2025-02-15', '2026-02-15', 'Active'),
            (104, 3, 'Comprehensive Auto', 100000.0, 1000.0, 1850.0, '2024-11-01', '2025-11-01', 'Expired'),
            (105, 4, 'Cyber Liability', 2000000.0, 10000.0, 12500.0, '2025-05-01', '2026-05-01', 'Active'),
            (106, 5, 'Commercial Auto', 750000.0, 3000.0, 5600.0, '2025-06-01', '2026-06-01', 'Active');

        INSERT INTO insured_assets VALUES
            (201, 101, 'Vehicle Fleet', 'VIN-8829104A', 145000.0),
            (202, 102, 'Commercial Warehouse', 'PROP-MIAMI-44', 1100000.0),
            (203, 103, 'Single Family Home', 'PROP-AUSTIN-12', 420000.0),
            (204, 104, 'Luxury Sedan', 'VIN-1194827B', 85000.0),
            (205, 105, 'Cloud Infrastructure Data', 'CYBER-SRV-01', 1800000.0),
            (206, 106, 'Armored Transport Van', 'VIN-4482019C', 210000.0);

        INSERT INTO adjusters VALUES
            (11, 'Samantha Cruz', 'FL', 8, 4),
            (12, 'Gregory Peck', 'TX', 15, 2),
            (13, 'Nancy Wheeler', 'CA', 6, 5),
            (14, 'Bradley Cooper', 'WA', 11, 3);

        INSERT INTO claims VALUES
            (1001, 101, 11, '2025-04-10', '2025-04-12', 18500.0, 16000.0, 'Approved'),
            (1002, 102, 11, '2025-08-20', '2025-08-22', 45000.0, 42500.0, 'Approved'),
            (1003, 103, 12, '2025-06-15', '2025-06-18', 12000.0, 9500.0, 'Approved'),
            (1004, 104, 13, '2025-01-08', '2025-01-10', 8200.0, 0.0, 'Rejected'),
            (1005, 105, 14, '2025-09-03', '2025-09-05', 125000.0, 110000.0, 'In Review'),
            (1006, 106, 11, '2025-10-14', '2025-10-15', 28000.0, 25000.0, 'Approved');

        INSERT INTO claim_payments VALUES
            (1, 1001, '2025-04-28', 16000.0, 'Direct Deposit'),
            (2, 1002, '2025-09-10', 25000.0, 'Wire Transfer'),
            (3, 1002, '2025-09-25', 17500.0, 'Wire Transfer'),
            (4, 1003, '2025-07-02', 9500.0, 'Check'),
            (5, 1006, '2025-11-01', 25000.0, 'Direct Deposit');
    """)
    conn.commit()
    conn.close()
    print("Created fintech_insurance_claims.db (6 tables)")


def create_cloud_devops_db():
    db_path = os.path.join(DATA_DIR, "cloud_devops_infrastructure.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript("""
        DROP TABLE IF EXISTS deploy_logs;
        DROP TABLE IF EXISTS cloud_costs;
        DROP TABLE IF EXISTS incident_alerts;
        DROP TABLE IF EXISTS deployments;
        DROP TABLE IF EXISTS nodes;
        DROP TABLE IF EXISTS compute_clusters;
        DROP TABLE IF EXISTS cloud_projects;

        CREATE TABLE cloud_projects (
            project_id INTEGER PRIMARY KEY,
            project_name TEXT UNIQUE NOT NULL COLLATE NOCASE,
            owner_email TEXT NOT NULL,
            billing_account TEXT NOT NULL COLLATE NOCASE,
            environment TEXT NOT NULL COLLATE NOCASE,
            monthly_budget REAL NOT NULL
        );

        CREATE TABLE compute_clusters (
            cluster_id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL,
            cluster_name TEXT NOT NULL COLLATE NOCASE,
            cloud_region TEXT NOT NULL COLLATE NOCASE,
            k8s_version TEXT NOT NULL,
            node_count INTEGER NOT NULL,
            status TEXT NOT NULL COLLATE NOCASE,
            FOREIGN KEY (project_id) REFERENCES cloud_projects(project_id)
        );

        CREATE TABLE nodes (
            node_id INTEGER PRIMARY KEY,
            cluster_id INTEGER NOT NULL,
            instance_type TEXT NOT NULL COLLATE NOCASE,
            vcpu INTEGER NOT NULL,
            ram_gb INTEGER NOT NULL,
            ip_address TEXT NOT NULL,
            status TEXT NOT NULL COLLATE NOCASE,
            FOREIGN KEY (cluster_id) REFERENCES compute_clusters(cluster_id)
        );

        CREATE TABLE deployments (
            deployment_id INTEGER PRIMARY KEY,
            cluster_id INTEGER NOT NULL,
            app_name TEXT NOT NULL COLLATE NOCASE,
            image_tag TEXT NOT NULL,
            replicas_target INTEGER NOT NULL,
            replicas_healthy INTEGER NOT NULL,
            cpu_request_cores REAL NOT NULL,
            FOREIGN KEY (cluster_id) REFERENCES compute_clusters(cluster_id)
        );

        CREATE TABLE incident_alerts (
            alert_id INTEGER PRIMARY KEY,
            cluster_id INTEGER NOT NULL,
            severity TEXT NOT NULL COLLATE NOCASE,
            alert_name TEXT NOT NULL COLLATE NOCASE,
            triggered_at TEXT NOT NULL,
            resolved_at TEXT,
            acknowledged INTEGER NOT NULL,
            FOREIGN KEY (cluster_id) REFERENCES compute_clusters(cluster_id)
        );

        CREATE TABLE cloud_costs (
            cost_id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL,
            service_name TEXT NOT NULL COLLATE NOCASE,
            billing_month TEXT NOT NULL,
            amount_usd REAL NOT NULL,
            FOREIGN KEY (project_id) REFERENCES cloud_projects(project_id)
        );

        CREATE TABLE deploy_logs (
            log_id INTEGER PRIMARY KEY,
            deployment_id INTEGER NOT NULL,
            commit_hash TEXT NOT NULL,
            deployed_by TEXT NOT NULL,
            deployment_status TEXT NOT NULL COLLATE NOCASE,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (deployment_id) REFERENCES deployments(deployment_id)
        );

        INSERT INTO cloud_projects VALUES
            (1, 't2sql-production', 'lead-architect@t2sql.io', 'BA-99120', 'Production', 15000.0),
            (2, 't2sql-staging', 'qa-team@t2sql.io', 'BA-99120', 'Staging', 5000.0),
            (3, 't2sql-data-lakehouse', 'data-eng@t2sql.io', 'BA-88410', 'Production', 25000.0),
            (4, 'internal-tooling', 'devops@t2sql.io', 'BA-11029', 'Development', 3000.0);

        INSERT INTO compute_clusters VALUES
            (10, 1, 'prod-us-east-cluster', 'us-east-1', 'v1.30.2', 12, 'Running'),
            (11, 1, 'prod-eu-central-cluster', 'eu-central-1', 'v1.30.2', 8, 'Running'),
            (12, 2, 'stg-us-east-cluster', 'us-east-1', 'v1.31.0', 4, 'Running'),
            (13, 3, 'data-proc-spark-cluster', 'us-central1', 'v1.29.4', 24, 'Running'),
            (14, 4, 'dev-sandbox-cluster', 'us-west-2', 'v1.31.0', 2, 'Stopped');

        INSERT INTO nodes VALUES
            (101, 10, 'c6i.4xlarge', 16, 32, '10.0.1.14', 'Ready'),
            (102, 10, 'c6i.4xlarge', 16, 32, '10.0.1.15', 'Ready'),
            (103, 10, 'm6i.8xlarge', 32, 128, '10.0.1.20', 'Ready'),
            (104, 11, 'c6i.4xlarge', 16, 32, '10.1.1.8', 'Ready'),
            (105, 12, 't4g.xlarge', 4, 16, '10.2.1.5', 'Ready'),
            (106, 13, 'r6i.16xlarge', 64, 512, '10.3.1.50', 'Ready'),
            (107, 13, 'r6i.16xlarge', 64, 512, '10.3.1.51', 'Ready');

        INSERT INTO deployments VALUES
            (501, 10, 't2sql-fastapi-backend', 'v2.4.1', 6, 6, 4.0),
            (502, 10, 't2sql-react-frontend', 'v2.4.1', 4, 4, 1.0),
            (503, 10, 'qwen-inference-service', 'v1.2.0', 2, 2, 16.0),
            (504, 11, 't2sql-fastapi-backend', 'v2.4.0', 4, 4, 4.0),
            (505, 12, 't2sql-fastapi-backend', 'v2.5.0-rc1', 2, 2, 2.0),
            (506, 13, 'spark-job-executor', 'v3.5.1', 8, 8, 32.0);

        INSERT INTO incident_alerts VALUES
            (1, 10, 'Warning', 'HighMemoryUsage', '2026-02-18 14:22:00', '2026-02-18 14:45:00', 1),
            (2, 10, 'Critical', 'PodCrashLoopBackOff', '2026-02-19 09:12:00', '2026-02-19 09:30:00', 1),
            (3, 11, 'Critical', 'NetworkPacketLoss', '2026-02-20 18:05:00', NULL, 0),
            (4, 13, 'Warning', 'DiskSpaceLow', '2026-02-21 03:15:00', '2026-02-21 04:00:00', 1);

        INSERT INTO cloud_costs VALUES
            (1, 1, 'Amazon Elastic Kubernetes Service', '2026-01', 6800.0),
            (2, 1, 'Elastic Load Balancing & NAT Gateway', '2026-01', 2400.0),
            (3, 2, 'Amazon Elastic Kubernetes Service', '2026-01', 2800.0),
            (4, 3, 'Google Cloud Dataproc', '2026-01', 14500.0),
            (5, 3, 'Cloud Storage Lakehouse', '2026-01', 7200.0),
            (6, 4, 'AWS EC2 Dev Instances', '2026-01', 1100.0);

        INSERT INTO deploy_logs VALUES
            (1, 501, 'a1f89c2', 'alex.devops@t2sql.io', 'Success', '2026-02-15 11:30:00'),
            (2, 502, '98b044d', 'claire.ui@t2sql.io', 'Success', '2026-02-15 12:00:00'),
            (3, 503, '7e2c91a', 'ai-team@t2sql.io', 'Success', '2026-02-16 16:45:00'),
            (4, 505, '12d88bb', 'alex.devops@t2sql.io', 'Success', '2026-02-17 10:15:00');
    """)
    conn.commit()
    conn.close()
    print("Created cloud_devops_infrastructure.db (7 tables)")


def create_food_delivery_db():
    db_path = os.path.join(DATA_DIR, "restaurant_food_delivery.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript("""
        DROP TABLE IF EXISTS order_items;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS customers;
        DROP TABLE IF EXISTS delivery_drivers;
        DROP TABLE IF EXISTS menu_items;
        DROP TABLE IF EXISTS restaurants;

        CREATE TABLE restaurants (
            restaurant_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL COLLATE NOCASE,
            cuisine TEXT NOT NULL COLLATE NOCASE,
            rating REAL NOT NULL,
            delivery_fee REAL NOT NULL,
            min_order REAL NOT NULL,
            is_active INTEGER NOT NULL
        );

        CREATE TABLE menu_items (
            item_id INTEGER PRIMARY KEY,
            restaurant_id INTEGER NOT NULL,
            name TEXT NOT NULL COLLATE NOCASE,
            category TEXT NOT NULL COLLATE NOCASE,
            price REAL NOT NULL,
            is_available INTEGER NOT NULL,
            FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
        );

        CREATE TABLE delivery_drivers (
            driver_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            vehicle_type TEXT NOT NULL COLLATE NOCASE,
            rating REAL NOT NULL,
            total_deliveries INTEGER NOT NULL,
            status TEXT NOT NULL COLLATE NOCASE
        );

        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            city TEXT NOT NULL COLLATE NOCASE,
            membership_tier TEXT NOT NULL COLLATE NOCASE,
            total_orders INTEGER NOT NULL
        );

        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            restaurant_id INTEGER NOT NULL,
            driver_id INTEGER NOT NULL,
            order_time TEXT NOT NULL,
            delivery_time TEXT,
            subtotal REAL NOT NULL,
            tip REAL NOT NULL,
            total_amount REAL NOT NULL,
            order_status TEXT NOT NULL COLLATE NOCASE,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id),
            FOREIGN KEY (driver_id) REFERENCES delivery_drivers(driver_id)
        );

        CREATE TABLE order_items (
            order_item_id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (item_id) REFERENCES menu_items(item_id)
        );

        INSERT INTO restaurants VALUES
            (1, 'Mario Pizzeria Trattoria', 'Italian', 4.8, 2.99, 15.0, 1),
            (2, 'Tokyo Express Ramen', 'Japanese', 4.7, 3.49, 12.0, 1),
            (3, 'Taco Fiesta Cantina', 'Mexican', 4.5, 1.99, 10.0, 1),
            (4, 'The Green Sprout Vegan', 'Vegan', 4.6, 3.99, 20.0, 1),
            (5, 'Bangkok Street Wok', 'Thai', 4.3, 2.49, 15.0, 1);

        INSERT INTO menu_items VALUES
            (101, 1, 'Truffle Mushroom Pizza', 'Mains', 18.5, 1),
            (102, 1, 'Classic Margherita', 'Mains', 14.0, 1),
            (103, 1, 'Tiramisu Classico', 'Dessert', 7.5, 1),
            (104, 2, 'Tonkotsu Ramen', 'Mains', 16.0, 1),
            (105, 2, 'Gyoza Dumplings (6pcs)', 'Appetizers', 8.0, 1),
            (106, 3, 'Carne Asada Street Tacos', 'Mains', 12.5, 1),
            (107, 3, 'Guacamole & Fresh Chips', 'Appetizers', 6.5, 1),
            (108, 4, 'Beyond Burger Deluxe', 'Mains', 15.5, 1),
            (109, 4, 'Avocado Kale Salad', 'Salads', 11.0, 1),
            (110, 5, 'Pad Thai with Shrimp', 'Mains', 15.0, 1);

        INSERT INTO delivery_drivers VALUES
            (201, 'Liam Walker', 'Bicycle', 4.9, 1420, 'Available'),
            (202, 'Sophia Martinez', 'Scooter', 4.8, 980, 'Busy'),
            (203, 'James Chen', 'Electric Car', 4.95, 2150, 'Available'),
            (204, 'Lucas Silva', 'Motorcycle', 4.7, 630, 'Offline');

        INSERT INTO customers VALUES
            (301, 'Emma Watson', 'Downtown', 'Gold', 42),
            (302, 'Noah Davis', 'North Side', 'Platinum', 88),
            (303, 'Olivia Taylor', 'Uptown', 'Standard', 14),
            (304, 'William Anderson', 'Downtown', 'Gold', 35),
            (305, 'Ava Thomas', 'West End', 'Standard', 8);

        INSERT INTO orders VALUES
            (1001, 301, 1, 201, '2026-02-21 18:30:00', '2026-02-21 19:05:00', 26.0, 5.0, 33.99, 'Delivered'),
            (1002, 302, 2, 202, '2026-02-21 19:00:00', '2026-02-21 19:38:00', 24.0, 4.5, 31.99, 'Delivered'),
            (1003, 303, 3, 203, '2026-02-21 19:15:00', '2026-02-21 19:42:00', 19.0, 3.0, 23.99, 'Delivered'),
            (1004, 304, 4, 201, '2026-02-21 20:00:00', '2026-02-21 20:35:00', 26.5, 6.0, 36.49, 'Delivered'),
            (1005, 305, 5, 202, '2026-02-21 20:10:00', NULL, 15.0, 3.0, 20.49, 'Out For Delivery');

        INSERT INTO order_items VALUES
            (1, 1001, 101, 1, 18.5),
            (2, 1001, 103, 1, 7.5),
            (3, 1002, 104, 1, 16.0),
            (4, 1002, 105, 1, 8.0),
            (5, 1003, 106, 1, 12.5),
            (6, 1003, 107, 1, 6.5),
            (7, 1004, 108, 1, 15.5),
            (8, 1004, 109, 1, 11.0),
            (9, 1005, 110, 1, 15.0);
    """)
    conn.commit()
    conn.close()
    print("Created restaurant_food_delivery.db (6 tables)")


def create_smart_city_transit_db():
    db_path = os.path.join(DATA_DIR, "smart_city_transportation.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript("""
        DROP TABLE IF EXISTS daily_ridership;
        DROP TABLE IF EXISTS transit_vehicles;
        DROP TABLE IF EXISTS route_stops;
        DROP TABLE IF EXISTS stations;
        DROP TABLE IF EXISTS transit_routes;
        DROP TABLE IF EXISTS transit_agencies;

        CREATE TABLE transit_agencies (
            agency_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL COLLATE NOCASE,
            city TEXT NOT NULL COLLATE NOCASE,
            fleet_size INTEGER NOT NULL,
            fare_type TEXT NOT NULL COLLATE NOCASE
        );

        CREATE TABLE transit_routes (
            route_id INTEGER PRIMARY KEY,
            agency_id INTEGER NOT NULL,
            route_number TEXT NOT NULL COLLATE NOCASE,
            route_name TEXT NOT NULL COLLATE NOCASE,
            route_type TEXT NOT NULL COLLATE NOCASE,
            headway_mins INTEGER NOT NULL,
            FOREIGN KEY (agency_id) REFERENCES transit_agencies(agency_id)
        );

        CREATE TABLE stations (
            station_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL COLLATE NOCASE,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            zone INTEGER NOT NULL,
            wheelchair_accessible INTEGER NOT NULL
        );

        CREATE TABLE route_stops (
            stop_id INTEGER PRIMARY KEY,
            route_id INTEGER NOT NULL,
            station_id INTEGER NOT NULL,
            stop_sequence INTEGER NOT NULL,
            is_express_stop INTEGER NOT NULL,
            FOREIGN KEY (route_id) REFERENCES transit_routes(route_id),
            FOREIGN KEY (station_id) REFERENCES stations(station_id)
        );

        CREATE TABLE transit_vehicles (
            vehicle_id INTEGER PRIMARY KEY,
            route_id INTEGER NOT NULL,
            vehicle_type TEXT NOT NULL COLLATE NOCASE,
            model_year INTEGER NOT NULL,
            fuel_type TEXT NOT NULL COLLATE NOCASE,
            passenger_capacity INTEGER NOT NULL,
            status TEXT NOT NULL COLLATE NOCASE,
            FOREIGN KEY (route_id) REFERENCES transit_routes(route_id)
        );

        CREATE TABLE daily_ridership (
            ridership_id INTEGER PRIMARY KEY,
            station_id INTEGER NOT NULL,
            service_date TEXT NOT NULL,
            entries_count INTEGER NOT NULL,
            exits_count INTEGER NOT NULL,
            FOREIGN KEY (station_id) REFERENCES stations(station_id)
        );

        INSERT INTO transit_agencies VALUES
            (1, 'Metropolitan Area Transit Authority', 'Metro City', 650, 'SmartCard / Contactless'),
            (2, 'Bay Regional Express Rail', 'Coastal Bay', 180, 'Distance-based Ticket'),
            (3, 'Valley Electric Trolley Corp', 'Sun Valley', 95, 'Flat Fare');

        INSERT INTO transit_routes VALUES
            (101, 1, 'Line 1', 'Blue Metro Line', 'Subway', 6),
            (102, 1, 'Line 2', 'Red Metro Line', 'Subway', 8),
            (103, 1, 'Bus 44', 'Crosstown Rapid Bus', 'BRT', 12),
            (104, 2, 'Coast-X', 'Pacific Coast Intercity Rail', 'Commuter Rail', 30),
            (105, 3, 'Trolley A', 'Downtown Heritage Loop', 'Light Rail', 10);

        INSERT INTO stations VALUES
            (1, 'Central Station Terminal', 40.7128, -74.0060, 1, 1),
            (2, 'Civic Center & University', 40.7180, -74.0110, 1, 1),
            (3, 'Innovation Tech Park', 40.7300, -73.9950, 2, 1),
            (4, 'Harborview Ferry Pier', 40.7010, -74.0150, 1, 1),
            (5, 'Oak Ridge Highlands', 40.7550, -73.9600, 3, 0);

        INSERT INTO route_stops VALUES
            (1, 101, 1, 1, 1),
            (2, 101, 2, 2, 0),
            (3, 101, 3, 3, 1),
            (4, 102, 1, 1, 1),
            (5, 102, 4, 2, 1),
            (6, 103, 2, 1, 0),
            (7, 103, 5, 2, 0),
            (8, 104, 1, 1, 1),
            (9, 104, 4, 2, 1);

        INSERT INTO transit_vehicles VALUES
            (501, 101, 'Six-Car Electric Trainset', 2022, 'Electric 750V DC', 840, 'In Service'),
            (502, 101, 'Six-Car Electric Trainset', 2024, 'Electric 750V DC', 880, 'In Service'),
            (503, 102, 'Six-Car Electric Trainset', 2019, 'Electric 750V DC', 800, 'Maintenance'),
            (504, 103, 'Articulated Low-Floor Bus', 2023, 'Battery Electric', 110, 'In Service'),
            (505, 104, 'Bi-Level Diesel-Electric Train', 2018, 'Diesel-Electric Hybrid', 620, 'In Service');

        INSERT INTO daily_ridership VALUES
            (1, 1, '2026-02-15', 48500, 46200),
            (2, 2, '2026-02-15', 24100, 23800),
            (3, 3, '2026-02-15', 18900, 19400),
            (4, 4, '2026-02-15', 12300, 11800),
            (5, 5, '2026-02-15', 5600, 5800),
            (6, 1, '2026-02-16', 51200, 49800),
            (7, 2, '2026-02-16', 26500, 25900);
    """)
    conn.commit()
    conn.close()
    print("Created smart_city_transportation.db (6 tables)")


def create_digital_music_db():
    db_path = os.path.join(DATA_DIR, "digital_music_streaming.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript("""
        DROP TABLE IF EXISTS track_royalties;
        DROP TABLE IF EXISTS playlist_tracks;
        DROP TABLE IF EXISTS playlists;
        DROP TABLE IF EXISTS tracks;
        DROP TABLE IF EXISTS albums;
        DROP TABLE IF EXISTS artists;
        DROP TABLE IF EXISTS record_labels;

        CREATE TABLE record_labels (
            label_id INTEGER PRIMARY KEY,
            label_name TEXT NOT NULL COLLATE NOCASE,
            country TEXT NOT NULL COLLATE NOCASE,
            distribution_partner TEXT NOT NULL
        );

        CREATE TABLE artists (
            artist_id INTEGER PRIMARY KEY,
            label_id INTEGER NOT NULL,
            stage_name TEXT NOT NULL COLLATE NOCASE,
            primary_genre TEXT NOT NULL COLLATE NOCASE,
            monthly_listeners INTEGER NOT NULL,
            country_origin TEXT NOT NULL COLLATE NOCASE,
            FOREIGN KEY (label_id) REFERENCES record_labels(label_id)
        );

        CREATE TABLE albums (
            album_id INTEGER PRIMARY KEY,
            artist_id INTEGER NOT NULL,
            title TEXT NOT NULL COLLATE NOCASE,
            release_year INTEGER NOT NULL,
            album_type TEXT NOT NULL COLLATE NOCASE,
            total_tracks INTEGER NOT NULL,
            FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
        );

        CREATE TABLE tracks (
            track_id INTEGER PRIMARY KEY,
            album_id INTEGER NOT NULL,
            track_number INTEGER NOT NULL,
            title TEXT NOT NULL COLLATE NOCASE,
            duration_seconds INTEGER NOT NULL,
            is_explicit INTEGER NOT NULL,
            stream_count INTEGER NOT NULL,
            FOREIGN KEY (album_id) REFERENCES albums(album_id)
        );

        CREATE TABLE playlists (
            playlist_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL COLLATE NOCASE,
            curator_type TEXT NOT NULL COLLATE NOCASE,
            followers_count INTEGER NOT NULL,
            is_public INTEGER NOT NULL
        );

        CREATE TABLE playlist_tracks (
            playlist_track_id INTEGER PRIMARY KEY,
            playlist_id INTEGER NOT NULL,
            track_id INTEGER NOT NULL,
            position INTEGER NOT NULL,
            FOREIGN KEY (playlist_id) REFERENCES playlists(playlist_id),
            FOREIGN KEY (track_id) REFERENCES tracks(track_id)
        );

        CREATE TABLE track_royalties (
            royalty_id INTEGER PRIMARY KEY,
            track_id INTEGER NOT NULL,
            calculation_period TEXT NOT NULL,
            total_plays INTEGER NOT NULL,
            royalty_payout_usd REAL NOT NULL,
            FOREIGN KEY (track_id) REFERENCES tracks(track_id)
        );

        INSERT INTO record_labels VALUES
            (1, 'Interscope Records', 'USA', 'Universal Music Group'),
            (2, 'Columbia Records', 'USA', 'Sony Music Entertainment'),
            (3, 'Atlantic Records', 'USA', 'Warner Music Group'),
            (4, 'XL Recordings', 'UK', 'Beggars Group');

        INSERT INTO artists VALUES
            (101, 1, 'Billie Eilish', 'Pop', 68000000, 'USA'),
            (102, 1, 'Kendrick Lamar', 'Hip-Hop', 59000000, 'USA'),
            (103, 2, 'Beyonce', 'R&B', 62000000, 'USA'),
            (104, 3, 'Ed Sheeran', 'Pop', 74000000, 'UK'),
            (105, 4, 'Radiohead', 'Alternative Rock', 24000000, 'UK'),
            (106, 4, 'Adele', 'Pop', 51000000, 'UK');

        INSERT INTO albums VALUES
            (201, 101, 'Hit Me Hard and Soft', 2024, 'Studio Album', 10),
            (202, 102, 'DAMN.', 2017, 'Studio Album', 14),
            (203, 103, 'Renaissance', 2022, 'Studio Album', 16),
            (204, 104, 'Divide', 2017, 'Studio Album', 16),
            (205, 105, 'OK Computer', 1997, 'Studio Album', 12);

        INSERT INTO tracks VALUES
            (301, 201, 1, 'Skinny', 219, 0, 185000000),
            (302, 201, 2, 'Lunch', 179, 1, 490000000),
            (303, 201, 3, 'Chihiro', 303, 0, 310000000),
            (304, 202, 2, 'DNA.', 185, 1, 1250000000),
            (305, 202, 8, 'HUMBLE.', 177, 1, 2150000000),
            (306, 203, 3, 'Alien Superstar', 215, 1, 340000000),
            (307, 203, 4, 'Cuff It', 225, 0, 680000000),
            (308, 204, 4, 'Shape of You', 233, 0, 3600000000),
            (309, 205, 1, 'Airbag', 284, 0, 95000000),
            (310, 205, 2, 'Paranoid Android', 387, 0, 180000000);

        INSERT INTO playlists VALUES
            (1, 'Today Top Hits', 'Editorial', 34500000, 1),
            (2, 'RapCaviar', 'Editorial', 15800000, 1),
            (3, 'Rock Classics & Anthems', 'Editorial', 8900000, 1),
            (4, 'Chill Vibes Evening', 'User Curated', 420000, 1);

        INSERT INTO playlist_tracks VALUES
            (1, 1, 302, 1),
            (2, 1, 307, 2),
            (3, 1, 308, 3),
            (4, 2, 304, 1),
            (5, 2, 305, 2),
            (6, 3, 309, 1),
            (7, 3, 310, 2),
            (8, 4, 301, 1),
            (9, 4, 303, 2);

        INSERT INTO track_royalties VALUES
            (1, 302, '2025-Q4', 120000000, 480000.0),
            (2, 305, '2025-Q4', 95000000, 380000.0),
            (3, 307, '2025-Q4', 80000000, 320000.0),
            (4, 308, '2025-Q4', 150000000, 600000.0);
    """)
    conn.commit()
    conn.close()
    print("Created digital_music_streaming.db (7 tables)")


if __name__ == "__main__":
    create_esports_db()
    create_logistics_warehouse_db()
    create_clinical_trials_db()
    create_insurance_claims_db()
    create_cloud_devops_db()
    create_food_delivery_db()
    create_smart_city_transit_db()
    create_digital_music_db()
    print("All 8 new enterprise datasets created successfully!")

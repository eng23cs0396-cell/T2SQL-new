"""
Curated 50-Query Multi-Table Enterprise Benchmark Suite
Distributes 50 complex, moderate, and multi-join queries across 23 databases with 3 to 11 tables:
- hospital_management.db (4 tables)
- fintech_banking.db (4 tables)
- supply_chain.db (5 tables)
- airline_flight_ops.db (6 tables)
- hotel_resort.db (7 tables)
- university.db (5 tables)
- ecommerce.db (5 tables)
- course_teach.sqlite (3 tables)
- streaming_entertainment.db (4 tables)
- rideshare_mobility.db (5 tables)
- real_estate_property.db (5 tables)
- telecom_network_ops.db (6 tables)
- smart_energy_grid.db (6 tables)
- crypto_exchange_market.db (7 tables)
- software_dev_git_tracker.db (8 tables)
- gaming_esports_league.db (5 tables)
- logistics_warehouse_inventory.db (6 tables)
- healthcare_clinical_trials.db (5 tables)
- fintech_insurance_claims.db (6 tables)
- cloud_devops_infrastructure.db (7 tables)
- restaurant_food_delivery.db (6 tables)
- smart_city_transportation.db (6 tables)
- digital_music_streaming.db (7 tables)
"""

import os
import sys
import json

sys.path.insert(0, os.path.abspath("."))
from backend.database.schema_extractor import DatabaseSchemaExtractor

TEST_PATH = os.path.abspath("data/processed/spider_test.json")
DB_DIR = os.path.abspath("data/databases")

CURATED_SPECS = [
    # 1. hospital_management (4 tables)
    {
        "id": "hosp_01",
        "db_id": "hospital_management",
        "db_file": "hospital_management.db",
        "question": "Which departments have an average doctor salary greater than 200000, and what is their average doctor salary?",
        "query": "SELECT d.dept_name, AVG(doc.salary) FROM departments d JOIN doctors doc ON d.dept_id = doc.dept_id GROUP BY d.dept_name HAVING AVG(doc.salary) > 200000"
    },
    {
        "id": "hosp_02",
        "db_id": "hospital_management",
        "db_file": "hospital_management.db",
        "question": "What is the total billing amount for patient Arthur Pendelton?",
        "query": "SELECT SUM(a.billing_amount) FROM appointments a JOIN patients p ON a.patient_id = p.patient_id WHERE p.first_name = 'Arthur' AND p.last_name = 'Pendelton'"
    },
    {
        "id": "hosp_03",
        "db_id": "hospital_management",
        "db_file": "hospital_management.db",
        "question": "Find the distinct first names, last names, and specialties of doctors who have billed more than the average billing amount across all appointments.",
        "query": "SELECT DISTINCT doc.first_name, doc.last_name, doc.specialty FROM doctors doc JOIN appointments a ON doc.doctor_id = a.doctor_id WHERE a.billing_amount > (SELECT AVG(billing_amount) FROM appointments)"
    },

    # 2. fintech_banking (4 tables)
    {
        "id": "bank_01",
        "db_id": "fintech_banking",
        "db_file": "fintech_banking.db",
        "question": "What is the total account balance for each customer in New York?",
        "query": "SELECT c.first_name, c.last_name, SUM(a.balance) FROM customers c JOIN accounts a ON c.customer_id = a.customer_id WHERE c.city = 'New York' GROUP BY c.customer_id, c.first_name, c.last_name"
    },
    {
        "id": "bank_02",
        "db_id": "fintech_banking",
        "db_file": "fintech_banking.db",
        "question": "List the account IDs and balances for all active checking accounts.",
        "query": "SELECT account_id, balance FROM accounts WHERE account_type = 'Checking' AND status = 'Active'"
    },
    {
        "id": "bank_03",
        "db_id": "fintech_banking",
        "db_file": "fintech_banking.db",
        "question": "List all customers who do not have any Investment accounts.",
        "query": "SELECT first_name, last_name, email FROM customers WHERE customer_id NOT IN (SELECT customer_id FROM accounts WHERE account_type = 'Investment')"
    },

    # 3. supply_chain (5 tables)
    {
        "id": "sc_01",
        "db_id": "supply_chain",
        "db_file": "supply_chain.db",
        "question": "What is the total quantity of products on hand in the Rotterdam Euro Hub warehouse?",
        "query": "SELECT SUM(i.quantity_on_hand) FROM inventory i JOIN warehouses w ON i.warehouse_id = w.warehouse_id WHERE w.warehouse_name = 'Rotterdam Euro Hub'"
    },
    {
        "id": "sc_02",
        "db_id": "supply_chain",
        "db_file": "supply_chain.db",
        "question": "List the product names and unit prices for all products supplied by Kyoto Sensor Corp.",
        "query": "SELECT p.product_name, p.unit_price FROM products p JOIN suppliers s ON p.supplier_id = s.supplier_id WHERE s.company_name LIKE 'Kyoto Sensor Corp%'"
    },
    {
        "id": "sc_03",
        "db_id": "supply_chain",
        "db_file": "supply_chain.db",
        "question": "List the supplier company names and their total purchase order amounts for all suppliers with a total purchase order amount greater than 50000 dollars.",
        "query": "SELECT s.company_name, SUM(po.total_amount) FROM suppliers s JOIN purchase_orders po ON s.supplier_id = po.supplier_id GROUP BY s.supplier_id, s.company_name HAVING SUM(po.total_amount) > 50000"
    },

    # 4. airline_flight_ops (6 tables)
    {
        "id": "air_01",
        "db_id": "airline_flight_ops",
        "db_file": "airline_flight_ops.db",
        "question": "What is the total revenue generated from First class tickets for each airline?",
        "query": "SELECT al.airline_name, SUM(t.fare_paid) FROM tickets t JOIN flights f ON t.flight_id = f.flight_id JOIN airlines al ON f.airline_id = al.airline_id WHERE t.ticket_class = 'First' GROUP BY al.airline_id, al.airline_name"
    },
    {
        "id": "air_02",
        "db_id": "airline_flight_ops",
        "db_file": "airline_flight_ops.db",
        "question": "List the flight numbers and base fares for all flights departing from JFK.",
        "query": "SELECT flight_number, base_fare FROM flights WHERE origin_code = 'JFK'"
    },
    {
        "id": "air_03",
        "db_id": "airline_flight_ops",
        "db_file": "airline_flight_ops.db",
        "question": "Find the flight number, airline name, origin city, and destination city for all flights operated by Boeing aircraft.",
        "query": "SELECT f.flight_number, al.airline_name, a_orig.city AS origin_city, a_dest.city AS dest_city FROM flights f JOIN airlines al ON f.airline_id = al.airline_id JOIN aircraft ac ON f.aircraft_id = ac.aircraft_id JOIN airports a_orig ON f.origin_code = a_orig.airport_code JOIN airports a_dest ON f.dest_code = a_dest.airport_code WHERE ac.manufacturer = 'Boeing'"
    },

    # 5. hotel_resort (7 tables)
    {
        "id": "hotel_01",
        "db_id": "hotel_resort",
        "db_file": "hotel_resort.db",
        "question": "List the first names, last names, and loyalty tiers for all guests who have spent more than 25000 dollars.",
        "query": "SELECT first_name, last_name, loyalty_tier FROM guests WHERE total_spend > 25000"
    },
    {
        "id": "hotel_02",
        "db_id": "hotel_resort",
        "db_file": "hotel_resort.db",
        "question": "Which amenity categories have generated more than 1000 dollars in total charges across all reservations, and what is the total charge?",
        "query": "SELECT a.category, SUM(u.total_charge) FROM amenity_usage u JOIN amenities a ON u.amenity_id = a.amenity_id GROUP BY a.category HAVING SUM(u.total_charge) > 1000"
    },
    {
        "id": "hotel_03",
        "db_id": "hotel_resort",
        "db_file": "hotel_resort.db",
        "question": "List the guest name, resort name, and room number for all reservations with a paid status.",
        "query": "SELECT g.first_name, g.last_name, res.resort_name, r.room_number FROM reservations rv JOIN guests g ON rv.guest_id = g.guest_id JOIN rooms r ON rv.room_id = r.room_id JOIN resorts res ON r.resort_id = res.resort_id WHERE rv.payment_status = 'Paid'"
    },

    # 6. university (5 tables)
    {
        "id": "uni_01",
        "db_id": "university",
        "db_file": "university.db",
        "question": "Find the names of students who have scored above 90 in Database Systems.",
        "query": "SELECT s.name FROM students s JOIN enrollments e ON s.student_id = e.student_id JOIN courses c ON e.course_id = c.course_id WHERE c.title = 'Database Systems' AND e.score > 90"
    },
    {
        "id": "uni_02",
        "db_id": "university",
        "db_file": "university.db",
        "question": "What is the average GPA of students in each department that has a budget over 800000?",
        "query": "SELECT d.department_name, AVG(s.gpa) FROM departments d JOIN students s ON d.department_id = s.department_id WHERE d.budget > 800000 GROUP BY d.department_id, d.department_name"
    },

    # 7. ecommerce (5 tables)
    {
        "id": "ecom_01",
        "db_id": "ecommerce",
        "db_file": "ecommerce.db",
        "question": "List the product name, category, and total quantity ordered for all products in the Electronics category.",
        "query": "SELECT p.product_name, c.category_name, SUM(oi.quantity) FROM products p JOIN categories c ON p.category_id = c.category_id JOIN order_items oi ON p.product_id = oi.product_id WHERE c.category_name = 'Electronics' GROUP BY p.product_id, p.product_name, c.category_name"
    },
    {
        "id": "ecom_02",
        "db_id": "ecommerce",
        "db_file": "ecommerce.db",
        "question": "Find the customer name and total amount spent across all delivered orders.",
        "query": "SELECT c.name, SUM(o.total_amount) AS total_spent FROM customers c JOIN orders o ON c.customer_id = o.customer_id WHERE o.status = 'Delivered' GROUP BY c.customer_id, c.name"
    },

    # 8. course_teach (3 tables)
    {
        "id": "course_01",
        "db_id": "course_teach",
        "db_file": "course_teach.sqlite",
        "question": "List the names of teachers in ascending order of age.",
        "query": "SELECT Name FROM teacher ORDER BY Age ASC"
    },

    # 9. streaming_entertainment (4 tables)
    {
        "id": "stream_01",
        "db_id": "streaming_entertainment",
        "db_file": "streaming_entertainment.db",
        "question": "List the titles and genre names for all content items with an IMDb rating greater than 8.5.",
        "query": "SELECT c.title, g.genre_name FROM content_items c JOIN genres g ON c.genre_id = g.genre_id WHERE c.imdb_rating > 8.5"
    },
    {
        "id": "stream_02",
        "db_id": "streaming_entertainment",
        "db_file": "streaming_entertainment.db",
        "question": "What is the average IMDb rating of content watched by subscribers on the Premium 4K plan?",
        "query": "SELECT AVG(c.imdb_rating) FROM content_items c JOIN watch_history w ON c.content_id = w.content_id JOIN subscribers s ON w.subscriber_id = s.subscriber_id WHERE s.plan_tier = 'Premium 4K'"
    },

    # 10. rideshare_mobility (5 tables)
    {
        "id": "ride_01",
        "db_id": "rideshare_mobility",
        "db_file": "rideshare_mobility.db",
        "question": "What is the total completed ride fare earned by driver Marcus Thorne?",
        "query": "SELECT SUM(r.fare_amount) FROM rides r JOIN drivers d ON r.driver_id = d.driver_id WHERE d.full_name = 'Marcus Thorne' AND r.status = 'Completed'"
    },
    {
        "id": "ride_02",
        "db_id": "rideshare_mobility",
        "db_file": "rideshare_mobility.db",
        "question": "List the full names and emails of all riders who have a perfect 5.0 rating.",
        "query": "SELECT full_name, email FROM riders WHERE rating = 5.0"
    },

    # 11. real_estate_property (5 tables)
    {
        "id": "re_01",
        "db_id": "real_estate_property",
        "db_file": "real_estate_property.db",
        "question": "List the address, list price, and agent name for all condos priced over 3000000 dollars.",
        "query": "SELECT p.address, p.list_price, a.full_name FROM properties p JOIN agents a ON p.agent_id = a.agent_id WHERE p.property_type = 'Condo' AND p.list_price > 3000000"
    },
    {
        "id": "re_02",
        "db_id": "real_estate_property",
        "db_file": "real_estate_property.db",
        "question": "What is the total list price of sold properties for each agent?",
        "query": "SELECT a.full_name, SUM(p.list_price) FROM agents a JOIN properties p ON a.agent_id = p.agent_id WHERE p.status = 'Sold' GROUP BY a.agent_id, a.full_name"
    },

    # 12. telecom_network_ops (6 tables)
    {
        "id": "tel_01",
        "db_id": "telecom_network_ops",
        "db_file": "telecom_network_ops.db",
        "question": "Find the cell tower names and region names for all towers with bandwidth of at least 100 Gbps.",
        "query": "SELECT t.tower_name, r.region_name FROM cell_towers t JOIN regions r ON t.region_id = r.region_id WHERE t.bandwidth_gbps >= 100"
    },
    {
        "id": "tel_02",
        "db_id": "telecom_network_ops",
        "db_file": "telecom_network_ops.db",
        "question": "What is the total data usage in megabytes recorded for customers on the Unlimited Ultra 5G plan?",
        "query": "SELECT SUM(cr.data_mb) FROM call_records cr JOIN customers c ON cr.customer_id = c.customer_id JOIN plans p ON c.plan_id = p.plan_id WHERE p.plan_name = 'Unlimited Ultra 5G'"
    },

    # 13. smart_energy_grid (6 tables)
    {
        "id": "energy_01",
        "db_id": "smart_energy_grid",
        "db_file": "smart_energy_grid.db",
        "question": "What is the total maximum output in megawatts for each energy source type?",
        "query": "SELECT es.source_type, SUM(g.max_output_mw) FROM generators g JOIN energy_sources es ON g.source_id = es.source_id GROUP BY es.source_type"
    },
    {
        "id": "energy_02",
        "db_id": "smart_energy_grid",
        "db_file": "smart_energy_grid.db",
        "question": "List the names and transformer counts for all substations with capacity of 500 MW or higher.",
        "query": "SELECT s.name, s.transformer_count FROM substations s WHERE s.capacity_mw >= 500"
    },

    # 14. crypto_exchange_market (7 tables)
    {
        "id": "crypto_01",
        "db_id": "crypto_exchange_market",
        "db_file": "crypto_exchange_market.db",
        "question": "What is the total trade volume in USD for the BTC/USDT trading pair?",
        "query": "SELECT SUM(t.price * t.quantity) FROM trades t WHERE t.pair_symbol = 'BTC/USDT'"
    },
    {
        "id": "crypto_02",
        "db_id": "crypto_exchange_market",
        "db_file": "crypto_exchange_market.db",
        "question": "List the usernames and BTC wallet balances of traders holding more than 10 BTC.",
        "query": "SELECT t.username, w.asset_symbol, w.balance FROM traders t JOIN wallets w ON t.trader_id = w.trader_id WHERE w.asset_symbol = 'BTC' AND w.balance > 10"
    },

    # 15. software_dev_git_tracker (8 tables)
    {
        "id": "git_01",
        "db_id": "software_dev_git_tracker",
        "db_file": "software_dev_git_tracker.db",
        "question": "List the repository names and the total count of pull requests for each repository.",
        "query": "SELECT r.repo_name, COUNT(p.pr_id) FROM repositories r JOIN pull_requests p ON r.repo_id = p.repo_id GROUP BY r.repo_id, r.repo_name"
    },
    {
        "id": "git_02",
        "db_id": "software_dev_git_tracker",
        "db_file": "software_dev_git_tracker.db",
        "question": "Find the distinct usernames of users who have authored commits in Python repositories.",
        "query": "SELECT DISTINCT u.username FROM users u JOIN commits c ON u.user_id = c.author_id JOIN repositories r ON c.repo_id = r.repo_id WHERE r.language = 'Python'"
    },

    # 16. gaming_esports_league (5 tables)
    {
        "id": "esports_01",
        "db_id": "gaming_esports_league",
        "db_file": "gaming_esports_league.db",
        "question": "Find the usernames, team names, and salaries of players in the Mid role earning more than 400000.",
        "query": "SELECT p.username, t.team_name, p.salary FROM players p JOIN teams t ON p.team_id = t.team_id WHERE p.role = 'Mid' AND p.salary > 400000"
    },
    {
        "id": "esports_02",
        "db_id": "gaming_esports_league",
        "db_file": "gaming_esports_league.db",
        "question": "What is the total tournament prize pool won by team T1 across S-Tier tournaments?",
        "query": "SELECT SUM(tr.prize_pool) FROM tournaments tr JOIN matches m ON tr.tournament_id = m.tournament_id JOIN teams t ON m.winner_team_id = t.team_id WHERE t.team_name = 'T1' AND tr.tier = 'S-Tier'"
    },

    # 17. logistics_warehouse_inventory (6 tables)
    {
        "id": "log_01",
        "db_id": "logistics_warehouse_inventory",
        "db_file": "logistics_warehouse_inventory.db",
        "question": "List the product name, warehouse name, and quantity on hand for all items where quantity is below the reorder level.",
        "query": "SELECT p.product_name, w.name, i.quantity_on_hand FROM inventory_stock i JOIN products p ON i.product_id = p.product_id JOIN storage_zones z ON i.zone_id = z.zone_id JOIN warehouses w ON z.warehouse_id = w.warehouse_id WHERE i.quantity_on_hand < i.reorder_level"
    },
    {
        "id": "log_02",
        "db_id": "logistics_warehouse_inventory",
        "db_file": "logistics_warehouse_inventory.db",
        "question": "What is the total cost value of all inventory stock in the Electronics category?",
        "query": "SELECT SUM(p.unit_cost * i.quantity_on_hand) FROM products p JOIN inventory_stock i ON p.product_id = i.product_id WHERE p.category = 'Electronics'"
    },

    # 18. healthcare_clinical_trials (5 tables)
    {
        "id": "clin_01",
        "db_id": "healthcare_clinical_trials",
        "db_file": "healthcare_clinical_trials.db",
        "question": "Which clinical studies are in Phase III with target enrollment greater than 200, and who are their sponsors?",
        "query": "SELECT s.company_name, cs.title, cs.target_enrollment FROM clinical_studies cs JOIN sponsors s ON cs.sponsor_id = s.sponsor_id WHERE cs.phase = 'Phase III' AND cs.target_enrollment > 200"
    },
    {
        "id": "clin_02",
        "db_id": "healthcare_clinical_trials",
        "db_file": "healthcare_clinical_trials.db",
        "question": "List the hospital names and the count of active patients enrolled at each trial site.",
        "query": "SELECT ts.hospital_name, COUNT(pe.enrollment_id) FROM trial_sites ts JOIN patient_enrollments pe ON ts.site_id = pe.site_id WHERE pe.completion_status = 'Active' GROUP BY ts.site_id, ts.hospital_name"
    },

    # 19. fintech_insurance_claims (6 tables)
    {
        "id": "ins_01",
        "db_id": "fintech_insurance_claims",
        "db_file": "fintech_insurance_claims.db",
        "question": "What is the total approved settlement amount for Commercial Auto policies?",
        "query": "SELECT SUM(c.settlement_amount) FROM claims c JOIN insurance_policies p ON c.policy_id = p.policy_id WHERE p.policy_type = 'Commercial Auto' AND c.status = 'Approved'"
    },
    {
        "id": "ins_02",
        "db_id": "fintech_insurance_claims",
        "db_file": "fintech_insurance_claims.db",
        "question": "List the full names and total approved settlement amounts for adjusters with more than 10 years experience.",
        "query": "SELECT a.full_name, SUM(c.settlement_amount) FROM adjusters a JOIN claims c ON a.adjuster_id = c.adjuster_id WHERE a.experience_years > 10 AND c.status = 'Approved' GROUP BY a.adjuster_id, a.full_name"
    },

    # 20. cloud_devops_infrastructure (7 tables)
    {
        "id": "cloud_01",
        "db_id": "cloud_devops_infrastructure",
        "db_file": "cloud_devops_infrastructure.db",
        "question": "Which compute clusters have unresolved critical incident alerts, and in which cloud regions are they located?",
        "query": "SELECT c.cluster_name, c.cloud_region, a.alert_name FROM compute_clusters c JOIN incident_alerts a ON c.cluster_id = a.cluster_id WHERE a.severity = 'Critical' AND a.resolved_at IS NULL"
    },
    {
        "id": "cloud_02",
        "db_id": "cloud_devops_infrastructure",
        "db_file": "cloud_devops_infrastructure.db",
        "question": "What is the total cloud cost in USD for the t2sql-production project in billing month 2026-01?",
        "query": "SELECT SUM(cc.amount_usd) FROM cloud_costs cc JOIN cloud_projects cp ON cc.project_id = cp.project_id WHERE cp.project_name = 't2sql-production' AND cc.billing_month = '2026-01'"
    },

    # 21. restaurant_food_delivery (6 tables)
    {
        "id": "food_01",
        "db_id": "restaurant_food_delivery",
        "db_file": "restaurant_food_delivery.db",
        "question": "List the customer names, restaurant names, and total amounts for all delivered orders with a total amount over 30 dollars.",
        "query": "SELECT c.full_name, r.name, o.total_amount FROM orders o JOIN customers c ON o.customer_id = c.customer_id JOIN restaurants r ON o.restaurant_id = r.restaurant_id WHERE o.order_status = 'Delivered' AND o.total_amount > 30"
    },
    {
        "id": "food_02",
        "db_id": "restaurant_food_delivery",
        "db_file": "restaurant_food_delivery.db",
        "question": "What is the average rating of restaurants offering Italian or Japanese cuisine?",
        "query": "SELECT AVG(rating) FROM restaurants WHERE cuisine IN ('Italian', 'Japanese')"
    },

    # 22. smart_city_transportation (6 tables)
    {
        "id": "transit_01",
        "db_id": "smart_city_transportation",
        "db_file": "smart_city_transportation.db",
        "question": "What is the total number of daily entries recorded across all wheelchair accessible stations on 2026-02-15?",
        "query": "SELECT SUM(r.entries_count) FROM daily_ridership r JOIN stations s ON r.station_id = s.station_id WHERE s.wheelchair_accessible = 1 AND r.service_date = '2026-02-15'"
    },
    {
        "id": "transit_02",
        "db_id": "smart_city_transportation",
        "db_file": "smart_city_transportation.db",
        "question": "List the route names and agencies for all subway routes with headway less than 10 minutes.",
        "query": "SELECT r.route_name, a.name FROM transit_routes r JOIN transit_agencies a ON r.agency_id = a.agency_id WHERE r.route_type = 'Subway' AND r.headway_mins < 10"
    },

    # 23. digital_music_streaming (7 tables)
    {
        "id": "music_01",
        "db_id": "digital_music_streaming",
        "db_file": "digital_music_streaming.db",
        "question": "Find the track titles, artist stage names, and stream counts for all explicit tracks with over 500 million streams.",
        "query": "SELECT t.title, a.stage_name, t.stream_count FROM tracks t JOIN albums alb ON t.album_id = alb.album_id JOIN artists a ON alb.artist_id = a.artist_id WHERE t.is_explicit = 1 AND t.stream_count > 500000000"
    },
    {
        "id": "music_02",
        "db_id": "digital_music_streaming",
        "db_file": "digital_music_streaming.db",
        "question": "What is the total royalty payout in USD distributed to tracks by artist Billie Eilish in calculation period 2025-Q4?",
        "query": "SELECT SUM(tr.royalty_payout_usd) FROM track_royalties tr JOIN tracks t ON tr.track_id = t.track_id JOIN albums alb ON t.album_id = alb.album_id JOIN artists a ON alb.artist_id = a.artist_id WHERE a.stage_name = 'Billie Eilish' AND tr.calculation_period = '2025-Q4'"
    }
]


def build_benchmark():
    formatted = []
    print(f"Building benchmark from {len(CURATED_SPECS)} curated multi-table specifications...")
    for spec in CURATED_SPECS:
        db_path = os.path.join(DB_DIR, spec["db_file"])
        if not os.path.exists(db_path):
            print(f"[WARNING] Database not found: {db_path}")
            continue
        extractor = DatabaseSchemaExtractor(db_path)
        schema_data = extractor.extract_full_schema()
        schema_text = schema_data["formatted_text"]
        
        instruction = f"{schema_text}\n\nQuestion: {spec['question']}"
        formatted.append({
            "id": spec["id"],
            "db_id": spec["db_id"],
            "instruction": instruction,
            "output": spec["query"],
            "question": spec["question"],
            "query": spec["query"],
            "schema_text": schema_text
        })

    # Read existing spider_test.json to preserve extra fallback cases
    existing = []
    if os.path.exists(TEST_PATH):
        with open(TEST_PATH, "r", encoding="utf-8") as f:
            try:
                existing = json.load(f)
            except Exception:
                existing = []

    # Filter out any prior curated IDs
    curated_ids = set(s["id"] for s in CURATED_SPECS)
    filtered = [c for c in existing if c.get("id") not in curated_ids and not str(c.get("id", "")).startswith("complex_")]

    final_cases = formatted + filtered

    with open(TEST_PATH, "w", encoding="utf-8") as f:
        json.dump(final_cases, f, indent=2)

    print(f"[SUCCESS] Built {len(formatted)} primary curated cases ({len(final_cases)} total) in {TEST_PATH}")


if __name__ == "__main__":
    build_benchmark()

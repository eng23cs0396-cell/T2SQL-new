"""
Verification of ground truth queries across all 15 custom multi-table datasets.
"""
import os
import sqlite3

DB_DIR = os.path.abspath("data/databases")

TEST_QUERIES = [
    # 1. streaming_entertainment
    ("streaming_entertainment.db",
     "SELECT c.title, g.genre_name FROM content_items c JOIN genres g ON c.genre_id = g.genre_id WHERE c.imdb_rating > 8.5"),
    ("streaming_entertainment.db",
     "SELECT AVG(c.imdb_rating) FROM content_items c JOIN watch_history w ON c.content_id = w.content_id JOIN subscribers s ON w.subscriber_id = s.subscriber_id WHERE s.plan_tier = 'Premium 4K'"),

    # 2. rideshare_mobility
    ("rideshare_mobility.db",
     "SELECT SUM(r.fare_amount) FROM rides r JOIN drivers d ON r.driver_id = d.driver_id WHERE d.full_name = 'Marcus Thorne' AND r.status = 'Completed'"),
    ("rideshare_mobility.db",
     "SELECT full_name, email FROM riders WHERE rating = 5.0"),

    # 3. real_estate_property
    ("real_estate_property.db",
     "SELECT p.address, p.list_price, a.full_name FROM properties p JOIN agents a ON p.agent_id = a.agent_id WHERE p.property_type = 'Condo' AND p.list_price > 3000000"),
    ("real_estate_property.db",
     "SELECT a.full_name, SUM(p.list_price) FROM agents a JOIN properties p ON a.agent_id = p.agent_id WHERE p.status = 'Sold' GROUP BY a.agent_id, a.full_name"),

    # 4. telecom_network_ops
    ("telecom_network_ops.db",
     "SELECT t.tower_name, r.region_name FROM cell_towers t JOIN regions r ON t.region_id = r.region_id WHERE t.bandwidth_gbps >= 100"),
    ("telecom_network_ops.db",
     "SELECT SUM(cr.data_mb) FROM call_records cr JOIN customers c ON cr.customer_id = c.customer_id JOIN plans p ON c.plan_id = p.plan_id WHERE p.plan_name = 'Unlimited Ultra 5G'"),

    # 5. smart_energy_grid
    ("smart_energy_grid.db",
     "SELECT es.source_type, SUM(g.max_output_mw) FROM generators g JOIN energy_sources es ON g.source_id = es.source_id GROUP BY es.source_type"),
    ("smart_energy_grid.db",
     "SELECT s.name, s.transformer_count FROM substations s WHERE s.capacity_mw >= 500"),

    # 6. crypto_exchange_market
    ("crypto_exchange_market.db",
     "SELECT SUM(t.price * t.quantity) FROM trades t WHERE t.pair_symbol = 'BTC/USDT'"),
    ("crypto_exchange_market.db",
     "SELECT t.username, w.asset_symbol, w.balance FROM traders t JOIN wallets w ON t.trader_id = w.trader_id WHERE w.asset_symbol = 'BTC' AND w.balance > 10"),

    # 7. software_dev_git_tracker
    ("software_dev_git_tracker.db",
     "SELECT r.repo_name, COUNT(p.pr_id) FROM repositories r JOIN pull_requests p ON r.repo_id = p.repo_id GROUP BY r.repo_id, r.repo_name"),
    ("software_dev_git_tracker.db",
     "SELECT DISTINCT u.username FROM users u JOIN commits c ON u.user_id = c.author_id JOIN repositories r ON c.repo_id = r.repo_id WHERE r.language = 'Python'"),

    # 8. gaming_esports_league
    ("gaming_esports_league.db",
     "SELECT p.username, t.team_name, p.salary FROM players p JOIN teams t ON p.team_id = t.team_id WHERE p.role = 'Mid' AND p.salary > 400000"),
    ("gaming_esports_league.db",
     "SELECT SUM(tr.prize_pool) FROM tournaments tr JOIN matches m ON tr.tournament_id = m.tournament_id JOIN teams t ON m.winner_team_id = t.team_id WHERE t.team_name = 'T1' AND tr.tier = 'S-Tier'"),

    # 9. logistics_warehouse_inventory
    ("logistics_warehouse_inventory.db",
     "SELECT p.product_name, w.name, i.quantity_on_hand FROM inventory_stock i JOIN products p ON i.product_id = p.product_id JOIN storage_zones z ON i.zone_id = z.zone_id JOIN warehouses w ON z.warehouse_id = w.warehouse_id WHERE i.quantity_on_hand < i.reorder_level"),
    ("logistics_warehouse_inventory.db",
     "SELECT SUM(p.unit_cost * i.quantity_on_hand) FROM products p JOIN inventory_stock i ON p.product_id = i.product_id WHERE p.category = 'Electronics'"),

    # 10. healthcare_clinical_trials
    ("healthcare_clinical_trials.db",
     "SELECT s.company_name, cs.title, cs.target_enrollment FROM clinical_studies cs JOIN sponsors s ON cs.sponsor_id = s.sponsor_id WHERE cs.phase = 'Phase III' AND cs.target_enrollment > 200"),
    ("healthcare_clinical_trials.db",
     "SELECT ts.hospital_name, COUNT(pe.enrollment_id) FROM trial_sites ts JOIN patient_enrollments pe ON ts.site_id = pe.site_id WHERE pe.completion_status = 'Active' GROUP BY ts.site_id, ts.hospital_name"),

    # 11. fintech_insurance_claims
    ("fintech_insurance_claims.db",
     "SELECT SUM(c.settlement_amount) FROM claims c JOIN insurance_policies p ON c.policy_id = p.policy_id WHERE p.policy_type = 'Commercial Auto' AND c.status = 'Approved'"),
    ("fintech_insurance_claims.db",
     "SELECT a.full_name, SUM(c.settlement_amount) FROM adjusters a JOIN claims c ON a.adjuster_id = c.adjuster_id WHERE a.experience_years > 10 AND c.status = 'Approved' GROUP BY a.adjuster_id, a.full_name"),

    # 12. cloud_devops_infrastructure
    ("cloud_devops_infrastructure.db",
     "SELECT c.cluster_name, c.cloud_region, a.alert_name FROM compute_clusters c JOIN incident_alerts a ON c.cluster_id = a.cluster_id WHERE a.severity = 'Critical' AND a.resolved_at IS NULL"),
    ("cloud_devops_infrastructure.db",
     "SELECT SUM(cc.amount_usd) FROM cloud_costs cc JOIN cloud_projects cp ON cc.project_id = cp.project_id WHERE cp.project_name = 't2sql-production' AND cc.billing_month = '2026-01'"),

    # 13. restaurant_food_delivery
    ("restaurant_food_delivery.db",
     "SELECT c.full_name, r.name, o.total_amount FROM orders o JOIN customers c ON o.customer_id = c.customer_id JOIN restaurants r ON o.restaurant_id = r.restaurant_id WHERE o.order_status = 'Delivered' AND o.total_amount > 30"),
    ("restaurant_food_delivery.db",
     "SELECT AVG(rating) FROM restaurants WHERE cuisine IN ('Italian', 'Japanese')"),

    # 14. smart_city_transportation
    ("smart_city_transportation.db",
     "SELECT SUM(r.entries_count) FROM daily_ridership r JOIN stations s ON r.station_id = s.station_id WHERE s.wheelchair_accessible = 1 AND r.service_date = '2026-02-15'"),
    ("smart_city_transportation.db",
     "SELECT r.route_name, a.name FROM transit_routes r JOIN transit_agencies a ON r.agency_id = a.agency_id WHERE r.route_type = 'Subway' AND r.headway_mins < 10"),

    # 15. digital_music_streaming
    ("digital_music_streaming.db",
     "SELECT t.title, a.stage_name, t.stream_count FROM tracks t JOIN albums alb ON t.album_id = alb.album_id JOIN artists a ON alb.artist_id = a.artist_id WHERE t.is_explicit = 1 AND t.stream_count > 500000000"),
    ("digital_music_streaming.db",
     "SELECT SUM(tr.royalty_payout_usd) FROM track_royalties tr JOIN tracks t ON tr.track_id = t.track_id JOIN albums alb ON t.album_id = alb.album_id JOIN artists a ON alb.artist_id = a.artist_id WHERE a.stage_name = 'Billie Eilish' AND tr.calculation_period = '2025-Q4'")
]

all_passed = True
for db_file, sql in TEST_QUERIES:
    db_path = os.path.join(DB_DIR, db_file)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        print(f"[OK] {db_file} -> {len(rows)} rows: {rows[:1]}")
    except Exception as e:
        print(f"[ERROR] {db_file} -> {e} | SQL: {sql}")
        all_passed = False
    finally:
        conn.close()

if all_passed:
    print("\nALL 30 QUERIES ACROSS 15 CUSTOM DATASETS EXECUTED SUCCESSFULLY!")

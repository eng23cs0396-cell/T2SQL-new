import sqlite3
import os

tests = [
    ('streaming_entertainment.db', 'SELECT g.genre_name, AVG(c.imdb_rating) FROM genres g JOIN content_items c ON g.genre_id = c.genre_id GROUP BY g.genre_id, g.genre_name HAVING AVG(c.imdb_rating) > 8.0'),
    ('streaming_entertainment.db', "SELECT SUM(w.watch_duration_mins) FROM watch_history w JOIN subscribers s ON w.subscriber_id = s.subscriber_id WHERE s.full_name = 'Emma Watson'"),
    ('rideshare_mobility.db', "SELECT d.full_name, SUM(r.fare_amount) FROM drivers d JOIN rides r ON d.driver_id = r.driver_id JOIN cities c ON d.city_id = c.city_id WHERE c.city_name = 'San Francisco' GROUP BY d.driver_id, d.full_name"),
    ('rideshare_mobility.db', "SELECT d.full_name FROM drivers d JOIN cities c ON d.city_id = c.city_id WHERE d.rating > 4.90 AND c.city_name = 'Tokyo'"),
    ('real_estate_property.db', "SELECT AVG(p.list_price) FROM properties p JOIN agents a ON p.agent_id = a.agent_id JOIN agencies ag ON a.agency_id = ag.agency_id WHERE p.property_type = 'Condo' AND p.status = 'Active' AND ag.city = 'New York'"),
    ('crypto_exchange_market.db', 'SELECT t.username, SUM(w.balance) FROM traders t JOIN wallets w ON t.trader_id = w.trader_id WHERE t.vip_level >= 4 GROUP BY t.trader_id, t.username'),
    ('software_dev_git_tracker.db', "SELECT count(*) FROM pull_requests pr JOIN users u ON pr.author_id = u.user_id WHERE u.full_name = 'Demis Hassabis' AND pr.status = 'Merged'")
]
for db, q in tests:
    rows = sqlite3.connect(os.path.join('data/databases', db)).execute(q).fetchall()
    print(f"{db:<30} | {len(rows)} rows | {rows}")

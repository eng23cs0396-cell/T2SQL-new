import sqlite3
import os

tests = [
    ('hospital_management.db', 'SELECT d.dept_name, AVG(doc.salary) FROM departments d JOIN doctors doc ON d.dept_id = doc.dept_id GROUP BY d.dept_name HAVING AVG(doc.salary) > 200000'),
    ('hospital_management.db', "SELECT p.first_name, p.last_name, doc.first_name, doc.last_name FROM appointments a JOIN patients p ON a.patient_id = p.patient_id JOIN doctors doc ON a.doctor_id = doc.doctor_id JOIN departments d ON doc.dept_id = d.dept_id WHERE a.status = 'Completed' AND d.dept_name = 'Cardiology'"),
    ('hospital_management.db', 'SELECT DISTINCT doc.first_name, doc.last_name, doc.specialty FROM doctors doc JOIN appointments a ON doc.doctor_id = a.doctor_id WHERE a.billing_amount > (SELECT AVG(billing_amount) FROM appointments)'),
    ('hospital_management.db', 'SELECT doc.first_name, doc.last_name, SUM(a.billing_amount) AS total_billed FROM doctors doc JOIN appointments a ON doc.doctor_id = a.doctor_id GROUP BY doc.doctor_id, doc.first_name, doc.last_name ORDER BY total_billed DESC'),
    ('fintech_banking.db', "SELECT c.first_name, c.last_name, SUM(a.balance) FROM customers c JOIN accounts a ON c.customer_id = a.customer_id WHERE c.city = 'New York' GROUP BY c.customer_id, c.first_name, c.last_name"),
    ('fintech_banking.db', "SELECT t.transaction_id, t.amount, t.txn_date, b.branch_name FROM transactions t JOIN accounts a ON t.account_id = a.account_id JOIN branches b ON a.branch_id = b.branch_id WHERE t.txn_type = 'Debit' AND t.amount > 2000"),
    ('fintech_banking.db', "SELECT first_name, last_name, email FROM customers WHERE customer_id NOT IN (SELECT customer_id FROM accounts WHERE account_type = 'Investment')"),
    ('fintech_banking.db', 'SELECT b.branch_name, AVG(a.balance) FROM branches b JOIN accounts a ON b.branch_id = a.branch_id GROUP BY b.branch_id, b.branch_name HAVING AVG(a.balance) > (SELECT AVG(balance) FROM accounts)'),
    ('supply_chain.db', "SELECT SUM(i.quantity_on_hand * p.unit_cost) FROM inventory i JOIN products p ON i.product_id = p.product_id JOIN warehouses w ON i.warehouse_id = w.warehouse_id WHERE w.warehouse_name = 'Chicago Logistics Terminal'"),
    ('supply_chain.db', 'SELECT s.company_name, SUM(po.total_amount) FROM suppliers s JOIN purchase_orders po ON s.supplier_id = po.supplier_id GROUP BY s.supplier_id, s.company_name HAVING SUM(po.total_amount) > 50000'),
    ('supply_chain.db', 'SELECT p1.product_name, p1.category, p1.unit_price FROM products p1 WHERE p1.unit_price > (SELECT AVG(p2.unit_price) FROM products p2 WHERE p2.category = p1.category)'),
    ('supply_chain.db', "SELECT w.warehouse_name, SUM(i.quantity_on_hand) AS total_qty FROM warehouses w JOIN inventory i ON w.warehouse_id = i.warehouse_id JOIN products p ON i.product_id = p.product_id WHERE p.category = 'Semiconductors' GROUP BY w.warehouse_id, w.warehouse_name ORDER BY total_qty DESC LIMIT 1"),
    ('airline_flight_ops.db', "SELECT f.flight_number, al.airline_name, a_orig.city AS origin_city, a_dest.city AS dest_city FROM flights f JOIN airlines al ON f.airline_id = al.airline_id JOIN aircraft ac ON f.aircraft_id = ac.aircraft_id JOIN airports a_orig ON f.origin_code = a_orig.airport_code JOIN airports a_dest ON f.dest_code = a_dest.airport_code WHERE ac.manufacturer = 'Boeing'"),
    ('airline_flight_ops.db', "SELECT al.airline_name, SUM(t.fare_paid) FROM tickets t JOIN flights f ON t.flight_id = f.flight_id JOIN airlines al ON f.airline_id = al.airline_id WHERE t.ticket_class = 'First' GROUP BY al.airline_id, al.airline_name"),
    ('airline_flight_ops.db', "SELECT DISTINCT p.first_name, p.last_name FROM passengers p JOIN tickets t ON p.passenger_id = t.passenger_id JOIN flights f ON t.flight_id = f.flight_id WHERE f.origin_code = 'JFK'"),
    ('airline_flight_ops.db', 'SELECT f.flight_number, AVG(t.fare_paid) AS avg_fare FROM flights f JOIN tickets t ON f.flight_id = t.flight_id GROUP BY f.flight_id, f.flight_number ORDER BY avg_fare DESC LIMIT 1'),
    ('hotel_resort.db', "SELECT g.first_name, g.last_name, res.resort_name, r.room_number FROM reservations rv JOIN guests g ON rv.guest_id = g.guest_id JOIN rooms r ON rv.room_id = r.room_id JOIN resorts res ON r.resort_id = res.resort_id WHERE rv.payment_status = 'Paid'"),
    ('hotel_resort.db', 'SELECT a.category, SUM(u.total_charge) FROM amenity_usage u JOIN amenities a ON u.amenity_id = a.amenity_id GROUP BY a.category HAVING SUM(u.total_charge) > 1000'),
    ('hotel_resort.db', "SELECT g.first_name, g.last_name, rv.room_total + COALESCE(SUM(u.total_charge), 0) AS total_bill FROM reservations rv JOIN guests g ON rv.guest_id = g.guest_id JOIN rooms r ON rv.room_id = r.room_id JOIN resorts res ON r.resort_id = res.resort_id LEFT JOIN amenity_usage u ON rv.reservation_id = u.reservation_id WHERE res.resort_name = 'Azure Horizon Paradise' GROUP BY rv.reservation_id, g.first_name, g.last_name, rv.room_total"),
    ('hotel_resort.db', 'SELECT first_name, last_name, loyalty_tier, total_spend FROM guests WHERE total_spend = (SELECT MAX(total_spend) FROM guests)'),
    ('university.db', "SELECT s.name FROM students s JOIN enrollments e ON s.student_id = e.student_id JOIN courses c ON e.course_id = c.course_id WHERE c.title = 'Database Systems' AND e.score > 90"),
    ('university.db', 'SELECT d.department_name, AVG(s.gpa) FROM departments d JOIN students s ON d.department_id = s.department_id WHERE d.budget > 800000 GROUP BY d.department_id, d.department_name'),
    ('ecommerce.db', "SELECT p.product_name, c.category_name, SUM(oi.quantity) FROM products p JOIN categories c ON p.category_id = c.category_id JOIN order_items oi ON p.product_id = oi.product_id WHERE c.category_name = 'Electronics' GROUP BY p.product_id, p.product_name, c.category_name"),
    ('ecommerce.db', "SELECT c.name, SUM(o.total_amount) AS total_spent FROM customers c JOIN orders o ON c.customer_id = o.customer_id WHERE o.status = 'Delivered' GROUP BY c.customer_id, c.name")
]

db_dir = "data/databases"
for idx, (db, sql) in enumerate(tests, 1):
    db_path = os.path.join(db_dir, db)
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    print(f"Query {idx:2d} | DB: {db:<24} | Rows: {len(rows):2d} | Sample: {rows[0] if rows else 'EMPTY'}")

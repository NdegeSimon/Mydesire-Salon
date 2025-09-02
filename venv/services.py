import sqlite3
from database import get_connection

# ✅ Create booking
def create_booking(customer_id, attendant_id, time):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO bookings (customer_id, attendant_id, time) VALUES (?, ?, ?)",
        (customer_id, attendant_id, time)
    )
    conn.commit()
    conn.close()

    # After booking → send notification
    message = f"Your booking with attendant {attendant_id} is confirmed for {time}."
    send_notification(customer_id, message)

# ✅ Send notification (via email/phone simulation)
def send_notification(customer_id, message):
    conn = get_connection()
    cur = conn.cursor()

    # Save notification in DB
    cur.execute(
        "INSERT INTO notifications (customer_id, message) VALUES (?, ?)",
        (customer_id, message)
    )

    # Fetch customer info (email/phone)
    cur.execute("SELECT name, email, phone FROM customers WHERE id=?", (customer_id,))
    customer = cur.fetchone()

    if customer:
        name, email, phone = customer
        print(f"📧 Sending email to {email}: {message}")
        print(f"📱 Sending SMS to {phone}: {message}")

    conn.commit()
    conn.close()

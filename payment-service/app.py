from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import os
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'mysql-db'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'database': os.getenv('DB_NAME', 'hotel_booking'),
    'port': int(os.getenv('DB_PORT', 3306))
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create payments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                booking_id INT,
                user_id INT,
                amount DECIMAL(10,2),
                payment_method VARCHAR(50),
                payment_status ENUM('pending', 'completed', 'failed', 'refunded') DEFAULT 'pending',
                transaction_id VARCHAR(255) UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create invoices table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INT AUTO_INCREMENT PRIMARY KEY,
                booking_id INT,
                user_id INT,
                invoice_number VARCHAR(50) UNIQUE,
                amount DECIMAL(10,2),
                tax_amount DECIMAL(10,2) DEFAULT 0,
                total_amount DECIMAL(10,2),
                status ENUM('draft', 'sent', 'paid', 'overdue') DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Payment database initialized successfully")
    except Exception as e:
        print(f"Error initializing payment database: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "payment-service"})

@app.route('/payments/process', methods=['POST'])
def process_payment():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate unique transaction ID
        transaction_id = str(uuid.uuid4())
        
        # Simulate payment processing (fake gateway)
        payment_status = 'completed'  # Always successful for demo
        
        cursor.execute("""
            INSERT INTO payments (booking_id, user_id, amount, payment_method, payment_status, transaction_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data['booking_id'], data['user_id'], data['amount'], 
              data['payment_method'], payment_status, transaction_id))
        
        payment_id = cursor.lastrowid
        
        # Update booking status to confirmed
        cursor.execute("""
            UPDATE bookings SET status = 'confirmed' WHERE id = %s
        """, (data['booking_id'],))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Payment processed successfully",
            "payment_id": payment_id,
            "transaction_id": transaction_id,
            "status": payment_status
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/invoices/generate', methods=['POST'])
def generate_invoice():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate unique invoice number
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Calculate tax (10% tax rate)
        tax_amount = data['amount'] * 0.10
        total_amount = data['amount'] + tax_amount
        
        cursor.execute("""
            INSERT INTO invoices (booking_id, user_id, invoice_number, amount, tax_amount, total_amount, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (data['booking_id'], data['user_id'], invoice_number, 
              data['amount'], tax_amount, total_amount, 'sent'))
        
        invoice_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Invoice generated successfully",
            "invoice_id": invoice_id,
            "invoice_number": invoice_number,
            "amount": data['amount'],
            "tax_amount": tax_amount,
            "total_amount": total_amount
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/payments/user/<int:user_id>', methods=['GET'])
def get_user_payments(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.*, b.check_in_date, b.check_out_date, h.name as hotel_name
            FROM payments p
            JOIN bookings b ON p.booking_id = b.id
            JOIN hotels h ON b.hotel_id = h.id
            WHERE p.user_id = %s
            ORDER BY p.created_at DESC
        """, (user_id,))
        payments = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(payments)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/invoices/user/<int:user_id>', methods=['GET'])
def get_user_invoices(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT i.*, b.check_in_date, b.check_out_date, h.name as hotel_name
            FROM invoices i
            JOIN bookings b ON i.booking_id = b.id
            JOIN hotels h ON b.hotel_id = h.id
            WHERE i.user_id = %s
            ORDER BY i.created_at DESC
        """, (user_id,))
        invoices = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(invoices)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/payments/all', methods=['GET'])
def get_all_payments():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.*, b.check_in_date, b.check_out_date, h.name as hotel_name, u.username
            FROM payments p
            JOIN bookings b ON p.booking_id = b.id
            JOIN hotels h ON b.hotel_id = h.id
            JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
        """)
        payments = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(payments)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/invoices/all', methods=['GET'])
def get_all_invoices():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT i.*, b.check_in_date, b.check_out_date, h.name as hotel_name, u.username
            FROM invoices i
            JOIN bookings b ON i.booking_id = b.id
            JOIN hotels h ON b.hotel_id = h.id
            JOIN users u ON i.user_id = u.id
            ORDER BY i.created_at DESC
        """)
        invoices = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(invoices)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/payments/<int:payment_id>/refund', methods=['POST'])
def refund_payment(payment_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE payments SET payment_status = 'refunded' WHERE id = %s", (payment_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Payment refunded successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5005, debug=True)
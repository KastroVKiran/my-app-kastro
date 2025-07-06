from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import os
from datetime import datetime, timedelta
import json

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
        
        # Create bookings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                hotel_id INT,
                room_type_id INT,
                check_in_date DATE NOT NULL,
                check_out_date DATE NOT NULL,
                total_amount DECIMAL(10,2),
                status ENUM('pending', 'confirmed', 'cancelled') DEFAULT 'pending',
                guest_name VARCHAR(255),
                guest_email VARCHAR(255),
                guest_phone VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create room_availability table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS room_availability (
                id INT AUTO_INCREMENT PRIMARY KEY,
                hotel_id INT,
                room_type_id INT,
                available_date DATE,
                available_rooms INT DEFAULT 10,
                UNIQUE KEY unique_availability (hotel_id, room_type_id, available_date)
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Booking database initialized successfully")
    except Exception as e:
        print(f"Error initializing booking database: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "booking-service"})

@app.route('/bookings', methods=['POST'])
def create_booking():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check room availability
        cursor.execute("""
            SELECT COUNT(*) FROM bookings 
            WHERE hotel_id = %s AND room_type_id = %s 
            AND status != 'cancelled'
            AND ((check_in_date <= %s AND check_out_date > %s) 
                 OR (check_in_date < %s AND check_out_date >= %s))
        """, (data['hotel_id'], data['room_type_id'], 
              data['check_in_date'], data['check_in_date'],
              data['check_out_date'], data['check_out_date']))
        
        existing_bookings = cursor.fetchone()[0]
        
        if existing_bookings >= 10:  # Max 10 rooms per type
            return jsonify({"error": "No rooms available for selected dates"}), 400
        
        # Create booking
        cursor.execute("""
            INSERT INTO bookings (user_id, hotel_id, room_type_id, check_in_date, 
                                check_out_date, total_amount, guest_name, guest_email, guest_phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (data['user_id'], data['hotel_id'], data['room_type_id'],
              data['check_in_date'], data['check_out_date'], data['total_amount'],
              data['guest_name'], data['guest_email'], data['guest_phone']))
        
        booking_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Booking created successfully", "booking_id": booking_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/bookings/<int:user_id>', methods=['GET'])
def get_user_bookings(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT b.*, h.name as hotel_name, h.location 
            FROM bookings b 
            JOIN hotels h ON b.hotel_id = h.id 
            WHERE b.user_id = %s 
            ORDER BY b.created_at DESC
        """, (user_id,))
        bookings = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(bookings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/bookings/all', methods=['GET'])
def get_all_bookings():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT b.*, h.name as hotel_name, h.location 
            FROM bookings b 
            JOIN hotels h ON b.hotel_id = h.id 
            ORDER BY b.created_at DESC
        """)
        bookings = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(bookings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/bookings/<int:booking_id>/confirm', methods=['PUT'])
def confirm_booking(booking_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE bookings SET status = 'confirmed' WHERE id = %s", (booking_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Booking confirmed successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/bookings/<int:booking_id>/cancel', methods=['PUT'])
def cancel_booking(booking_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE bookings SET status = 'cancelled' WHERE id = %s", (booking_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Booking cancelled successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/availability', methods=['GET'])
def check_availability():
    try:
        hotel_id = request.args.get('hotel_id')
        check_in = request.args.get('check_in')
        check_out = request.args.get('check_out')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get available rooms for the date range
        cursor.execute("""
            SELECT rt.*, 
                   (10 - COALESCE(booked.count, 0)) as available_rooms
            FROM room_types rt
            LEFT JOIN (
                SELECT room_type_id, COUNT(*) as count
                FROM bookings
                WHERE hotel_id = %s 
                AND status != 'cancelled'
                AND ((check_in_date <= %s AND check_out_date > %s) 
                     OR (check_in_date < %s AND check_out_date >= %s))
                GROUP BY room_type_id
            ) booked ON rt.id = booked.room_type_id
            WHERE rt.hotel_id = %s
            HAVING available_rooms > 0
        """, (hotel_id, check_in, check_in, check_out, check_out, hotel_id))
        
        availability = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(availability)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5002, debug=True)
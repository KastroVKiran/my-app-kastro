from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import os
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
        
        # Create hotels table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hotels (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                location VARCHAR(255) NOT NULL,
                description TEXT,
                amenities TEXT,
                price_per_night DECIMAL(10,2),
                total_rooms INT DEFAULT 50,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create room_types table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS room_types (
                id INT AUTO_INCREMENT PRIMARY KEY,
                hotel_id INT,
                type_name VARCHAR(100) NOT NULL,
                price DECIMAL(10,2),
                capacity INT,
                amenities TEXT,
                FOREIGN KEY (hotel_id) REFERENCES hotels(id)
            )
        """)
        
        # Insert sample data
        cursor.execute("SELECT COUNT(*) FROM hotels")
        count = cursor.fetchone()[0]
        
        if count == 0:
            sample_hotels = [
                ("Grand Palace Hotel", "New York", "Luxury hotel in Manhattan", "WiFi, Pool, Spa, Gym, Restaurant", 350.00, 100),
                ("Beach Resort", "Miami", "Beachfront resort with ocean views", "Beach Access, Pool, Bar, WiFi", 250.00, 80),
                ("Mountain Lodge", "Colorado", "Cozy lodge in the mountains", "Fireplace, WiFi, Restaurant, Hiking", 180.00, 60),
                ("Business Hotel", "Chicago", "Modern hotel for business travelers", "WiFi, Conference Room, Gym", 220.00, 120),
                ("Boutique Inn", "San Francisco", "Charming boutique hotel", "WiFi, Breakfast, Concierge", 290.00, 40)
            ]
            
            for hotel in sample_hotels:
                cursor.execute("""
                    INSERT INTO hotels (name, location, description, amenities, price_per_night, total_rooms)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, hotel)
            
            # Insert room types
            room_types = [
                (1, "Deluxe Suite", 450.00, 2, "King bed, City view, Mini bar"),
                (1, "Standard Room", 300.00, 2, "Queen bed, WiFi"),
                (2, "Ocean View", 320.00, 2, "Ocean view, Balcony"),
                (2, "Garden View", 200.00, 2, "Garden view, Patio"),
                (3, "Mountain View", 220.00, 2, "Mountain view, Fireplace"),
                (4, "Business Suite", 280.00, 2, "Desk, Meeting area"),
                (5, "Boutique Room", 250.00, 2, "Unique decor, Premium amenities")
            ]
            
            for room_type in room_types:
                cursor.execute("""
                    INSERT INTO room_types (hotel_id, type_name, price, capacity, amenities)
                    VALUES (%s, %s, %s, %s, %s)
                """, room_type)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "hotel-service"})

@app.route('/hotels', methods=['GET'])
def get_hotels():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM hotels ORDER BY created_at DESC")
        hotels = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(hotels)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/hotels/<int:hotel_id>', methods=['GET'])
def get_hotel(hotel_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM hotels WHERE id = %s", (hotel_id,))
        hotel = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if hotel:
            return jsonify(hotel)
        else:
            return jsonify({"error": "Hotel not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/hotels/<int:hotel_id>/rooms', methods=['GET'])
def get_hotel_rooms(hotel_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM room_types WHERE hotel_id = %s", (hotel_id,))
        rooms = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rooms)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/hotels', methods=['POST'])
def add_hotel():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO hotels (name, location, description, amenities, price_per_night, total_rooms)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data['name'], data['location'], data['description'], 
              data['amenities'], data['price_per_night'], data.get('total_rooms', 50)))
        
        conn.commit()
        hotel_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Hotel added successfully", "hotel_id": hotel_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/hotels/<int:hotel_id>', methods=['DELETE'])
def delete_hotel(hotel_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM hotels WHERE id = %s", (hotel_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Hotel deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001, debug=True)
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import os
from datetime import datetime

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
        
        # Create reviews table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                hotel_id INT,
                booking_id INT,
                rating INT CHECK (rating >= 1 AND rating <= 5),
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert sample reviews
        cursor.execute("SELECT COUNT(*) FROM reviews")
        count = cursor.fetchone()[0]
        
        if count == 0:
            sample_reviews = [
                (1, 1, None, 5, "Excellent service and beautiful rooms!"),
                (1, 2, None, 4, "Great location and nice beach access."),
                (1, 3, None, 4, "Cozy mountain lodge with great hiking trails."),
                (1, 4, None, 3, "Good for business trips, convenient location."),
                (1, 5, None, 5, "Charming boutique hotel with amazing breakfast."),
                (2, 1, None, 4, "Luxury hotel with outstanding amenities."),
                (2, 2, None, 5, "Perfect beachfront location for vacation."),
                (2, 3, None, 3, "Nice mountain views but rooms could be updated."),
            ]
            
            for review in sample_reviews:
                cursor.execute("""
                    INSERT INTO reviews (user_id, hotel_id, booking_id, rating, comment)
                    VALUES (%s, %s, %s, %s, %s)
                """, review)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Review database initialized successfully")
    except Exception as e:
        print(f"Error initializing review database: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "review-service"})

@app.route('/reviews', methods=['POST'])
def create_review():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO reviews (user_id, hotel_id, booking_id, rating, comment)
            VALUES (%s, %s, %s, %s, %s)
        """, (data['user_id'], data['hotel_id'], data.get('booking_id'),
              data['rating'], data['comment']))
        
        review_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Review created successfully", "review_id": review_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reviews/hotel/<int:hotel_id>', methods=['GET'])
def get_hotel_reviews(hotel_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.*, u.username, u.first_name, u.last_name
            FROM reviews r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE r.hotel_id = %s
            ORDER BY r.created_at DESC
        """, (hotel_id,))
        reviews = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(reviews)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reviews/user/<int:user_id>', methods=['GET'])
def get_user_reviews(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.*, h.name as hotel_name, h.location
            FROM reviews r
            JOIN hotels h ON r.hotel_id = h.id
            WHERE r.user_id = %s
            ORDER BY r.created_at DESC
        """, (user_id,))
        reviews = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(reviews)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reviews/hotel/<int:hotel_id>/average', methods=['GET'])
def get_hotel_average_rating(hotel_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT AVG(rating) as average_rating, COUNT(*) as total_reviews
            FROM reviews
            WHERE hotel_id = %s
        """, (hotel_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        average_rating = float(result[0]) if result[0] else 0
        total_reviews = result[1]
        
        return jsonify({
            "hotel_id": hotel_id,
            "average_rating": round(average_rating, 1),
            "total_reviews": total_reviews
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reviews/all', methods=['GET'])
def get_all_reviews():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.*, u.username, u.first_name, u.last_name, h.name as hotel_name, h.location
            FROM reviews r
            LEFT JOIN users u ON r.user_id = u.id
            JOIN hotels h ON r.hotel_id = h.id
            ORDER BY r.created_at DESC
        """)
        reviews = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(reviews)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reviews WHERE id = %s", (review_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Review deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5004, debug=True)
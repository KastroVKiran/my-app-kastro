CREATE DATABASE IF NOT EXISTS hotel_booking;
USE hotel_booking;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    phone VARCHAR(20),
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Hotels table
CREATE TABLE IF NOT EXISTS hotels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    description TEXT,
    amenities TEXT,
    price_per_night DECIMAL(10,2),
    total_rooms INT DEFAULT 50,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Room types table
CREATE TABLE IF NOT EXISTS room_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hotel_id INT,
    type_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2),
    capacity INT,
    amenities TEXT,
    FOREIGN KEY (hotel_id) REFERENCES hotels(id)
);

-- Bookings table
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
);

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    hotel_id INT,
    booking_id INT,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT,
    user_id INT,
    amount DECIMAL(10,2),
    payment_method VARCHAR(50),
    payment_status ENUM('pending', 'completed', 'failed', 'refunded') DEFAULT 'pending',
    transaction_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Invoices table
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
);

-- User sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    session_token VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Room availability table
CREATE TABLE IF NOT EXISTS room_availability (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hotel_id INT,
    room_type_id INT,
    available_date DATE,
    available_rooms INT DEFAULT 10,
    UNIQUE KEY unique_availability (hotel_id, room_type_id, available_date)
);

-- Insert sample data
-- Insert admin user
INSERT IGNORE INTO users (username, email, password_hash, first_name, last_name, is_admin) 
VALUES ('admin', 'admin@hotel.com', SHA2('admin123', 256), 'Admin', 'User', TRUE);

-- Insert sample hotels
INSERT IGNORE INTO hotels (id, name, location, description, amenities, price_per_night, total_rooms) VALUES
(1, 'Grand Palace Hotel', 'New York', 'Luxury hotel in Manhattan', 'WiFi, Pool, Spa, Gym, Restaurant', 350.00, 100),
(2, 'Beach Resort', 'Miami', 'Beachfront resort with ocean views', 'Beach Access, Pool, Bar, WiFi', 250.00, 80),
(3, 'Mountain Lodge', 'Colorado', 'Cozy lodge in the mountains', 'Fireplace, WiFi, Restaurant, Hiking', 180.00, 60),
(4, 'Business Hotel', 'Chicago', 'Modern hotel for business travelers', 'WiFi, Conference Room, Gym', 220.00, 120),
(5, 'Boutique Inn', 'San Francisco', 'Charming boutique hotel', 'WiFi, Breakfast, Concierge', 290.00, 40);

-- Insert room types
INSERT IGNORE INTO room_types (hotel_id, type_name, price, capacity, amenities) VALUES
(1, 'Deluxe Suite', 450.00, 2, 'King bed, City view, Mini bar'),
(1, 'Standard Room', 300.00, 2, 'Queen bed, WiFi'),
(2, 'Ocean View', 320.00, 2, 'Ocean view, Balcony'),
(2, 'Garden View', 200.00, 2, 'Garden view, Patio'),
(3, 'Mountain View', 220.00, 2, 'Mountain view, Fireplace'),
(4, 'Business Suite', 280.00, 2, 'Desk, Meeting area'),
(5, 'Boutique Room', 250.00, 2, 'Unique decor, Premium amenities');

-- Insert sample reviews
INSERT IGNORE INTO reviews (user_id, hotel_id, rating, comment) VALUES
(1, 1, 5, 'Excellent service and beautiful rooms!'),
(1, 2, 4, 'Great location and nice beach access.'),
(1, 3, 4, 'Cozy mountain lodge with great hiking trails.'),
(1, 4, 3, 'Good for business trips, convenient location.'),
(1, 5, 5, 'Charming boutique hotel with amazing breakfast.');

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    color VARCHAR(50),
    max_speed DECIMAL(10,2),
    consumption DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
CREATE INDEX IF NOT EXISTS idx_products_color ON products(color);
CREATE INDEX IF NOT EXISTS idx_products_max_speed ON products(max_speed);
CREATE INDEX IF NOT EXISTS idx_products_consumption ON products(consumption);

-- Insert sample data
INSERT INTO products (name, description, price, color, max_speed, consumption) VALUES
('Luxury Sedan 2024', 'Premium luxury sedan with advanced features', 45000.00, 'Black', 220.00, 8.5),
('Sports Car GT', 'High-performance sports car with sleek design', 65000.00, 'Red', 280.00, 12.5),
('Electric SUV', 'Eco-friendly SUV with long range', 55000.00, 'White', 180.00, 0.0),
('Compact Hatchback', 'Fuel-efficient city car', 25000.00, 'Blue', 160.00, 6.5),
('Family Minivan', 'Spacious family vehicle with modern amenities', 35000.00, 'Silver', 170.00, 9.0);
ALTER TABLE products ADD COLUMN image_url TEXT;
-- Create conversation_logs table
CREATE TABLE IF NOT EXISTS conversation_logs (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL
);

-- Ensure session_id is indexed for conversation_logs
CREATE INDEX IF NOT EXISTS idx_conversation_logs_session_id ON conversation_logs(session_id);

-- Create user_profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    session_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    location VARCHAR(255),
    age INTEGER,
    budget NUMERIC,
    usage TEXT,
    preferences JSONB,
    requirements JSONB,
    test_drive_agreed BOOLEAN,
    phone_number VARCHAR(20),
    email VARCHAR(255),
    confirmation_sent BOOLEAN,
    test_drive_status BOOLEAN,
    test_drive_date TIMESTAMP
);

-- Add indexes for user_profiles on columns that may be filtered
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_phone_number ON user_profiles(phone_number); 
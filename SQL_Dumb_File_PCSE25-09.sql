-- Dump of database: lung_health_system
-- ------------------------------------------------------
CREATE DATABASE IF NOT EXISTS lung_health_system;
USE lung_health_system;

-- Table structure for table users
DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- No pre-inserted records. Users will register through the web interface.

-- Sample data for testing purposes (commented out)
-- INSERT INTO users (name, email, password) VALUES
-- ('Alice Johnson', 'alice@example.com', 'hashed_password_1'),
-- ('Bob Smith', 'bob@example.com', 'hashed_password_2'),
-- ('Charlie Lee', 'charlie@example.com', 'hashed_password_3');
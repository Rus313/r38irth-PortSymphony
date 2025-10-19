-- ============================================
-- PSA Global Insights Dashboard
-- MySQL Database Schema
-- Data Engineer: Database Specialist
-- ============================================

-- Create database
CREATE DATABASE IF NOT EXISTS psa_maritime CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE psa_maritime;

-- ============================================
-- VESSELS TABLE
-- Master data for all vessels
-- ============================================

CREATE TABLE IF NOT EXISTS vessels (
    vessel_id INT AUTO_INCREMENT PRIMARY KEY,
    vessel_name VARCHAR(255) NOT NULL,
    imo_number VARCHAR(20) UNIQUE NOT NULL,
    operator VARCHAR(255),
    service VARCHAR(100),
    current_location POINT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_imo (imo_number),
    INDEX idx_operator (operator),
    INDEX idx_updated (last_updated)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- SHIP_MOVEMENTS TABLE
-- Detailed vessel movement records
-- ============================================

CREATE TABLE IF NOT EXISTS ship_movements (
    movement_id INT AUTO_INCREMENT PRIMARY KEY,
    operator VARCHAR(255),
    service VARCHAR(100),
    direction ENUM('Import', 'Export') NOT NULL,
    business_unit VARCHAR(100),
    vessel_name VARCHAR(255),
    imo_number VARCHAR(20) NOT NULL,
    rotation_no VARCHAR(50),
    from_port VARCHAR(100),
    to_port VARCHAR(100),
    berth VARCHAR(50),
    status VARCHAR(50),
    
    -- Timing fields
    btr_96h_to_atb DATETIME COMMENT '96h before arrival',
    final_btr DATETIME COMMENT 'Final berthing time request',
    abt DATETIME COMMENT 'Actual berthing time',
    atb DATETIME COMMENT 'Alongside time berth',
    atu DATETIME COMMENT 'Actual time unberthed',
    
    -- Performance metrics
    arrival_variance_4h BOOLEAN COMMENT 'Within 4-hour target',
    arrival_accuracy_final_btr DECIMAL(5,2) COMMENT 'Accuracy percentage',
    wait_time_atb_btr DECIMAL(10,2) COMMENT 'Wait time ATB-BTR (hours)',
    wait_time_abt_btr DECIMAL(10,2) COMMENT 'Wait time ABT-BTR (hours)',
    wait_time_atb_abt DECIMAL(10,2) COMMENT 'Wait time ATB-ABT (hours)',
    berth_time_hours DECIMAL(10,2) COMMENT 'Berth time ATU-ATB (hours)',
    assured_port_time_pct DECIMAL(5,2) COMMENT 'Assured port time percentage',
    
    -- Sustainability metrics
    bunker_saved_usd DECIMAL(12,2) COMMENT 'Bunker cost savings',
    carbon_abatement_tonnes DECIMAL(10,3) COMMENT 'Carbon saved (tonnes)',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (imo_number) REFERENCES vessels(imo_number) ON DELETE CASCADE,
    
    INDEX idx_imo (imo_number),
    INDEX idx_berth (berth),
    INDEX idx_status (status),
    INDEX idx_atb (atb),
    INDEX idx_business_unit (business_unit),
    INDEX idx_from_port (from_port),
    INDEX idx_to_port (to_port)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- WEATHER_DATA TABLE
-- Weather conditions and forecasts
-- ============================================

CREATE TABLE IF NOT EXISTS weather_data (
    weather_id INT AUTO_INCREMENT PRIMARY KEY,
    port VARCHAR(100) NOT NULL,
    timestamp DATETIME NOT NULL,
    temperature DECIMAL(5,2) COMMENT 'Temperature in Celsius',
    feels_like DECIMAL(5,2) COMMENT 'Feels like temperature',
    humidity INT COMMENT 'Humidity percentage',
    pressure INT COMMENT 'Atmospheric pressure (hPa)',
    wind_speed DECIMAL(5,2) COMMENT 'Wind speed (m/s)',
    wind_direction INT COMMENT 'Wind direction (degrees)',
    wave_height DECIMAL(5,2) COMMENT 'Wave height (meters)',
    visibility DECIMAL(5,2) COMMENT 'Visibility (km)',
    precipitation DECIMAL(5,2) COMMENT 'Precipitation (mm)',
    weather_description VARCHAR(255),
    is_forecast BOOLEAN DEFAULT FALSE COMMENT 'True if forecast, false if actual',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_port (port),
    INDEX idx_timestamp (timestamp),
    INDEX idx_forecast (is_forecast),
    UNIQUE KEY unique_port_timestamp (port, timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- BERTH_AVAILABILITY TABLE
-- Real-time berth status
-- ============================================

CREATE TABLE IF NOT EXISTS berth_availability (
    berth_id VARCHAR(50) PRIMARY KEY,
    terminal VARCHAR(100) NOT NULL,
    status ENUM('Available', 'Occupied', 'Maintenance', 'Reserved') DEFAULT 'Available',
    current_vessel_imo VARCHAR(20),
    expected_available_time DATETIME,
    max_vessel_size INT COMMENT 'Maximum vessel size (TEU)',
    max_draft DECIMAL(5,2) COMMENT 'Maximum draft (meters)',
    berth_length DECIMAL(6,2) COMMENT 'Berth length (meters)',
    equipment VARCHAR(255) COMMENT 'Available equipment',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (current_vessel_imo) REFERENCES vessels(imo_number) ON DELETE SET NULL,
    
    INDEX idx_terminal (terminal),
    INDEX idx_status (status),
    INDEX idx_available_time (expected_available_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- CARBON_METRICS TABLE
-- Carbon emissions and savings tracking
-- ============================================

CREATE TABLE IF NOT EXISTS carbon_metrics (
    metric_id INT AUTO_INCREMENT PRIMARY KEY,
    vessel_imo VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    total_emissions_tonnes DECIMAL(10,3) COMMENT 'Total emissions for the day',
    emissions_per_hour DECIMAL(10,3) COMMENT 'Average emissions per hour',
    savings_from_optimization DECIMAL(10,3) COMMENT 'Carbon saved through optimization',
    bunker_consumption_mt DECIMAL(10,3) COMMENT 'Bunker consumption (metric tonnes)',
    distance_traveled_nm DECIMAL(10,2) COMMENT 'Distance traveled (nautical miles)',
    average_speed_knots DECIMAL(5,2) COMMENT 'Average speed',
    optimization_method VARCHAR(255) COMMENT 'Method used for optimization',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (vessel_imo) REFERENCES vessels(imo_number) ON DELETE CASCADE,
    
    INDEX idx_vessel_date (vessel_imo, date),
    INDEX idx_date (date),
    UNIQUE KEY unique_vessel_date (vessel_imo, date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- VECTOR_EMBEDDINGS TABLE
-- Semantic search embeddings
-- ============================================

CREATE TABLE IF NOT EXISTS vector_embeddings (
    embedding_id INT AUTO_INCREMENT PRIMARY KEY,
    movement_id INT NOT NULL,
    document_text TEXT NOT NULL COMMENT 'Original text that was embedded',
    embedding_vector JSON NOT NULL COMMENT 'Vector embedding as JSON array',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (movement_id) REFERENCES ship_movements(movement_id) ON DELETE CASCADE,
    
    INDEX idx_movement (movement_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- USER_QUERIES TABLE
-- Track user queries for analytics
-- ============================================

CREATE TABLE IF NOT EXISTS user_queries (
    query_id INT AUTO_INCREMENT PRIMARY KEY,
    user_department VARCHAR(100),
    query_text TEXT NOT NULL,
    intent_type VARCHAR(50) COMMENT 'chat/analysis/bulk',
    analysis_category VARCHAR(50),
    model_used VARCHAR(50) COMMENT 'Which AI model was used',
    response_time_ms INT COMMENT 'Response time in milliseconds',
    was_successful BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_department (user_department),
    INDEX idx_intent (intent_type),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- ALERTS TABLE
-- System-generated alerts
-- ============================================

CREATE TABLE IF NOT EXISTS alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    alert_type ENUM('bunching', 'weather', 'delay', 'carbon', 'maintenance') NOT NULL,
    severity ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    affected_vessels JSON COMMENT 'Array of IMO numbers',
    affected_berths JSON COMMENT 'Array of berth IDs',
    recommended_action TEXT,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_type (alert_type),
    INDEX idx_severity (severity),
    INDEX idx_resolved (is_resolved),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- SAMPLE DATA INSERTION
-- ============================================

-- Insert sample ports as vessels (for tracking)
INSERT INTO vessels (vessel_name, imo_number, operator, service) VALUES
('MSC Diana', '9876543', 'MSC', 'Asia-Europe'),
('Ever Given', '9811000', 'Evergreen', 'Far East-Europe'),
('CMA CGM Antoine', '9454436', 'CMA CGM', 'Asia-Med'),
('Maersk Essex', '9632101', 'Maersk', 'Trans-Pacific'),
('COSCO Shipping', '9793241', 'COSCO', 'Asia-US');

-- Insert sample berths
INSERT INTO berth_availability (berth_id, terminal, status, max_vessel_size, max_draft, berth_length) VALUES
('B01', 'Terminal 1', 'Available', 20000, 16.0, 400.0),
('B02', 'Terminal 1', 'Occupied', 20000, 16.0, 400.0),
('B03', 'Terminal 2', 'Available', 18000, 15.5, 380.0),
('B04', 'Terminal 2', 'Maintenance', 18000, 15.5, 380.0),
('B05', 'Terminal 3', 'Available', 22000, 17.0, 420.0),
('B06', 'Terminal 3', 'Occupied', 22000, 17.0, 420.0),
('B07', 'Terminal 4', 'Available', 15000, 14.0, 350.0),
('B08', 'Terminal 4', 'Available', 15000, 14.0, 350.0);

-- Insert sample ship movements
INSERT INTO ship_movements (
    operator, service, direction, business_unit, vessel_name, imo_number,
    rotation_no, from_port, to_port, berth, status, final_btr, atb, atu,
    arrival_variance_4h, arrival_accuracy_final_btr, wait_time_atb_btr,
    berth_time_hours, bunker_saved_usd, carbon_abatement_tonnes
) VALUES
('MSC', 'Asia-Europe', 'Import', 'Container', 'MSC Diana', '9876543',
 'MSC001', 'Singapore', 'Rotterdam', 'B02', 'At Berth',
 DATE_SUB(NOW(), INTERVAL 2 HOUR), DATE_SUB(NOW(), INTERVAL 1 HOUR), NULL,
 TRUE, 95.5, 1.2, NULL, 4200.00, 12.4),

('Evergreen', 'Far East-Europe', 'Export', 'Container', 'Ever Given', '9811000',
 'EVG002', 'Shanghai', 'Los Angeles', NULL, 'In Transit',
 DATE_ADD(NOW(), INTERVAL 12 HOUR), NULL, NULL,
 NULL, NULL, NULL, NULL, NULL, NULL),

('CMA CGM', 'Asia-Med', 'Import', 'Container', 'CMA CGM Antoine', '9454436',
 'CGM003', 'Rotterdam', 'Singapore', 'B03', 'Waiting',
 DATE_ADD(NOW(), INTERVAL 4 HOUR), NULL, NULL,
 NULL, NULL, NULL, NULL, NULL, NULL),

('Maersk', 'Trans-Pacific', 'Export', 'Container', 'Maersk Essex', '9632101',
 'MSK004', 'Los Angeles', 'Shanghai', NULL, 'Departed',
 DATE_SUB(NOW(), INTERVAL 48 HOUR), DATE_SUB(NOW(), INTERVAL 46 HOUR),
 DATE_SUB(NOW(), INTERVAL 22 HOUR), TRUE, 98.2, 2.0, 24.0, 8500.00, 32.1),

('COSCO', 'Asia-US', 'Import', 'Container', 'COSCO Shipping', '9793241',
 'COS005', 'Antwerp', 'Singapore', NULL, 'In Transit',
 DATE_ADD(NOW(), INTERVAL 18 HOUR), NULL, NULL,
 NULL, NULL, NULL, NULL, NULL, NULL);

-- Insert sample weather data
INSERT INTO weather_data (
    port, timestamp, temperature, humidity, wind_speed, wind_direction,
    wave_height, visibility, precipitation, weather_description, is_forecast
) VALUES
('Singapore', NOW(), 28.5, 78, 3.2, 120, 0.5, 10.0, 0.0, 'Partly cloudy', FALSE),
('Rotterdam', NOW(), 12.3, 85, 8.5, 270, 1.5, 8.5, 2.5, 'Light rain', FALSE),
('Shanghai', NOW(), 18.7, 72, 5.1, 180, 0.8, 9.0, 0.0, 'Clear', FALSE),
('Los Angeles', NOW(), 22.4, 65, 4.3, 90, 0.6, 12.0, 0.0, 'Sunny', FALSE),
('Antwerp', NOW(), 10.8, 88, 9.2, 250, 1.8, 7.0, 5.0, 'Rain', FALSE),

-- Forecast data
('Singapore', DATE_ADD(NOW(), INTERVAL 24 HOUR), 29.0, 75, 3.5, 130, 0.6, 10.0, 0.0, 'Partly cloudy', TRUE),
('Rotterdam', DATE_ADD(NOW(), INTERVAL 24 HOUR), 11.5, 90, 12.0, 280, 2.5, 6.0, 8.0, 'Heavy rain', TRUE),
('Shanghai', DATE_ADD(NOW(), INTERVAL 24 HOUR), 19.2, 70, 4.8, 170, 0.7, 9.5, 0.0, 'Clear', TRUE);

-- Insert sample carbon metrics
INSERT INTO carbon_metrics (
    vessel_imo, date, total_emissions_tonnes, emissions_per_hour,
    savings_from_optimization, bunker_consumption_mt, distance_traveled_nm,
    average_speed_knots, optimization_method
) VALUES
('9876543', DATE_SUB(CURDATE(), INTERVAL 1 DAY), 45.2, 1.88, 12.4, 15.2, 420, 18.5, 'Speed optimization'),
('9811000', DATE_SUB(CURDATE(), INTERVAL 1 DAY), 52.8, 2.20, 8.7, 17.8, 480, 20.0, 'Route optimization'),
('9454436', DATE_SUB(CURDATE(), INTERVAL 2 DAY), 38.6, 1.61, 15.2, 13.0, 390, 17.2, 'Weather routing'),
('9632101', DATE_SUB(CURDATE(), INTERVAL 2 DAY), 48.9, 2.04, 10.3, 16.5, 450, 19.3, 'Speed optimization'),
('9793241', DATE_SUB(CURDATE(), INTERVAL 3 DAY), 41.3, 1.72, 11.8, 14.2, 410, 18.0, 'Berth scheduling');

-- Insert sample alerts
INSERT INTO alerts (
    alert_type, severity, title, description, affected_vessels,
    affected_berths, recommended_action
) VALUES
('bunching', 'HIGH', 'Vessel Bunching Detected at Terminal 4',
 '3 vessels scheduled to arrive within 4-hour window at Singapore Terminal 4',
 '["9454436", "9793241", "9876543"]', '["B07", "B08"]',
 'Recommend staggering arrivals by 45 minutes to optimize berth utilization. Estimated savings: $4,200 in bunker costs, 2.1 hours wait time reduction.'),

('weather', 'MEDIUM', 'Strong Winds Expected at Rotterdam',
 'Wind speeds of 35 knots expected tomorrow 08:00-14:00 GMT. May affect berthing operations.',
 '["9811000", "9454436"]', '["B01", "B02", "B03"]',
 'Consider delaying arrivals or adjusting schedule. Monitor weather updates closely.'),

('delay', 'CRITICAL', 'Significant Arrival Delay',
 'MSC Mediterranean delayed by 6.2 hours due to port congestion at origin',
 '["9876543"]', '["B07"]',
 'Berth #7 now available ahead of schedule. Can reassign to waiting vessel to improve utilization.'),

('carbon', 'LOW', 'Carbon Optimization Opportunity',
 'Potential to reduce emissions by 15% through speed optimization on current route',
 '["9793241"]', NULL,
 'Recommend reducing speed to 16 knots for fuel efficiency. Estimated savings: 8.5 tonnes CO2, $3,200.'),

('maintenance', 'MEDIUM', 'Scheduled Berth Maintenance',
 'Berth B04 scheduled for maintenance starting tomorrow 00:00 for 48 hours',
 NULL, '["B04"]',
 'Reassign scheduled vessels to alternative berths. B03 and B05 available as alternatives.');

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

-- View: Recent vessel performance
CREATE OR REPLACE VIEW v_recent_performance AS
SELECT 
    v.vessel_name,
    v.imo_number,
    v.operator,
    sm.from_port,
    sm.to_port,
    sm.berth,
    sm.atb,
    sm.atu,
    sm.arrival_accuracy_final_btr,
    sm.wait_time_atb_btr,
    sm.berth_time_hours,
    sm.bunker_saved_usd,
    sm.carbon_abatement_tonnes,
    sm.status
FROM ship_movements sm
JOIN vessels v ON sm.imo_number = v.imo_number
WHERE sm.atb >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY sm.atb DESC;

-- View: Current berth occupancy
CREATE OR REPLACE VIEW v_berth_occupancy AS
SELECT 
    ba.berth_id,
    ba.terminal,
    ba.status,
    v.vessel_name,
    ba.expected_available_time,
    ba.max_vessel_size,
    ba.berth_length
FROM berth_availability ba
LEFT JOIN vessels v ON ba.current_vessel_imo = v.imo_number;

-- View: Carbon summary by vessel
CREATE OR REPLACE VIEW v_carbon_summary AS
SELECT 
    v.vessel_name,
    v.imo_number,
    v.operator,
    SUM(cm.total_emissions_tonnes) as total_emissions,
    SUM(cm.savings_from_optimization) as total_savings,
    AVG(cm.emissions_per_hour) as avg_emissions_rate,
    COUNT(*) as days_tracked
FROM carbon_metrics cm
JOIN vessels v ON cm.vessel_imo = v.imo_number
WHERE cm.date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY v.vessel_name, v.imo_number, v.operator;

-- View: Active alerts summary
CREATE OR REPLACE VIEW v_active_alerts AS
SELECT 
    alert_type,
    severity,
    title,
    description,
    created_at,
    TIMESTAMPDIFF(HOUR, created_at, NOW()) as hours_active
FROM alerts
WHERE is_resolved = FALSE
ORDER BY 
    FIELD(severity, 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'),
    created_at DESC;

-- View: Weather forecast summary
CREATE OR REPLACE VIEW v_weather_forecast AS
SELECT 
    port,
    timestamp,
    temperature,
    wind_speed,
    wave_height,
    weather_description,
    CASE 
        WHEN wind_speed > 15 THEN 'HIGH RISK'
        WHEN wind_speed > 10 THEN 'MODERATE RISK'
        ELSE 'LOW RISK'
    END as operational_risk
FROM weather_data
WHERE is_forecast = TRUE
AND timestamp >= NOW()
AND timestamp <= DATE_ADD(NOW(), INTERVAL 72 HOUR)
ORDER BY port, timestamp;

-- ============================================
-- STORED PROCEDURES
-- ============================================

-- Procedure: Calculate vessel wait time statistics
DELIMITER //
CREATE PROCEDURE sp_calculate_wait_time_stats(
    IN p_days INT
)
BEGIN
    SELECT 
        business_unit,
        COUNT(*) as total_vessels,
        AVG(wait_time_atb_btr) as avg_wait_time,
        MIN(wait_time_atb_btr) as min_wait_time,
        MAX(wait_time_atb_btr) as max_wait_time,
        STDDEV(wait_time_atb_btr) as std_wait_time
    FROM ship_movements
    WHERE atb >= DATE_SUB(NOW(), INTERVAL p_days DAY)
    AND wait_time_atb_btr IS NOT NULL
    GROUP BY business_unit
    ORDER BY avg_wait_time DESC;
END //
DELIMITER ;

-- Procedure: Detect vessel bunching
DELIMITER //
CREATE PROCEDURE sp_detect_bunching(
    IN p_hours_ahead INT,
    IN p_window_hours INT
)
BEGIN
    -- Find berths with 3+ vessels arriving within specified window
    SELECT 
        berth,
        COUNT(*) as vessel_count,
        MIN(final_btr) as window_start,
        MAX(final_btr) as window_end,
        GROUP_CONCAT(vessel_name SEPARATOR ', ') as vessels
    FROM ship_movements
    WHERE final_btr BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL p_hours_ahead HOUR)
    AND status IN ('Scheduled', 'In Transit')
    GROUP BY berth
    HAVING vessel_count >= 3
    AND TIMESTAMPDIFF(HOUR, MIN(final_btr), MAX(final_btr)) <= p_window_hours
    ORDER BY vessel_count DESC;
END //
DELIMITER ;

-- Procedure: Get carbon optimization opportunities
DELIMITER //
CREATE PROCEDURE sp_carbon_opportunities(
    IN p_days INT
)
BEGIN
    SELECT 
        v.vessel_name,
        v.imo_number,
        AVG(cm.emissions_per_hour) as avg_emissions_rate,
        AVG(cm.average_speed_knots) as avg_speed,
        SUM(cm.savings_from_optimization) as total_savings,
        -- Calculate potential additional savings (10% improvement)
        SUM(cm.total_emissions_tonnes) * 0.10 as potential_savings
    FROM carbon_metrics cm
    JOIN vessels v ON cm.vessel_imo = v.imo_number
    WHERE cm.date >= DATE_SUB(CURDATE(), INTERVAL p_days DAY)
    GROUP BY v.vessel_name, v.imo_number
    HAVING avg_emissions_rate > (
        SELECT AVG(emissions_per_hour) FROM carbon_metrics
        WHERE date >= DATE_SUB(CURDATE(), INTERVAL p_days DAY)
    )
    ORDER BY potential_savings DESC;
END //
DELIMITER ;

-- ============================================
-- TRIGGERS
-- ============================================

-- Trigger: Auto-update berth availability when vessel berths
DELIMITER //
CREATE TRIGGER tr_update_berth_on_arrival
AFTER UPDATE ON ship_movements
FOR EACH ROW
BEGIN
    IF NEW.atb IS NOT NULL AND OLD.atb IS NULL THEN
        UPDATE berth_availability
        SET status = 'Occupied',
            current_vessel_imo = NEW.imo_number
        WHERE berth_id = NEW.berth;
    END IF;
END //
DELIMITER ;

-- Trigger: Auto-update berth availability when vessel departs
DELIMITER //
CREATE TRIGGER tr_update_berth_on_departure
AFTER UPDATE ON ship_movements
FOR EACH ROW
BEGIN
    IF NEW.atu IS NOT NULL AND OLD.atu IS NULL THEN
        UPDATE berth_availability
        SET status = 'Available',
            current_vessel_imo = NULL,
            expected_available_time = NULL
        WHERE berth_id = NEW.berth;
    END IF;
END //
DELIMITER ;

-- Trigger: Log user queries
DELIMITER //
CREATE TRIGGER tr_log_query_response_time
BEFORE INSERT ON user_queries
FOR EACH ROW
BEGIN
    IF NEW.response_time_ms > 5000 THEN
        -- Flag slow queries for optimization
        SET NEW.was_successful = FALSE;
    END IF;
END //
DELIMITER ;

-- ============================================
-- INDEXES FOR OPTIMIZATION
-- ============================================

-- Additional composite indexes for common queries
CREATE INDEX idx_movement_performance ON ship_movements(atb, arrival_accuracy_final_btr, wait_time_atb_btr);
CREATE INDEX idx_carbon_vessel_date ON carbon_metrics(vessel_imo, date DESC);
CREATE INDEX idx_weather_port_forecast ON weather_data(port, is_forecast, timestamp);
CREATE INDEX idx_alerts_active ON alerts(is_resolved, severity, created_at);

-- Full-text search indexes
ALTER TABLE alerts ADD FULLTEXT INDEX ft_alert_text(title, description);
ALTER TABLE ship_movements ADD FULLTEXT INDEX ft_vessel_info(vessel_name, from_port, to_port);

-- ============================================
-- SAMPLE ANALYTICS QUERIES
-- ============================================

-- Query 1: Daily performance summary
-- SELECT * FROM v_recent_performance WHERE DATE(atb) = CURDATE();

-- Query 2: Detect bunching for next 48 hours
-- CALL sp_detect_bunching(48, 4);

-- Query 3: Carbon optimization opportunities
-- CALL sp_carbon_opportunities(30);

-- Query 4: Wait time statistics by business unit
-- CALL sp_calculate_wait_time_stats(30);

-- Query 5: Active high-priority alerts
-- SELECT * FROM v_active_alerts WHERE severity IN ('HIGH', 'CRITICAL');

-- Query 6: Weather risk assessment
-- SELECT * FROM v_weather_forecast WHERE operational_risk = 'HIGH RISK';

-- ============================================
-- BACKUP AND MAINTENANCE
-- ============================================

-- Recommended maintenance schedule:
-- 1. Daily: Backup database
-- 2. Weekly: Optimize tables (OPTIMIZE TABLE)
-- 3. Monthly: Archive old data (movements > 6 months)
-- 4. Quarterly: Review and update indexes

-- Archive old movements (run monthly)
-- CREATE TABLE ship_movements_archive LIKE ship_movements;
-- INSERT INTO ship_movements_archive SELECT * FROM ship_movements WHERE atb < DATE_SUB(NOW(), INTERVAL 6 MONTH);
-- DELETE FROM ship_movements WHERE atb < DATE_SUB(NOW(), INTERVAL 6 MONTH);

-- ============================================
-- GRANTS AND PERMISSIONS
-- ============================================

-- Create application user
-- CREATE USER 'psa_app'@'localhost' IDENTIFIED BY 'secure_password';
-- GRANT SELECT, INSERT, UPDATE ON psa_maritime.* TO 'psa_app'@'localhost';
-- GRANT EXECUTE ON PROCEDURE psa_maritime.* TO 'psa_app'@'localhost';

-- Create read-only user for analytics
-- CREATE USER 'psa_analytics'@'localhost' IDENTIFIED BY 'analytics_password';
-- GRANT SELECT ON psa_maritime.* TO 'psa_analytics'@'localhost';

-- FLUSH PRIVILEGES;

-- ============================================
-- END OF SCHEMA
-- ============================================
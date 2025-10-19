"""
Database Manager Module
MySQL database operations and queries
Data Engineer: Database Specialist
"""

import mysql.connector
from mysql.connector import Error, pooling
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration"""
    
    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        port: int = 3306,
        pool_name: str = "psa_pool",
        pool_size: int = 5
    ):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.pool_name = pool_name
        self.pool_size = pool_size


class DatabaseManager:
    """
    Manages all database operations with connection pooling
    """
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection_pool = self._create_connection_pool()
    
    def _create_connection_pool(self):
        """Create MySQL connection pool"""
        try:
            pool = pooling.MySQLConnectionPool(
                pool_name=self.config.pool_name,
                pool_size=self.config.pool_size,
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                password=self.config.password,
                database=self.config.database
            )
            logger.info("Database connection pool created successfully")
            return pool
        except Error as e:
            logger.error(f"Error creating connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        connection = None
        try:
            connection = self.connection_pool.get_connection()
            yield connection
        except Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    # ============================================
    # VESSEL OPERATIONS
    # ============================================
    
    def get_recent_vessels(self, limit: int = 10) -> List[Dict]:
        """Get most recent vessel movements"""
        
        query = """
        SELECT 
            v.vessel_name,
            v.imo_number,
            v.operator,
            sm.from_port,
            sm.to_port,
            sm.berth,
            sm.status,
            sm.atb,
            sm.atu,
            sm.wait_time_atb_btr,
            sm.berth_time_hours,
            sm.carbon_abatement_tonnes,
            sm.bunker_saved_usd
        FROM ship_movements sm
        JOIN vessels v ON sm.imo_number = v.imo_number
        ORDER BY sm.atb DESC
        LIMIT %s
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            cursor.close()
            
        logger.info(f"Retrieved {len(results)} recent vessels")
        return results
    
    def get_vessel_by_imo(self, imo_number: str) -> Optional[Dict]:
        """Get vessel details by IMO number"""
        
        # ✅ ADD: Input validation
        from security.validation import validate_imo
        is_valid, message = validate_imo(imo_number)
        if not is_valid:
            logger.warning(f"Invalid IMO number: {imo_number}")
            return None
        
        # ✅ IMPORTANT: Use %s placeholders (already correct in your code!)
        query = """
            SELECT *
            FROM vessels
            WHERE imo_number = %s
        """
    
    with self.get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (imo_number,))  # ✅ This is correct - using tuple for parameters
        result = cursor.fetchone()
        cursor.close()
        
    return result
    
    def get_upcoming_arrivals(self, hours: int = 48) -> List[Dict]:
        """Get vessels arriving in next N hours"""
        
        future_time = datetime.now() + timedelta(hours=hours)
        
        query = """
        SELECT 
            v.vessel_name,
            v.imo_number,
            v.operator,
            sm.from_port,
            sm.to_port,
            sm.berth,
            sm.final_btr as eta,
            sm.status
        FROM ship_movements sm
        JOIN vessels v ON sm.imo_number = v.imo_number
        WHERE sm.final_btr BETWEEN NOW() AND %s
        AND sm.status IN ('Scheduled', 'In Transit')
        ORDER BY sm.final_btr ASC
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (future_time,))
            results = cursor.fetchall()
            cursor.close()
            
        logger.info(f"Retrieved {len(results)} upcoming arrivals")
        return results
    
    def get_historical_movements(
        self,
        days: int = 30,
        limit: int = 500
    ) -> List[Dict]:
        """Get historical vessel movements"""
        
        start_date = datetime.now() - timedelta(days=days)
        
        query = """
        SELECT 
            v.vessel_name,
            v.imo_number,
            v.operator,
            sm.*
        FROM ship_movements sm
        JOIN vessels v ON sm.imo_number = v.imo_number
        WHERE sm.atb >= %s
        ORDER BY sm.atb DESC
        LIMIT %s
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (start_date, limit))
            results = cursor.fetchall()
            cursor.close()
            
        logger.info(f"Retrieved {len(results)} historical movements")
        return results
    
    # ============================================
    # METRICS & ANALYTICS
    # ============================================
    
    def get_current_metrics(self) -> Dict:
        """Get current performance metrics"""
        
        query = """
        SELECT 
            AVG(arrival_accuracy_final_btr) as avg_arrival_accuracy,
            AVG(wait_time_atb_btr) as avg_wait_time,
            SUM(carbon_abatement_tonnes) as total_carbon_saved,
            SUM(bunker_saved_usd) as total_bunker_saved,
            COUNT(*) as total_movements
        FROM ship_movements
        WHERE atb >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            
        return result or {}
    
    def get_performance_data(self, days: int = 30) -> List[Dict]:
        """Get performance data for analysis"""
        
        start_date = datetime.now() - timedelta(days=days)
        
        query = """
        SELECT 
            DATE(atb) as date,
            business_unit,
            AVG(arrival_accuracy_final_btr) as avg_accuracy,
            AVG(wait_time_atb_btr) as avg_wait_time,
            AVG(berth_time_hours) as avg_berth_time,
            COUNT(*) as vessel_count
        FROM ship_movements
        WHERE atb >= %s
        GROUP BY DATE(atb), business_unit
        ORDER BY date DESC
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (start_date,))
            results = cursor.fetchall()
            cursor.close()
            
        return results
    
    # ============================================
    # CARBON & SUSTAINABILITY
    # ============================================
    
    def get_carbon_metrics(self, days: int = 30) -> List[Dict]:
        """Get carbon emissions and savings data"""
        
        start_date = datetime.now() - timedelta(days=days)
        
        query = """
        SELECT 
            cm.date,
            v.vessel_name,
            v.imo_number,
            cm.total_emissions_tonnes,
            cm.emissions_per_hour,
            cm.savings_from_optimization
        FROM carbon_metrics cm
        JOIN vessels v ON cm.vessel_imo = v.imo_number
        WHERE cm.date >= %s
        ORDER BY cm.date DESC
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (start_date,))
            results = cursor.fetchall()
            cursor.close()
            
        logger.info(f"Retrieved {len(results)} carbon metrics")
        return results
    
    def get_carbon_summary(self) -> Dict:
        """Get carbon emissions summary"""
        
        query = """
        SELECT 
            SUM(total_emissions_tonnes) as total_emissions,
            SUM(savings_from_optimization) as total_savings,
            AVG(emissions_per_hour) as avg_emissions_rate,
            COUNT(DISTINCT vessel_imo) as vessels_tracked
        FROM carbon_metrics
        WHERE date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            
        return result or {}
    
    # ============================================
    # BERTH MANAGEMENT
    # ============================================
    
    def get_berth_availability(self) -> List[Dict]:
        """Get current berth availability"""
        
        query = """
        SELECT 
            berth_id,
            terminal,
            status,
            current_vessel_imo,
            expected_available_time,
            max_vessel_size
        FROM berth_availability
        ORDER BY terminal, berth_id
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
        return results
    
    def get_berth_utilization(self, days: int = 7) -> Dict:
        """Calculate berth utilization metrics"""
        
        start_date = datetime.now() - timedelta(days=days)
        
        query = """
        SELECT 
            berth,
            COUNT(*) as total_vessels,
            AVG(berth_time_hours) as avg_berth_time,
            SUM(berth_time_hours) as total_occupied_hours
        FROM ship_movements
        WHERE atb >= %s AND atu IS NOT NULL
        GROUP BY berth
        ORDER BY total_vessels DESC
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (start_date,))
            results = cursor.fetchall()
            cursor.close()
            
        # Calculate utilization percentage
        total_hours = days * 24
        for result in results:
            result['utilization_pct'] = (
                result['total_occupied_hours'] / total_hours * 100
            )
        
        return results
    
    # ============================================
    # WEATHER DATA
    # ============================================
    
    def get_weather_forecast(self, port: str = "Singapore") -> List[Dict]:
        """Get weather forecast for specified port"""
        
        query = """
        SELECT 
            timestamp,
            temperature,
            wind_speed,
            wind_direction,
            wave_height,
            visibility,
            precipitation
        FROM weather_data
        WHERE port = %s
        AND timestamp >= NOW()
        AND timestamp <= DATE_ADD(NOW(), INTERVAL 72 HOUR)
        ORDER BY timestamp ASC
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (port,))
            results = cursor.fetchall()
            cursor.close()
            
        return results
    
    def get_current_weather(self, port: str) -> Optional[Dict]:
        """Get current weather conditions"""
        
        query = """
        SELECT *
        FROM weather_data
        WHERE port = %s
        ORDER BY timestamp DESC
        LIMIT 1
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (port,))
            result = cursor.fetchone()
            cursor.close()
            
        return result
    
    # ============================================
    # DATA INSERTION
    # ============================================
    
    def insert_vessel(self, vessel_data: Dict) -> bool:
        """Insert new vessel record"""
        
        query = """
        INSERT INTO vessels (vessel_name, imo_number, operator, service, current_location)
        VALUES (%(vessel_name)s, %(imo_number)s, %(operator)s, %(service)s, POINT(%(lon)s, %(lat)s))
        ON DUPLICATE KEY UPDATE
            vessel_name = VALUES(vessel_name),
            operator = VALUES(operator),
            last_updated = NOW()
        """
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, vessel_data)
                conn.commit()
                cursor.close()
            logger.info(f"Inserted vessel: {vessel_data.get('vessel_name')}")
            return True
        except Error as e:
            logger.error(f"Error inserting vessel: {e}")
            return False
    
    def insert_ship_movement(self, movement_data: Dict) -> bool:
        """Insert ship movement record"""
        
        query = """
        INSERT INTO ship_movements (
            operator, service, direction, business_unit, vessel_name, imo_number,
            rotation_no, from_port, to_port, berth, status, btr_96h_to_atb,
            final_btr, abt, atb, atu, arrival_variance_4h, arrival_accuracy_final_btr,
            wait_time_atb_btr, wait_time_abt_btr, wait_time_atb_abt, berth_time_hours,
            assured_port_time_pct, bunker_saved_usd, carbon_abatement_tonnes
        )
        VALUES (
            %(operator)s, %(service)s, %(direction)s, %(business_unit)s,
            %(vessel_name)s, %(imo_number)s, %(rotation_no)s, %(from_port)s,
            %(to_port)s, %(berth)s, %(status)s, %(btr_96h_to_atb)s,
            %(final_btr)s, %(abt)s, %(atb)s, %(atu)s, %(arrival_variance_4h)s,
            %(arrival_accuracy_final_btr)s, %(wait_time_atb_btr)s,
            %(wait_time_abt_btr)s, %(wait_time_atb_abt)s, %(berth_time_hours)s,
            %(assured_port_time_pct)s, %(bunker_saved_usd)s, %(carbon_abatement_tonnes)s
        )
        """
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, movement_data)
                conn.commit()
                cursor.close()
            logger.info(f"Inserted movement for vessel: {movement_data.get('vessel_name')}")
            return True
        except Error as e:
            logger.error(f"Error inserting movement: {e}")
            return False
    
    def insert_weather_data(self, weather_data: Dict) -> bool:
        """Insert weather data record"""
        
        query = """
        INSERT INTO weather_data (
            port, timestamp, temperature, wind_speed, wind_direction,
            wave_height, visibility, precipitation
        )
        VALUES (
            %(port)s, %(timestamp)s, %(temperature)s, %(wind_speed)s,
            %(wind_direction)s, %(wave_height)s, %(visibility)s, %(precipitation)s
        )
        """
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, weather_data)
                conn.commit()
                cursor.close()
            logger.info(f"Inserted weather data for: {weather_data.get('port')}")
            return True
        except Error as e:
            logger.error(f"Error inserting weather data: {e}")
            return False
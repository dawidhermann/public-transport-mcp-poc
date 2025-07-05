-- Initialize PostGIS extensions and create basic schema for public transport data

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Create schema for public transport data
CREATE SCHEMA IF NOT EXISTS transport;

-- Create tables for public transport entities
CREATE TABLE IF NOT EXISTS transport.stops (
    id SERIAL PRIMARY KEY,
    stop_id VARCHAR(50) UNIQUE NOT NULL,
    stop_name VARCHAR(255) NOT NULL,
    stop_desc TEXT,
    stop_lat DECIMAL(10, 8),
    stop_lon DECIMAL(11, 8),
    location_type INTEGER DEFAULT 0,
    parent_station VARCHAR(50),
    stop_timezone VARCHAR(50),
    wheelchair_boarding INTEGER DEFAULT 0,
    geom GEOMETRY(POINT, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transport.routes (
    id SERIAL PRIMARY KEY,
    route_id VARCHAR(50) UNIQUE NOT NULL,
    agency_id VARCHAR(50),
    route_short_name VARCHAR(50),
    route_long_name VARCHAR(255),
    route_desc TEXT,
    route_type INTEGER NOT NULL,
    route_url VARCHAR(255),
    route_color VARCHAR(6),
    route_text_color VARCHAR(6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transport.trips (
    id SERIAL PRIMARY KEY,
    route_id VARCHAR(50) NOT NULL,
    service_id VARCHAR(50) NOT NULL,
    trip_id VARCHAR(50) UNIQUE NOT NULL,
    trip_headsign VARCHAR(255),
    trip_short_name VARCHAR(50),
    direction_id INTEGER,
    block_id VARCHAR(50),
    shape_id VARCHAR(50),
    wheelchair_accessible INTEGER DEFAULT 0,
    bikes_allowed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transport.stop_times (
    id SERIAL PRIMARY KEY,
    trip_id VARCHAR(50) NOT NULL,
    arrival_time TIME,
    departure_time TIME,
    stop_id VARCHAR(50) NOT NULL,
    stop_sequence INTEGER NOT NULL,
    stop_headsign VARCHAR(255),
    pickup_type INTEGER DEFAULT 0,
    drop_off_type INTEGER DEFAULT 0,
    shape_dist_traveled DECIMAL(10, 2),
    timepoint INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transport.shapes (
    id SERIAL PRIMARY KEY,
    shape_id VARCHAR(50) NOT NULL,
    shape_pt_lat DECIMAL(10, 8) NOT NULL,
    shape_pt_lon DECIMAL(11, 8) NOT NULL,
    shape_pt_sequence INTEGER NOT NULL,
    shape_dist_traveled DECIMAL(10, 2),
    geom GEOMETRY(POINT, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_stops_geom ON transport.stops USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_stops_stop_id ON transport.stops (stop_id);
CREATE INDEX IF NOT EXISTS idx_routes_route_id ON transport.routes (route_id);
CREATE INDEX IF NOT EXISTS idx_trips_trip_id ON transport.trips (trip_id);
CREATE INDEX IF NOT EXISTS idx_trips_route_id ON transport.trips (route_id);
CREATE INDEX IF NOT EXISTS idx_stop_times_trip_id ON transport.stop_times (trip_id);
CREATE INDEX IF NOT EXISTS idx_stop_times_stop_id ON transport.stop_times (stop_id);
CREATE INDEX IF NOT EXISTS idx_shapes_shape_id ON transport.shapes (shape_id);
CREATE INDEX IF NOT EXISTS idx_shapes_geom ON transport.shapes USING GIST (geom);

-- Create triggers to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_stops_updated_at BEFORE UPDATE ON transport.stops FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_routes_updated_at BEFORE UPDATE ON transport.routes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_trips_updated_at BEFORE UPDATE ON transport.trips FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA transport TO transport_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA transport TO transport_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA transport TO transport_user;

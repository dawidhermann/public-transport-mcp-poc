"""
Sample Apache Beam pipeline for processing public transport data.
This pipeline demonstrates reading data, transforming it, and writing to both PostGIS and Neo4j.
"""

import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.options.pipeline_options import PipelineOptions
import json
import logging
import psycopg2
from neo4j import GraphDatabase
from typing import Dict, Any, List
from apache_beam.io import ReadFromCsv
from datetime import datetime


class DatabaseConfig:
    """Configuration for database connections"""

    POSTGIS_CONFIG = {
        "host": "postgis",
        "port": 5432,
        "database": "transport_db",
        "user": "transport_user",
        "password": "transport_pass",
    }

    NEO4J_CONFIG = {
        "uri": "bolt://neo4j:7687",
        "user": "neo4j",
        "password": "transport_pass",
    }


# class TransformStopData(beam.DoFn):
#     """Transform raw stop data into structured format"""

#     def process(self, element):
#         try:
#             # Assume element is a dictionary with stop data
#             stop_data = {
#                 "stop_id": element.get("stop_id"),
#                 "stop_name": element.get("stop_name"),
#                 "stop_lat": float(element.get("stop_lat", 0)),
#                 "stop_lon": float(element.get("stop_lon", 0)),
#                 "location_type": int(element.get("location_type", 0)),
#             }

#             # Add geospatial point
#             if stop_data["stop_lat"] and stop_data["stop_lon"]:
#                 stop_data["geom"] = (
#                     f"POINT({stop_data['stop_lon']} {stop_data['stop_lat']})"
#                 )

#             yield stop_data

#         except Exception as e:
#             logging.error(f"Error transforming stop data: {e}")


def transform_stop_data(element):
    """Transform raw stop data into structured format"""

    print(f"Transforming element: {element}")  # Debugging line
    try:
        # Assume element is a dictionary with stop data
        stop_data = {
            "stop_id": element.get("stop_id"),
            "stop_name": element.get("stop_name"),
            "stop_lat": float(element.get("stop_lat", 0)),
            "stop_lon": float(element.get("stop_lon", 0)),
            "location_type": int(element.get("location_type", 0)),
        }

        # Add geospatial point
        if stop_data["stop_lat"] and stop_data["stop_lon"]:
            stop_data["geom"] = (
                f"POINT({stop_data['stop_lat']} {stop_data['stop_lon']})"
            )

        return stop_data

    except Exception as e:
        logging.error(f"Error transforming stop data: {e}")
        return {}


def transform_stop_times_data(element: Dict[str, Any]) -> Dict[str, Any]:
    """Transform raw stop times data into structured format"""
    try:
        # Assume element is a dictionary with stop times data
        stop_times_data = {
            "trip_id": element.get("trip_id"),
            "arrival_time": element.get("arrival_time"),
            "departure_time": element.get("departure_time"),
            "stop_id": element.get("stop_id"),
            "stop_sequence": int(element.get("stop_sequence", 0)),
        }

        return stop_times_data

    except Exception as e:
        logging.error(f"Error transforming stop times data: {e}")
        return {}


def transform_routes_data(element: Dict[str, Any]) -> Dict[str, Any]:
    """Transform raw routes data into structured format"""
    try:
        # Assume element is a dictionary with routes data
        route_data = {
            "route_id": element.get("route_id"),
            "route_name": element.get("route_name"),
            "route_type": int(element.get("route_type", 0)),
            "agency_id": element.get("agency_id"),
            "route_color": element.get("route_color", ""),
            "route_text_color": element.get("route_text_color", ""),
        }
        return route_data
    except Exception as e:
        logging.error(f"Error transforming routes data: {e}")
        return {}


def traansform_trips_data(element: Dict[str, Any]) -> Dict[str, Any]:
    """Transform raw trips data into structured format"""
    try:
        # Assume element is a dictionary with trips data
        trip_data = {
            "trip_id": element.get("trip_id"),
            "route_id": element.get("route_id"),
            "service_id": element.get("service_id"),
            "trip_headsign": element.get("trip_headsign", ""),
            "direction_id": int(element.get("direction_id", 0)),
            "block_id": element.get("block_id", ""),
            "shape_id": element.get("shape_id", ""),
        }
        return trip_data
    except Exception as e:
        logging.error(f"Error transforming trips data: {e}")
        return {}


class WriteToPostGIS(beam.DoFn):
    """Write transformed data to PostGIS database"""

    def __init__(self):
        self.connection = None

    def setup(self):
        """Setup database connection"""
        try:
            self.connection = psycopg2.connect(**DatabaseConfig.POSTGIS_CONFIG)
            logging.info("Connected to PostGIS database")
        except Exception as e:
            logging.error(f"Failed to connect to PostGIS: {e}")

    def process(self, element):
        if not self.connection:
            return

        try:
            cursor = self.connection.cursor()

            # Insert stop data
            insert_query = """
                INSERT INTO transport.stops (stop_id, stop_name, stop_lat, stop_lon, location_type, geom)
                VALUES (%(stop_id)s, %(stop_name)s, %(stop_lat)s, %(stop_lon)s, %(location_type)s, ST_GeomFromText(%(geom)s, 4326))
                ON CONFLICT (stop_id) DO UPDATE SET
                    stop_name = EXCLUDED.stop_name,
                    stop_lat = EXCLUDED.stop_lat,
                    stop_lon = EXCLUDED.stop_lon,
                    location_type = EXCLUDED.location_type,
                    geom = EXCLUDED.geom,
                    updated_at = CURRENT_TIMESTAMP;
            """

            cursor.execute(insert_query, element)
            self.connection.commit()

            yield element

        except Exception as e:
            logging.error(f"Error writing to PostGIS: {e}")
            if self.connection:
                self.connection.rollback()

    def teardown(self):
        """Clean up database connection"""
        if self.connection:
            self.connection.close()


class WriteToNeo4j(beam.DoFn):
    """Write transformed data to Neo4j graph database"""

    def __init__(self):
        self.driver = None

    def setup(self):
        """Setup Neo4j connection"""
        try:
            self.driver = GraphDatabase.driver(
                DatabaseConfig.NEO4J_CONFIG["uri"],
                auth=(
                    DatabaseConfig.NEO4J_CONFIG["user"],
                    DatabaseConfig.NEO4J_CONFIG["password"],
                ),
            )
            logging.info("Connected to Neo4j database")
        except Exception as e:
            logging.error(f"Failed to connect to Neo4j: {e}")

    def process(self, element):
        if not self.driver:
            return

        try:
            with self.driver.session() as session:
                # Create or update stop node
                query = """
                    MERGE (s:Stop {stop_id: $stop_id})
                    SET s.name = $stop_name,
                        s.latitude = $stop_lat,
                        s.longitude = $stop_lon,
                        s.location_type = $location_type,
                        s.updated_at = datetime()
                    RETURN s
                """

                session.run(query, element)
                yield element

        except Exception as e:
            logging.error(f"Error writing to Neo4j: {e}")

    def teardown(self):
        """Clean up Neo4j connection"""
        if self.driver:
            self.driver.close()


class WriteTripsToNeo4j(beam.DoFn):
    """Write trips data to Neo4j graph database"""

    def __init__(self):
        self.driver = None

    def setup(self):
        """Setup Neo4j connection"""
        try:
            self.driver = GraphDatabase.driver(
                DatabaseConfig.NEO4J_CONFIG["uri"],
                auth=(
                    DatabaseConfig.NEO4J_CONFIG["user"],
                    DatabaseConfig.NEO4J_CONFIG["password"],
                ),
            )
            logging.info("Connected to Neo4j database")
        except Exception as e:
            logging.error(f"Failed to connect to Neo4j: {e}")

    def process(self, element):
        if not self.driver:
            return

        try:
            with self.driver.session() as session:
                # Create or update trip node
                # query = """
                #     MERGE (t:Trip {trip_id: $trip_id})
                #     SET t.route_id = $route_id,
                #         t.service_id = $service_id,
                #         t.trip_headsign = $trip_headsign,
                #         t.direction_id = $direction_id,
                #         t.block_id = $block_id,
                #         t.shape_id = $shape_id,
                #         t.updated_at = datetime()
                #     RETURN t
                # """
                query = """
                    MATCH (n:Trip {trip_id: $trip_id})
                    MATCH (r: Route {route_id: $route_id})
                    CREATE (r)<-[:IN_ROUTE{route_id: $route_id}]-(n)
                    RETURN n, r;
                """

                session.run(query, element)
                yield element

        except Exception as e:
            logging.error(f"Error writing trips to Neo4j: {e}")

    def teardown(self):
        """Clean up Neo4j connection"""
        if self.driver:
            self.driver.close()


class WriteRoutesToNeo4j(beam.DoFn):
    """Write routes data to Neo4j graph database"""

    def __init__(self):
        self.driver = None

    def setup(self):
        """Setup Neo4j connection"""
        try:
            self.driver = GraphDatabase.driver(
                DatabaseConfig.NEO4J_CONFIG["uri"],
                auth=(
                    DatabaseConfig.NEO4J_CONFIG["user"],
                    DatabaseConfig.NEO4J_CONFIG["password"],
                ),
            )
            logging.info("Connected to Neo4j database")
        except Exception as e:
            logging.error(f"Failed to connect to Neo4j: {e}")

    def process(self, element):
        if not self.driver:
            return

        try:
            with self.driver.session() as session:
                # Create or update route node
                query = """
                    MERGE (r:Route {route_id: $route_id})
                    SET r.name = $route_name,
                        r.type = $route_type,
                        r.agency_id = $agency_id,
                        r.color = $route_color,
                        r.text_color = $route_text_color,
                        r.updated_at = datetime()
                    RETURN r
                """

                session.run(query, element)
                yield element

        except Exception as e:
            logging.error(f"Error writing routes to Neo4j: {e}")

    def teardown(self):
        """Clean up Neo4j connection"""
        if self.driver:
            self.driver.close()


class WriteStopTimesDataToNeo4j(beam.DoFn):
    """Write stop times data to Neo4j graph database"""

    def __init__(self):
        self.driver = None

    def setup(self):
        """Setup Neo4j connection"""
        try:
            self.driver = GraphDatabase.driver(
                DatabaseConfig.NEO4J_CONFIG["uri"],
                auth=(
                    DatabaseConfig.NEO4J_CONFIG["user"],
                    DatabaseConfig.NEO4J_CONFIG["password"],
                ),
            )
            logging.info("Connected to Neo4j database")
        except Exception as e:
            logging.error(f"Failed to connect to Neo4j: {e}")

    def process(self, batch_data):
        if not self.driver:
            return

        try:
            with self.driver.session() as session:
                # Create or update stop time node
                query = """
                    UNWIND $batch as row
                    MATCH (s:Stop {stop_id: row.stop_id}), (t:Trip {trip_id: row.trip_id})-[:IN_ROUTE]->(r:Route)
                    MERGE (r)-[st:STOP_TIME{id: row.stop_id}]->(s)
                    SET st.sequence = row.stop_sequence
                """

                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logging.info(
                    f"Writing batch of {len(batch_data)} elements at {current_time}"
                )

                session.run(query, {"batch": batch_data})
                # yield element

        except Exception as e:
            logging.error(f"Error writing stop times to Neo4j: {e}")

    def teardown(self):
        """Clean up Neo4j connection"""
        if self.driver:
            self.driver.close()


def run_pipeline(input_file: str = None):
    """Run the Apache Beam pipeline"""

    pipeline_options = PipelineOptions(
        [
            "--job_name=my-beam-job",
            "--runner=DirectRunner",
            "--project=transport-project",
        ]
    )

    with beam.Pipeline(options=pipeline_options) as pipeline:

        # Create pipeline
        stops_data = (
            pipeline
            | "Create Sample Data"
            >> ReadFromCsv(
                "data/stops.csv",
                header=0,
            )
            | "Convert to Dict" >> beam.Map(lambda row: row._asdict())
            | "Transform Stop Data" >> beam.Map(transform_stop_data)
        )

        # # Transform stop times data
        # stop_times_data = (
        #     pipeline
        #     | "Read Stop Times Data" >> ReadFromCsv("data/stop_times.csv", header=0)
        #     | "Convert to Dict" >> beam.Map(lambda row: row._asdict())
        #     | "Transform Stop Times Data" >> beam.Map(transform_stop_times_data)
        # )

        # # Transform routes data
        # routes_data = (
        #     pipeline
        #     | "Read Routes Data" >> ReadFromCsv("data/routes.csv", header=0)
        #     | "Convert to Dict" >> beam.Map(lambda row: row._asdict())
        #     | "Transform Routes Data" >> beam.Map(transform_routes_data)
        # )

        # # Transform trips data
        # trips_data = (
        #     pipeline
        #     | "Read Trips Data"
        #     >> ReadFromCsv(
        #         "data/trips.csv",
        #         header=0,
        #     )
        #     | "Convert to Dict" >> beam.Map(lambda row: row._asdict())
        #     | "Transform Trips Data" >> beam.Map(traansform_trips_data)
        # )

        # Write to PostGIS
        (stops_data | "Write to PostGIS" >> beam.ParDo(WriteToPostGIS()))

        # # Write to Neo4j
        # (stops_data | "Write to Neo4j" >> beam.ParDo(WriteToNeo4j()))
        # (trips_data | "Write to Neo4j" >> beam.ParDo(WriteTripsToNeo4j()))
        # (
        #     stop_times_data
        #     | "Batching" >> beam.BatchElements(min_batch_size=100, max_batch_size=1000)
        #     | "Write Stop Times to Neo4j" >> beam.ParDo(WriteStopTimesDataToNeo4j())
        # )
        # (routes_data | "Write Routes to Neo4j" >> beam.ParDo(WriteRoutesToNeo4j()))


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    run_pipeline()

# Public Transport MCP PoC

This project demonstrates a Model Context Protocol (MCP) proof of concept for public transport data processing using Apache Beam, PostGIS, and Neo4j.

## Architecture

- **PostGIS**: Geospatial database for storing stop locations, routes, and spatial data
- **Neo4j**: Graph database for modeling transport network relationships
- **Apache Beam**: Data processing pipeline for ETL operations
- **Jupyter Lab**: Interactive development environment

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB of available RAM

### Setup

1. Clone or navigate to the project directory:

   ```bash
   cd /Users/dawidhermann/projects/scout/public-transport-mcp-poc
   ```

2. Start the services:

   ```bash
   docker-compose up -d
   ```

3. Check service status:
   ```bash
   docker-compose ps
   ```

### Service URLs

- **PostGIS**: `localhost:5432`

  - Database: `transport_db`
  - Username: `transport_user`
  - Password: `transport_pass`

- **Neo4j Browser**: `http://localhost:7474`

  - Username: `neo4j`
  - Password: `transport_pass`

- **Jupyter Lab**: `http://localhost:8889`

  - Token: `transport_token`

- **Beam Interactive**: `http://localhost:8888`

### Database Connections

#### PostGIS Connection String

```
postgresql://transport_user:transport_pass@localhost:5432/transport_db
```

#### Neo4j Connection

```
bolt://localhost:7687
Username: neo4j
Password: transport_pass
```

## Project Structure

```
.
├── docker-compose.yml          # Main Docker Compose configuration
├── requirements.txt            # Python dependencies
├── .env                       # Environment variables
├── init-scripts/              # Database initialization scripts
│   └── 01-init-postgis.sql    # PostGIS schema setup
├── beam-pipelines/            # Apache Beam pipeline code
│   └── transport_pipeline.py  # Sample transport data pipeline
├── beam-data/                 # Data files for processing
├── notebooks/                 # Jupyter notebooks for analysis
└── README.md                  # This file
```

## Running the Sample Pipeline

1. Access the Beam container:

   ```bash
   docker-compose exec beam-python bash
   ```

2. Run the sample pipeline:
   ```bash
   cd /app
   python pipelines/transport_pipeline.py
   ```

## Development Workflow

### Using Jupyter Lab

1. Open Jupyter Lab at `http://localhost:8889`
2. Use token: `transport_token`
3. Navigate to the `work` directory
4. Create new notebooks for data analysis

### Database Management

#### PostGIS

Connect using any PostgreSQL client or from within containers:

```bash
docker-compose exec postgis psql -U transport_user -d transport_db
```

#### Neo4j

Access the Neo4j browser at `http://localhost:7474` or use Cypher shell:

```bash
docker-compose exec neo4j cypher-shell -u neo4j -p transport_pass
```

## Sample Queries

### PostGIS - Find nearby stops

```sql
SELECT stop_name, stop_lat, stop_lon
FROM transport.stops
WHERE ST_DWithin(
    geom,
    ST_SetSRID(ST_MakePoint(13.4050, 52.5200), 4326),
    1000  -- 1km radius
);
```

### Neo4j - Graph relationships

```cypher
MATCH (s:Stop)
RETURN s.name, s.latitude, s.longitude
LIMIT 10;
```

## Stopping Services

To stop all services:

```bash
docker-compose down
```

To stop and remove volumes (⚠️ this will delete all data):

```bash
docker-compose down -v
```

## Troubleshooting

### Check service logs

```bash
docker-compose logs [service-name]
```

### Restart a specific service

```bash
docker-compose restart [service-name]
```

### Check resource usage

```bash
docker stats
```

## Next Steps

1. Load real GTFS (General Transit Feed Specification) data
2. Implement route optimization algorithms
3. Add real-time data processing capabilities
4. Create visualization dashboards
5. Implement MCP server for external integrations

## Contributing

1. Add your pipeline code to `beam-pipelines/`
2. Place sample data in `beam-data/`
3. Create analysis notebooks in `notebooks/`
4. Update documentation as needed

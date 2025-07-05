# Makefile for Public Transport MCP PoC

.PHONY: help up down logs status clean restart pipeline test

# Default target
help:
	@echo "Available commands:"
	@echo "  up         - Start all services"
	@echo "  down       - Stop all services"
	@echo "  logs       - Show logs for all services"
	@echo "  status     - Show status of all services"
	@echo "  clean      - Stop services and remove volumes (⚠️  deletes data)"
	@echo "  restart    - Restart all services"
	@echo "  pipeline   - Run the sample Beam pipeline"
	@echo "  test       - Test database connections"
	@echo "  psql       - Connect to PostGIS database"
	@echo "  cypher     - Connect to Neo4j cypher shell"

# Start all services
up:
	docker-compose up -d
	@echo "Services starting... Check status with 'make status'"
	@echo ""
	@echo "Service URLs:"
	@echo "  PostGIS:    localhost:5432"
	@echo "  Neo4j:      http://localhost:7474"
	@echo "  Jupyter:    http://localhost:8889 (token: transport_token)"
	@echo "  Beam:       http://localhost:8888"

# Stop all services
down:
	docker-compose down

# Show logs for all services
logs:
	docker-compose logs -f

# Show status of all services
status:
	docker-compose ps

# Stop services and remove volumes (deletes data)
clean:
	docker-compose down -v
	docker system prune -f

# Restart all services
restart:
	docker-compose restart

# Run the sample Beam pipeline
pipeline:
	docker-compose exec beam-python python /app/pipelines/transport_pipeline.py

# Test database connections
test:
	@echo "Testing PostGIS connection..."
	docker-compose exec postgis pg_isready -U transport_user -d transport_db
	@echo "Testing Neo4j connection..."
	docker-compose exec neo4j cypher-shell -u neo4j -p transport_pass "RETURN 'Connection successful' as status;"

# Connect to PostGIS database
psql:
	docker-compose exec postgis psql -U transport_user -d transport_db

# Connect to Neo4j cypher shell
cypher:
	docker-compose exec neo4j cypher-shell -u neo4j -p transport_pass

# Show service-specific logs
logs-postgis:
	docker-compose logs -f postgis

logs-neo4j:
	docker-compose logs -f neo4j

logs-beam:
	docker-compose logs -f beam-python

logs-jupyter:
	docker-compose logs -f jupyter-lab

install-mcp:
	fastmcp install ./src/server.py --with googlemaps --with load_dotenv --with psycopg2-binary --with neo4j

run-mcp:
	uv run fastmcp run ./src/server.py

debug-mcp:
	npx @modelcontextprotocol/inspector uv run --with fastmcp --with googlemaps --with load_dotenv --with psycopg2-binary fastmcp run /Users/dawidhermann/projects/scout/public-transport-mcp-poc/public-transport-mcp/src/server.py
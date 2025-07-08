from fastmcp import FastMCP, Context
from dotenv import load_dotenv
from maps.maps_client import MapsClient
from db.geolocation.postgis_client import PostgisClient
from db.graph.graph_client import GraphClient
import os

load_dotenv(override=True)


mcp: FastMCP = FastMCP(name="public-transport-mcp", version="0.1.0")
postgis_client: PostgisClient = PostgisClient(
    user=os.getenv("POSTGRES_USER", default="postgres"),
    password=os.getenv("POSTGRES_PASSWORD", default="postgres"),
    db_name=os.getenv("POSTGRES_DB", default="postgres"),
    host=os.getenv("POSTGRES_HOST", default="localhost"),
    port=int(os.getenv("POSTGRES_PORT", default="5432")),
)
neo4j_client: GraphClient = GraphClient(
    uri=os.getenv("NEO4J_URI", default="bolt://localhost:7687"),
    user=os.getenv("NEO4J_USER", default="neo4j"),
    password=os.getenv("NEO4J_PASSWORD", default="neo4j"),
)


@mcp.tool("address_geoconverter")
async def address_geoconverter(address: str, ctx: Context):
    """
    Converts an address to geolocation coordinates and retrieves nearby stops.

    :param address: The address of the office which is trip destination.
    :return: A list of dictionaries with latitude and longitude and name of stops where user can find house.
    Use geolocation to find street or city names and return it to user as proposal.
    Use stops's latitude and longitude and return string https://www.immobilienscout24.de/Suche/radius/wohnung-mieten?geocoordinates={latitude}%3B{longitude}%3B2.0 with replaced {latitude} and {longitude} with stop's latitude and longitude.
    """
    gmaps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not gmaps_api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY is not set in the environment variables.")
    client = MapsClient(api_key=gmaps_api_key)
    address_geolocation = client.get_geolocation(address)
    await ctx.info(
        f"Address '{address}' converted to coordinates: {address_geolocation.lat}, {address_geolocation.lng}"
    )
    result = await postgis_client.get_points_with_distance(
        lat=address_geolocation.lat,
        lng=address_geolocation.lng,
        distance=1000,
        ctx=ctx,
        limit=10,
    )
    stops = await neo4j_client.get_first_stop(result[1].get("stop_id"), ctx)
    return stops

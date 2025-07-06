from fastmcp import FastMCP, Context
import psycopg2
import re

pattern = r"POINT\(([0-9.-]+)\s+([0-9.-]+)\)"


class PostgisClient:

    def __init__(
        self, user: str, password: str, db_name: str, host: str, port: int = 5432
    ):
        """
        Initialize the PostgisClient with the provided connection parameters.
        """
        conn = psycopg2.connect(
            user=user, password=password, database=db_name, host=host, port=port
        )
        self.conn = conn

    async def get_points_with_distance(
        self, lat: float, lng: float, distance: float, ctx: Context, limit: int = 100
    ) -> list[dict[str, float]]:
        """
        Get points within a certain distance from a given latitude and longitude.

        :param lat: Latitude of the center point.
        :param lng: Longitude of the center point.
        :param distance: Distance in meters.
        :param limit: Maximum number of points to return.
        :return: A list of dictionaries with latitude and longitude of points within the distance.
        """
        with self.conn.cursor() as cursor:
            query = """
                SELECT stop_id, ST_AsText(geom) AS geom
                FROM transport.stops
                WHERE ST_DWithin(
                    geom::geography,
                    ST_MakePoint(%s, %s)::geography,
                    %s
                )
                LIMIT %s;
            """
            cursor.execute(query, (lat, lng, distance, limit))
            results = cursor.fetchall()
            await ctx.info(
                f"Found {len(results)} points within {distance} meters of ({lat}, {lng})"
            )
            await ctx.info(f"{results}")
            point_list = []
            for point in results:
                match = re.match(pattern, point[1])
                if not match:
                    raise ValueError(f"Invalid point format: {point[1]}")
                await ctx.info(f"Point found: {point[1]}")
                point_list.append(
                    {
                        "stop_id": point[0],
                        "lat": float(match.group(1)),
                        "lng": float(match.group(2)),
                    }
                )
            await ctx.info(f"Returning {len(point_list)} points")
            return point_list

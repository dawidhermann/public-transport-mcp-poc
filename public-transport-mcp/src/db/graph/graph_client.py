from fastmcp import FastMCP, Context
from neo4j import GraphDatabase


class GraphClient:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    async def get_first_stop(self, stop_id: str, ctx: Context):
        await ctx.info(f"Getting first stop for stop_id: {stop_id}")
        query = """
          MATCH (:Stop{stop_id: $stop_id})<-[:STOP_TIME]-(r:Route),
          (s:Stop)<-[st:STOP_TIME{sequence: 0}]-(r)
          RETURN s;
        """
        stops = []
        with self.driver.session() as session:
            result = session.run(query, {"stop_id": stop_id})
            stops = []
            for record in result:
                stop_node = record["s"]
                stop_dict = {
                    "stop_id": stop_node.get("stop_id"),
                    "latitude": stop_node.get("latitude"),
                    "longitude": stop_node.get("longitude"),
                    "name": stop_node.get(
                        "name"
                    ),  # opcjonalnie, jeśli potrzebujesz nazwy
                }
                stops.append(stop_dict)
            return stops

    # def run_query(self, query: str, parameters: dict = None):
    #     with self.driver.session() as session:
    #         result = session.run(query, parameters or {})
    #         return [record for record in result]  # Return all records as a list

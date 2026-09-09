from mcp.server.mcpserver import MCPServer
from dotenv import load_dotenv
import os
import psycopg
from psycopg import Connection

load_dotenv()

mcp = MCPServer("chinook")

def get_connection():
    PGHOST = os.getenv("PGHOST")
    PGPORT = os.getenv("PGPORT")
    PGUSER = os.getenv("PGUSER")
    PGPASSWORD = os.getenv("PGPASSWORD")
    PGDATABASE = os.getenv("PGDATABASE")

    return psycopg.connect(host=PGHOST, port=PGPORT, user=PGUSER, password=PGPASSWORD, dbname=PGDATABASE)

@mcp.tool()
def contar_tracks() -> int:
    """
    Returns the number of total songs in the database.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM track;")
            return cur.fetchone()[0]

@mcp.tool()
def tracks_by_genre(genre: str) -> list[str]:
    """
    Returns a list with the tracks associated with a certain genre.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT track.name AS track_name FROM genre JOIN track ON track.genre_id = genre.genre_id WHERE genre.name = %s;", (genre,))
            results = cur.fetchall()
            return [result[0] for result in results]

if __name__ == "__main__":
    mcp.run()
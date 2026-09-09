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

@mcp.tool()
def top_20_artists() -> list[dict]:
    """
    Returns a list with the top 20 artists with more tracks.
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT artist.name AS artist_name, COUNT(*) AS track_count FROM artist JOIN album ON artist.artist_id = album.artist_id JOIN track ON track.album_id = album.album_id GROUP BY artist.name ORDER BY track_count DESC LIMIT 20;")
            results = cur.fetchall()
            return [{"artists": result[0], "tracks": result[1]} for result in results]

@mcp.tool()
def sales_by_country() -> list[dict]:
    """
    Returns a list with the total sales by country in descending order.
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT billing_country, SUM(total) as sales FROM invoice GROUP BY billing_country ORDER BY sales DESC;")
            results = cur.fetchall()
            return [{"country": result[0], "sales": result[1]} for result in results]

@mcp.tool()
def list_schema() -> list[dict]:
    """
    Returns a list with table and column names of the tables of the database.
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = 'public' ORDER BY table_name, ordinal_position LIMIT 10;")
            results = cur.fetchall()
            return [{"table": result[0], "column": result[1]} for result in results]
        
if __name__ == "__main__":
    mcp.run()
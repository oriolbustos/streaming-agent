from mcp.server.mcpserver import MCPServer
from dotenv import load_dotenv
import os
import psycopg
from typing import Optional

load_dotenv()

mcp = MCPServer("chinook")

def get_connection(readonly:bool=False):
    PGHOST = os.getenv("PGHOST")
    PGPORT = os.getenv("PGPORT")
    PGUSER = os.getenv("PGUSER_RO" if readonly else "PGUSER")
    PGPASSWORD = os.getenv("PGPASSWORD_RO" if readonly else "PGPASSWORD")
    PGDATABASE = os.getenv("PGDATABASE")

    return psycopg.connect(host=PGHOST, port=PGPORT, user=PGUSER, password=PGPASSWORD, dbname=PGDATABASE)

def run_query(sql, params=None, limit:Optional[int]=None, readonly=False):
    with get_connection(readonly) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            columns = [description[0] for description in cur.description]
            rows = cur.fetchmany(limit) if limit else cur.fetchall()
            return [dict(zip(columns, row)) for row in rows]

@mcp.tool()
def contar_tracks() -> list[dict]:
    """Returns the number of total songs in the database."""
    return run_query("SELECT COUNT(*) FROM track;")

@mcp.tool()
def tracks_by_genre(genre: str) -> list[dict]:
    """Returns a list with the tracks associated with a certain genre."""
    return run_query("SELECT track.name AS track_name FROM genre JOIN track ON track.genre_id = genre.genre_id WHERE genre.name = %s;", (genre,))

@mcp.tool()
def top_20_artists() -> list[dict]:
    """Returns a list with the top 20 artists with more tracks."""
    return run_query("SELECT artist.name AS artist_name, COUNT(*) AS track_count FROM artist JOIN album ON artist.artist_id = album.artist_id JOIN track ON track.album_id = album.album_id GROUP BY artist.name ORDER BY track_count DESC LIMIT 20;")

@mcp.tool()
def sales_by_country() -> list[dict]:
    """Returns a list with the total sales by country in descending order."""
    return run_query("SELECT billing_country, SUM(total) as sales FROM invoice GROUP BY billing_country ORDER BY sales DESC;")

@mcp.tool()
def list_schema() -> list[dict]:
    """
    Returns a list with table and column names of the tables of the database.
    """
    return run_query("SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = 'public' ORDER BY table_name, ordinal_position LIMIT 10;")

@mcp.tool()
def run_readonly_sql(sql:str):
    """Execute a custom Read-Only SQL query in PostgreSQL. Executing with user with only SELECT's permissions."""
    sql_check = sql.strip().lower().rstrip(";")
    condition1 = "select" != sql_check.split(" ")[0]
    condition2 = ";" in sql_check
    if condition1 or condition2:
        raise Exception("Not permitted query commands")
    
    return run_query(sql, limit=100, readonly=True)

if __name__ == "__main__":
    mcp.run()
# Add lifespan support for startup/shutdown with strong typing
import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# from fake_database import Database  # Replace with your actual DB type
import sqlite3

database_db="/home/ailab/files/mcpserver-python-sdk-nai/sqlite3/test_database.sqlite"

from mcp.server.fastmcp import Context, FastMCP

# Create a named server
mcp = FastMCP("My First App")

# Specify dependencies for deployment and development
mcp = FastMCP("My First App", dependencies=["pandas", "numpy"])


@mcp.resource("schema://main")
def get_schema() -> str:
    """Provide the database schema as a resource"""
    conn = sqlite3.connect(database_db)
    schema = conn.execute("SELECT sql FROM sqlite_master WHERE type='table'").fetchall() # [NOTE][TODO] replace `sqlite_master` with correct DATABASE NAME = ???
    return "\n".join(sql[0] for sql in schema if sql[0])


@mcp.tool()
def query_data(sql: str) -> str:
    """Execute SQL queries safely"""
    conn = sqlite3.connect(database_db)
    try:
        result = conn.execute(sql).fetchall()
        return "\n".join(str(row) for row in result)
    except Exception as e:
        return f"Error: {str(e)}"


# Fix app_lifespan to use synchronous SQLite connection
@dataclass
class AppContext:
    db: sqlite3.Connection


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""
    # Initialize on startup
    # db = await sqlite3.connect(database_db)
    # try:
    #     yield AppContext(db=db)
    # finally:
    #     # Cleanup on shutdown
    #     await db.disconnect()
    db = sqlite3.connect(database_db)  # Use synchronous connection
    try:
        # Record metrics for startup
        import time
        start_time = time.time()
        db = sqlite3.connect(database_db)  # Use synchronous connection
        yield AppContext(db=db) # [TODO] move sqlite3.connect(...) here s.t. startup_duration != 0 ???
        end_time = time.time()
        startup_duration = end_time - start_time
        print(f"\n[INFO] App Lifespan Startup Duration: {startup_duration:.8f} seconds")
        logger.info(f"\n[INFO] App Lifespan Startup Duration: {startup_duration:.8f} seconds")
    finally:
        # Cleanup on shutdown
        db.close()
        # Record metrics for shutdown
        shutdown_time = time.time()
        shutdown_duration = shutdown_time - start_time
        print(f"\n[INFO] App Lifespan Shutdown Duration: {shutdown_duration:.8f} seconds")
        logger.info(f"\n[INFO] App Lifespan Shutdown Duration: {shutdown_duration:.8f} seconds")


# Function to run the app_lifespan generator and print its context
async def run_app_lifespan():
    print("\n[INFO] Getting App Lifespan...")
    async with app_lifespan(mcp) as context:
        print("\n[INFO] App Lifespan context results:")
        print(f"Database Name: {context.db}")  # Example: Print database name or other context attributes


# Pass lifespan to server
mcp = FastMCP("My First App", lifespan=app_lifespan)


# Access type-safe lifespan context in tools
@mcp.tool()
def query_db(ctx: Context) -> str:
    """Tool that uses initialized resources"""
    db = ctx.request_context.lifespan_context.db
    return db.query()


# Example usage
logger.info("Started MCP app: %s", mcp)
logger.info("Getting SQLite3 DB schema...")
schema = get_schema()
logger.info("SQLite3 DB schema:\n%s", schema)

print("\n[INFO] started MCP app", mcp)
print("\n[INFO] Getting SQLite3 DB schema...")
schema = get_schema()
print("\n[INFO] SQLite3 DB schema: ", schema)
sql_query = "SELECT id FROM users"
ids = query_data(sql_query)
logger.info("SQLite3 DB TABLE users contain ids:\n%s", ids)
print("\n[INFO] SQLite3 DB TABLE users contain ids = ", ids)

sql_query_0 = "SELECT name FROM users GROUP BY id"
names = query_data(sql_query_0)
print("\n[INFO] SQLite3 DB TABLE users contain names = ", names)
logger.info("SQLite3 DB TABLE users contain names:\n%s", names)

sql_query_1 = "SELECT email, address FROM users GROUP BY id"
email_address = query_data(sql_query_1)
print("\n[INFO] SQLite3 DB TABLE users contain email_address = ", email_address)
logger.info("SQLite3 DB TABLE users contain email_address:\n%s", email_address)

print("\n[INFO] Getting App Lifespan...")
logger.info("Getting App Lifespan...")
app_life = app_lifespan(mcp)
logger.debug("App Lifespan results: %s", app_life)

# app_life = app_lifespan(mcp)
# print("\n[DEBUG] App Lifespan results: ", app_life)

# Run the async function
asyncio.run(run_app_lifespan())


query_db

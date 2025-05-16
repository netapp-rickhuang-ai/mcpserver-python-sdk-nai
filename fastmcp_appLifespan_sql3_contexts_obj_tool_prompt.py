import asyncio
import logging
import sqlite3
import time
from collections.abc import AsyncIterator

# Add lifespan support for startup/shutdown with strong typing
from contextlib import asynccontextmanager
from dataclasses import dataclass

import httpx
from PIL import Image as PILImage

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.fastmcp.prompts import base  # Import base for prompts

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.info("\n[INFO] Starting FastMCP server for File Ingestion App...")

mcp = FastMCP(
    "File Ingestion App"
)  # [NOTE][TODO] add ANY dependencies=List["libraries"] ???


# Fix app_lifespan to reflect File Ingestion App contexts
@dataclass
class AppContext:
    files: list[str]  # List of file paths being processed
    start_time: float  # Start time of the app lifespan
    end_time: float = 0.0  # End time of the app lifespan (default to 0.0)


@mcp.tool()
async def long_task(files: list[str], ctx: Context) -> str:
    """Process multiple files with progress tracking"""
    for i, file in enumerate(files):
        """# await ctx.info(f"Processing {file}")
        # await ctx.report_progress(i + 1, len(files))  # Report progress (1-based index)
        # # Simulate reading the file (replace with actual file reading logic)
        # with open(file, 'r') as f:
        #     data = f.read()
        # # data, mime_type = await ctx.read_resource(f"file://{file}")
        # ctx.info(f"\n[INFO] Finished processing {file}")
        # logger.info(f"\n[INFO] Finished processing {file}")"""
        # Use logging instead of ctx.info for testing outside a request
        logger.info(f"Processing {file}")
        # Simulate progress reporting
        logger.info(f"Progress: {i + 1}/{len(files)}")
        # Simulate reading the file (replace with actual file reading logic)
        with open(file) as f:
            data = f.read()
        logger.info(f"\n[INFO] Finished processing {file}")
        logger.info(f"\n[INFO] {file} contains data: {data} of type: ", type(data))
    return "Processing complete"


@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI given weight in kg and height in meters"""
    bmi = weight_kg / (height_m**2)
    logger.info(
        f"[INFO] Calculated BMI: {bmi:.2f} for weight: {weight_kg} kg and height: {height_m} m"
    )
    return bmi


@mcp.tool()
async def fetch_weather(city: str) -> str:
    """Fetch current weather for a city"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.weather.com/{city}")
        logger.info(
            f"[INFO] Fetched weather for city: {city}, Response: {response.text}"
        )
        return response.text


@mcp.prompt()
def review_code(code: str) -> str:
    """Prompt to review code"""
    review_message = f"Please review this code:\n\n{code}"
    logger.info(f"[INFO] Generated code review prompt: {review_message}")
    return review_message


@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    """Prompt to debug an error"""
    messages = [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]
    logger.info(f"[INFO] Generated debug error prompt for error: {error}")
    return messages


@mcp.tool()
def create_thumbnail_and_store(image_path: str, thumbnail_path: str) -> str:
    """Create a thumbnail from an image, save it to disk, and store info in the images table."""
    # Create thumbnail
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    img.save(thumbnail_path, format="PNG")
    img_bytes = img.tobytes()
    img_format = "png"
    # Save to SQLite
    db_path = "/Users/rickhuang/Documents/Snowflake/mcpserver-python-sdk-nai/test_database.sqlite"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT NOT NULL,
            thumbnail_path TEXT NOT NULL,
            data BLOB NOT NULL,
            format TEXT NOT NULL
        )
    """)
    cursor.execute(
        "INSERT INTO images (image_path, thumbnail_path, data, format) VALUES (?, ?, ?, ?)",
        (image_path, thumbnail_path, img_bytes, img_format),
    )
    conn.commit()
    conn.close()
    return f"Thumbnail for {image_path} created, saved to {thumbnail_path}, and stored in database."


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""
    # Initialize on startup
    start_time = time.time()
    files = []  # Initialize an empty list of files <-- [TODO][NOTE] should from function input 'server: FastMCP context' !!!
    try:
        # Yield the context with the list of files and start time
        yield AppContext(files=files, start_time=start_time)
        end_time = time.time()
        startup_duration = end_time - start_time
        print(f"\n[INFO] App Lifespan Startup Duration: {startup_duration:.8f} seconds")
        logger.info(
            f"\n[INFO] App Lifespan Startup Duration: {startup_duration:.8f} seconds"
        )
    finally:
        # Record metrics for shutdown
        shutdown_time = time.time()
        shutdown_duration = shutdown_time - start_time
        print(
            f"\n[INFO] App Lifespan Shutdown Duration: {shutdown_duration:.8f} seconds"
        )
        logger.info(
            f"\n[INFO] App Lifespan Shutdown Duration: {shutdown_duration:.8f} seconds"
        )


async def test_file_ingestion(files_path: str):
    async with app_lifespan(mcp) as context:
        context.files.append(files_path)  # Add the file path to the context
        # Use mcp.run_tool to execute the long_task tool within the request lifecycle
        result = await mcp.call_tool("long_task", {"files": context.files})
        print("\n[DEBUG] async function test_file_ingestion result = ", result)
        logger.info(f"\n[DEBUG] async function test_file_ingestion result = {result}")


# Function to run the app_lifespan generator and print its context
async def run_app_lifespan():
    print("\n[INFO] Getting App Lifespan...")
    async with app_lifespan(mcp) as context:
        print("\n[INFO] App Lifespan context results:")
        print(
            f"Read files: {context.files}"
        )  # Example: Print database name or other context attributes


# # Pass lifespan to server
# mcp = FastMCP("File Ingestion App", lifespan=app_lifespan)

# [Test] example usage
logger.info("\n[INFO] Testing File Ingestion App...")
file_path = "/Users/rickhuang/Library/CloudStorage/OneDrive-Personal/workspace-mac/llama_index/data/paul_graham_essay.txt"
# file_path="/home/ailab/files/llama_index/data/llama2_paper/source_files/source.txt"
# input_files = [file_path]
# long_task(input_files, Context)

# Run the test
asyncio.run(test_file_ingestion(file_path))
logger.info("\n[INFO] File Ingestion App asyncio.run completed.")

# Update the database path to a valid location
test_database = (
    "/Users/rickhuang/Documents/Snowflake/mcpserver-python-sdk-nai/test_database.sqlite"
)


# Function to process text and store in the database
async def process_and_store_text(file_path: str):
    async with app_lifespan(mcp) as context:
        # Read the text file
        with open(file_path) as file:
            text_content = file.read()

        # Connect to the database
        connection = sqlite3.connect(test_database)
        cursor = connection.cursor()

        # Ensure the `users` table exists before querying it
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
        """)
        logger.info("[INFO] Table 'users' created successfully (if it did not exist).")
        connection.commit()

        # Query the database
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        print("[INFO] Users in the database:")
        for row in rows:
            print(row)

        cursor.execute("""CREATE TABLE IF NOT EXISTS text (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL)
        """)
        print("[INFO] Table 'text' created successfully.")
        logger.info("[INFO] Table 'text' created successfully.")
        connection.commit()

        # cursor.execute("SELECT * FROM text")
        # txt_rows = cursor.fetchall()
        # print("[INFO] Text table in the database:")
        # for row in txt_rows:
        #     print(row)

        # Insert the text content into the `text` table [TODO] /fix table to insert!
        # cursor.execute("INSERT INTO text (content) VALUES (?)", (text_content,))

        cursor.execute("INSERT INTO text (content) VALUES (?)", (text_content,))
        logger.info("[INFO] INSERTed 'text' table: %s", text_content)
        print("[INFO] text_content inserted into 'text' table:", text_content)
        connection.commit()

        # Print and log the schema of the `text` table
        cursor.execute("PRAGMA table_info(text)")
        # cursor.execute("PRAGMA table_info(users)")
        schema = cursor.fetchall()
        print("[INFO] Schema of 'text' table:", schema)
        logger.info("[INFO] Schema of 'text' table: %s", schema)
        # print("[INFO] Schema of 'users' table:", schema)
        # logger.info("[INFO] Schema of 'users' table: %s", schema)

        # Close the connection
        connection.close()

        # Log the app lifespan for this step
        logger.info("[INFO] App lifespan for processing and storing text completed.")


# Example usage
asyncio.run(process_and_store_text(file_path))


# Example usage of tools and prompts
async def example_usage():
    logger.info("[INFO] Starting example usage of tools and prompts...")

    # Example: Calculate BMI
    weight = 70.0  # kg
    height = 1.75  # meters
    bmi = calculate_bmi(weight, height)
    logger.info(f"[INFO] Example BMI calculation result: {bmi:.2f}")

    # # Example: Fetch weather
    # city = "San Francisco"
    # weather = await fetch_weather(city)
    # logger.info(f"[INFO] Example weather fetch result for {city}: {weather}")

    # Example: Review code
    code_snippet = "def add(a, b):\n    return a + b"
    review = review_code(code_snippet)
    logger.info(f"[INFO] Example code review prompt: {review}")

    # Example: Debug error
    error_message = "IndexError: list index out of range"
    debug_messages = debug_error(error_message)
    logger.info(f"[INFO] Example debug error prompt messages: {debug_messages}")

    # Example: Create thumbnail and store in database
    image_path = "/Users/rickhuang/Documents/Snowflake/img/Insight_BRK-1384-2_sentimentAnalysis_page_1.jpg"  # Replace with a valid image path
    thumbnail_path = "/Users/rickhuang/Documents/Snowflake/img/Insight_BRK-1384-2_sentimentAnalysis_page_1_thumbnail.jpg"  # Replace with a valid thumbnail path
    create_thumbnail_and_store(image_path, thumbnail_path)
    logger.info(
        f"[INFO] Example thumbnail creation and storage result: {thumbnail_path}"
    )


# Run the example usage
asyncio.run(example_usage())

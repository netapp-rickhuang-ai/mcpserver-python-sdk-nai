from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("Test App")


@mcp.tool()
async def long_task(files: list[str], ctx: Context) -> str:
    """Process multiple files with progress tracking"""
    for i, file in enumerate(files):
        ctx.info(f"Processing {file}")
        await ctx.report_progress(i, len(files))
        data, mime_type = await ctx.read_resource(f"file://{file}")
    return "Processing complete"


# [Test] example usage
files_path="/home/ailab/files/llama_index/data/llama2_paper/source_files/source.txt"
long_task([files_path], Context)

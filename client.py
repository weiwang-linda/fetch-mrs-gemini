import asyncio
import logging
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from google import genai
from google.genai import types
from dotenv import load_dotenv, dotenv_values

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.info("Starting setup...")

# load environment variables from .env
load_dotenv()  
env_dict = dotenv_values("/<home-path>/.rh-gitlab-mcp.env")

class MCPClient:
    def __init__(self):
        # Initialize
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        self.genai = genai.Client()

    async def connect_to_server(self, server_script_path: str):
        """Connect to MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=env_dict
        )

        logger.info("Connecting to mcp server...")
        self.stdio, self.write = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        logger.info(f"\nConnected to server with tools: {[tool.name for tool in tools]}")

    async def process_query(self, query: str) -> str:
        """Process a query using Gemini and available tools"""
        logger.info("Query...")
        # Use automatic function calling with MCP session
        response = await self.genai.aio.models.generate_content(
            model="gemini-2.5-pro",
            contents=query,
            config=types.GenerateContentConfig(
                tools=[self.session],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False),
            ),
        )
        return response.text
    
    async def chat_loop(self):
        """Interactive chat loop"""
        logger.info("\nMCP Client Started!")
        logger.info("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break
                response = await self.process_query(query)
                logger.info("\n" + response)
            except Exception as e:
                logger.debug(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        logger.info("Closing...")
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        logger.info("Usage: python client.py <server_script>")
        sys.exit(1)
    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())

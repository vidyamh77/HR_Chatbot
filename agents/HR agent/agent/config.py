"""Configuration for the HR Agentic Solution."""
import os
import sys
import types
import typing

# --- Library Monkey-Patches for ADK compatibility with MCP SDK 2.x ---
try:
    # 1. Patch OpenTelemetry HTTPX instrumentation check to prevent crashing on httpx2 calls
    try:
        import opentelemetry.instrumentation.utils
        opentelemetry.instrumentation.utils.is_http_instrumentation_enabled = lambda: False
    except Exception:
        pass

    # 2. Patch anyio to handle datetime.timedelta and httpx.Timeout in fail_after/move_on_after
    import anyio
    _orig_fail_after = anyio.fail_after
    _orig_move_on_after = anyio.move_on_after

    def patched_fail_after(delay, shield=False):
        if delay is not None:
            if hasattr(delay, "total_seconds"):
                delay = delay.total_seconds()
            elif hasattr(delay, "connect") or hasattr(delay, "read"):
                read_val = getattr(delay, "read", None)
                delay = read_val if isinstance(read_val, (int, float)) else 30.0
            elif not isinstance(delay, (int, float)):
                try:
                    delay = float(delay)
                except Exception:
                    delay = 30.0
        return _orig_fail_after(delay, shield)

    def patched_move_on_after(delay, shield=False):
        if delay is not None:
            if hasattr(delay, "total_seconds"):
                delay = delay.total_seconds()
            elif hasattr(delay, "connect") or hasattr(delay, "read"):
                read_val = getattr(delay, "read", None)
                delay = read_val if isinstance(read_val, (int, float)) else 30.0
            elif not isinstance(delay, (int, float)):
                try:
                    delay = float(delay)
                except Exception:
                    delay = 30.0
        return _orig_move_on_after(delay, shield)

    anyio.fail_after = patched_fail_after
    anyio.move_on_after = patched_move_on_after

    # 1. Dynamically mock the deleted mcp.shared.session module in sys.modules
    mcp_shared_session = types.ModuleType("mcp.shared.session")
    sys.modules["mcp.shared.session"] = mcp_shared_session

    # Now import mcp and its client/shared packages
    import mcp
    import mcp.types
    import mcp.client.stdio
    import mcp.client.session
    import mcp.client.streamable_http
    import mcp.shared.exceptions

    # 2. Patch missing root attributes in mcp namespace
    mcp.SamplingCapability = mcp.types.SamplingCapability
    mcp.StdioServerParameters = mcp.client.stdio.StdioServerParameters

    # 3. Copy ProgressFnT from client.session to the mocked shared.session where google-adk expects it
    mcp_shared_session.ProgressFnT = mcp.client.session.ProgressFnT

    # 4. Patch missing McpHttpClientFactory on mcp.client.streamable_http module with a dummy Protocol
    class DummyFactory(typing.Protocol):
        pass
    mcp.client.streamable_http.McpHttpClientFactory = DummyFactory

    # 5. Patch capitalization mismatch: McpError -> MCPError in shared.exceptions
    mcp.shared.exceptions.McpError = mcp.shared.exceptions.MCPError

    # 6. Patch ClientSession stream properties redirection with closed status wrapper
    class StreamClosedWrapper:
        def __init__(self, dispatcher):
            self._dispatcher = dispatcher

        @property
        def _closed(self):
            return self._dispatcher._closed

    @property
    def read_stream_prop(self):
        return StreamClosedWrapper(self._dispatcher)

    @property
    def write_stream_prop(self):
        return StreamClosedWrapper(self._dispatcher)

    mcp.client.session.ClientSession._read_stream = read_stream_prop
    mcp.client.session.ClientSession._write_stream = write_stream_prop

    # 7. Patch Tool schema properties redirection to snake_case fields
    @property
    def input_schema_prop(self):
        return self.input_schema

    @property
    def output_schema_prop(self):
        return self.output_schema

    mcp.types.Tool.inputSchema = input_schema_prop
    mcp.types.Tool.outputSchema = output_schema_prop

except Exception as e:
    import logging
    logging.warning(f"Failed to apply MCP library monkey-patch: {e}")

from dotenv import load_dotenv

load_dotenv()

# --- Model Configuration ---
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# --- Retrieval Configuration ---
# 'okf' | 'rag' | 'mock'
RETRIEVAL_MODE = os.getenv("RETRIEVAL_MODE", "mock").lower()

# --- Paths ---
AGENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APP_NAME = "hr_agentic_solution"

# --- Live SaaS Integration Configuration ---
X_MCP_TOKEN = os.getenv("X_MCP_TOKEN", "mcp_U9oSNftO8cuJ3LUynzTTrioN_4RxXyqfrxQv5wIqO4Y")
WORKWEEK_MCP_URL = "https://mock-saas.aishprabhat.demo.altostrat.com/work-week/mcp/"
SERVICEIMMEDIATELY_MCP_URL = "https://mock-saas.aishprabhat.demo.altostrat.com/service-immediately/mcp/"


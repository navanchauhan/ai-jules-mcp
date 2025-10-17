from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path

import httpx
from fastmcp import FastMCP

SPEC_PATH = Path(__file__).with_name("openapi.json")

with SPEC_PATH.open(encoding="utf-8") as spec_file:
    JULES_OPENAPI_SPEC = json.load(spec_file)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Jules FastMCP server.")
    parser.add_argument(
        "--api-key",
        dest="api_key",
        default=os.getenv("JULES_API_KEY"),
        help="API key for the Jules API (or set JULES_API_KEY).",
    )
    args = parser.parse_args()
    if not args.api_key:
        parser.error("Provide --api-key or set the JULES_API_KEY environment variable.")
    return args


def build_mcp(api_key: str) -> tuple[FastMCP, httpx.AsyncClient]:
    client = httpx.AsyncClient(
        base_url="https://jules.googleapis.com",
        headers={"X-Goog-Api-Key": api_key},
    )
    mcp = FastMCP.from_openapi(
        openapi_spec=JULES_OPENAPI_SPEC,
        client=client,
        name="Jules MCP Server",
    )
    return mcp, client


def main() -> None:
    args = parse_args()
    mcp, client = build_mcp(args.api_key)
    try:
        mcp.run()
    finally:
        asyncio.run(client.aclose())


if __name__ == "__main__":
    main()

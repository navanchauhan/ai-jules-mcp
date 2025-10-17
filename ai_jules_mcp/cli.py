from __future__ import annotations

import argparse
import asyncio
import json
import os
from importlib import resources

import httpx
from fastmcp import FastMCP

_OPENAPI_SPEC: dict | None = None


def load_openapi_spec() -> dict:
    global _OPENAPI_SPEC
    if _OPENAPI_SPEC is None:
        with resources.files(__package__).joinpath("openapi.json").open("r", encoding="utf-8") as spec_file:
            _OPENAPI_SPEC = json.load(spec_file)
    return _OPENAPI_SPEC


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
        openapi_spec=load_openapi_spec(),
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

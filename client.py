#!/usr/bin/env python3
import asyncio
import argparse
import json
import os
import sys
from typing import Optional, List, Dict, Any, Union
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process Charles Proxy logs using MCP')
    parser.add_argument('file_path', help='Path to the Charles log file (.chlsj)')
    parser.add_argument('--format', choices=['summary', 'detailed', 'raw'], default='summary',
                        help='Output format (default: summary)')
    parser.add_argument('--save', action='store_true', help='Save parsed results to file')
    parser.add_argument('--output-dir', default='./output', help='Directory to save results (default: ./output)')
    parser.add_argument('--dashboard', action='store_true', help='Open a dashboard in browser to visualize the results')
    parser.add_argument('--host', help='Filter by hostname (e.g., "dashboard.paytm.com")')
    parser.add_argument('--match-type', choices=['exact', 'contains'], default='exact',
                        help='Type of matching to use (default: exact)')
    args = parser.parse_args()
    
    # If dashboard is requested, we need to save the results
    needs_save = args.save or args.dashboard

    # Connect to the MCP server
    async with AsyncExitStack() as exit_stack:
        # Configure server parameters
        server_params = StdioServerParameters(
            command="python",
            args=["server.py"],
            env=None
        )
        
        # Connect to the server
        stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        session = await exit_stack.enter_async_context(ClientSession(stdio, write))
        
        # Initialize the session
        await session.initialize()
        
        try:
            # If host is specified, use host-based filtering
            if args.host:
                # Get entries matching the host
                if needs_save:
                    result = await session.call_tool(
                        "parse_and_save_charles_log_by_host",
                        {
                            "file_path": args.file_path,
                            "host": args.host,
                            "output_dir": args.output_dir,
                            "format_type": args.format,
                            "match_type": args.match_type
                        }
                    )
                else:
                    result = await session.call_tool(
                        "parse_charles_log_by_host",
                        {
                            "file_path": args.file_path,
                            "host": args.host,
                            "format_type": args.format,
                            "match_type": args.match_type
                        }
                    )
                
                # Print the result for matching host
                if isinstance(result, dict):
                    print("\nEntries matching host:", args.host)
                    print(json.dumps(result, indent=2))
                else:
                    print("\nEntries matching host:", args.host)
                    print(result)
                
                # Get entries not matching the host
                if needs_save:
                    result_exclude = await session.call_tool(
                        "parse_and_save_charles_log_exclude_host",
                        {
                            "file_path": args.file_path,
                            "host": args.host,
                            "output_dir": args.output_dir,
                            "format_type": args.format,
                            "match_type": args.match_type
                        }
                    )
                else:
                    result_exclude = await session.call_tool(
                        "parse_charles_log_by_host",
                        {
                            "file_path": args.file_path,
                            "host": args.host,
                            "format_type": args.format,
                            "match_type": args.match_type
                        }
                    )
                
                # Print the result for non-matching host
                if isinstance(result_exclude, dict):
                    print("\nEntries not matching host:", args.host)
                    print(json.dumps(result_exclude, indent=2))
                else:
                    print("\nEntries not matching host:", args.host)
                    print(result_exclude)
                
                # Open dashboard if requested
                if args.dashboard:
                    if isinstance(result, dict) and "output_file" in result:
                        print("\nOpening dashboard for matching entries...")
                        dashboard_result = await session.call_tool(
                            "view_charles_log_dashboard",
                            {
                                "file_path": result["output_file"]
                            }
                        )
                        if isinstance(dashboard_result, dict):
                            print(json.dumps(dashboard_result, indent=2))
                        else:
                            print(dashboard_result)
                    
                    if isinstance(result_exclude, dict) and "output_file" in result_exclude:
                        print("\nOpening dashboard for non-matching entries...")
                        dashboard_result = await session.call_tool(
                            "view_charles_log_dashboard",
                            {
                                "file_path": result_exclude["output_file"]
                            }
                        )
                        if isinstance(dashboard_result, dict):
                            print(json.dumps(dashboard_result, indent=2))
                        else:
                            print(dashboard_result)
            
            # No filtering, process entire file
            else:
                if needs_save:
                    result = await session.call_tool(
                        "parse_and_save_charles_log",
                        {
                            "file_path": args.file_path,
                            "output_dir": args.output_dir,
                            "format_type": args.format
                        }
                    )
                else:
                    result = await session.call_tool(
                        "parse_charles_log",
                        {
                            "file_path": args.file_path,
                            "format_type": args.format
                        }
                    )
                
                # Print the result
                if isinstance(result, dict):
                    print(json.dumps(result, indent=2))
                else:
                    print(result)
                
                # Open dashboard if requested
                if args.dashboard and isinstance(result, dict) and "output_file" in result:
                    dashboard_result = await session.call_tool(
                        "view_charles_log_dashboard",
                        {
                            "file_path": result["output_file"]
                        }
                    )
                    if isinstance(dashboard_result, dict):
                        print(json.dumps(dashboard_result, indent=2))
                    else:
                        print(dashboard_result)
                
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 
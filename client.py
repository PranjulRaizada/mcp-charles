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
        
        # List available tools
        response = await session.list_tools()
        print(f"Available tools: {[tool.name for tool in response.tools]}")
        
        # Execute the tool to parse Charles logs
        if needs_save:
            result = await session.call_tool(
                "parse_and_save_charles_log",
                {
                    "file_path": args.file_path,
                    "format_type": args.format,
                    "output_dir": args.output_dir
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
        print("Results:")
        
        try:
            # The MCP tool results might be in various formats depending on the version
            # Try to extract the text content from the result
            result_text = None
            
            # Check if content is directly available
            if hasattr(result, 'content'):
                content = result.content
                # Handle TextContent objects which might be in a list
                if isinstance(content, list) and len(content) > 0:
                    if hasattr(content[0], 'text'):
                        result_text = content[0].text
                elif hasattr(content, 'text'):
                    result_text = content.text
                elif isinstance(content, (dict, str)):
                    result_text = content
            # Try alternative property names
            elif hasattr(result, 'text'):
                result_text = result.text
                
            # If we couldn't extract text, use the raw result
            if result_text is None:
                result_text = str(result)
                
            # Handle the text content
            if isinstance(result_text, dict):
                data = result_text
            else:
                # Try to parse as JSON
                data = json.loads(result_text)
            
            if "error" in data:
                print(f"Error: {data['error']}")
            elif needs_save and "status" in data and data["status"] == "success":
                print(f"Success: {data['message']}")
                print(f"Output file: {data['output_file']}")
                
                # If user wants to view the dashboard, call the dashboard tool
                if args.dashboard and data['output_file'] and os.path.exists(data['output_file']):
                    await view_dashboard(session, data['output_file'])
            else:
                if args.format == "summary":
                    print(f"Total entries: {data.get('total_entries', 0)}")
                    print(f"Request methods: {data.get('request_methods', {})}")
                    print(f"Status codes: {data.get('status_codes', {})}")
                    print(f"Top hosts: {dict(list(data.get('hosts', {}).items())[:5])}")
                    timing = data.get('timing', {})
                    print(f"Timing (ms): min={timing.get('min', 0):.2f}, " +
                          f"max={timing.get('max', 0):.2f}, " +
                          f"avg={timing.get('avg', 0):.2f}")
                else:
                    entry_count = len(data.get('entries', []))
                    print(f"Processed {entry_count} entries")
                    # Print the first entry as a sample
                    if entry_count > 0:
                        print("\nSample entry:")
                        sample = data['entries'][0]
                        print(f"URL: {sample.get('url', '')}")
                        print(f"Method: {sample.get('method', '')}")
                        print(f"Status: {sample.get('status', '')}")
                        print(f"Duration: {sample.get('duration', 0)} ms")
        except json.JSONDecodeError:
            print(f"Raw response (not JSON): {result}")
        except Exception as e:
            print(f"Error processing result: {str(e)}")
            print(f"Raw result: {result}")

async def view_dashboard(session, file_path):
    """Open a dashboard in the browser for the given JSON file"""
    try:
        dashboard_response = await session.call_tool(
            "view_charles_log_dashboard",
            {
                "file_path": file_path
            }
        )
        
        if hasattr(dashboard_response, 'error') and dashboard_response.error:
            print(f"Error opening dashboard: {dashboard_response.error}")
        else:
            print("Dashboard opened in browser")
    except Exception as e:
        print(f"Error opening dashboard: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 
#!/usr/bin/env python3
import asyncio
import argparse
import json
from typing import Dict, List, Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def process_large_file(session, file_path: str, output_path: Optional[str] = None):
    """Process a large Charles log file in chunks"""
    print(f"Processing large file: {file_path}")
    
    # Initialize variables
    offset = 0
    has_more = True
    total_entries = 0
    chunks_processed = 0
    
    # Statistics
    methods = {}
    status_codes = {}
    hosts = {}
    
    # Process in chunks
    while has_more:
        # Call MCP tool to read chunk
        result = await session.call_tool(
            "read_large_file_part",
            {
                "file_path": file_path,
                "start_offset": offset,
                "length": 2000000  # 2MB chunks
            }
        )
        
        # Extract data from CallToolResult
        result_data = None
        if hasattr(result, 'content'):
            content = result.content
            # Handle TextContent objects which might be in a list
            if isinstance(content, list) and len(content) > 0:
                if hasattr(content[0], 'text'):
                    result_data = json.loads(content[0].text)
            elif hasattr(content, 'text'):
                result_data = json.loads(content.text)
            elif isinstance(content, (dict, str)):
                result_data = content if isinstance(content, dict) else json.loads(content)
        elif hasattr(result, 'text'):
            result_data = json.loads(result.text)
        
        # If we couldn't parse the result, skip this chunk
        if result_data is None:
            print(f"Error: Could not parse result: {result}")
            return
        
        # Check for errors
        if "error" in result_data:
            print(f"Error: {result_data['error']}")
            return
        
        # Process entries
        entries = result_data.get("entries", [])
        entry_count = len(entries)
        total_entries += entry_count
        chunks_processed += 1
        
        # Update statistics
        for entry in entries:
            # Count methods
            method = None
            if "request" in entry and isinstance(entry["request"], dict):
                method = entry["request"].get("method")
            if not method:
                method = "UNKNOWN"
            methods[method] = methods.get(method, 0) + 1
            
            # Count status codes
            status = None
            if "status" in entry:
                status = entry["status"]
            elif "response" in entry and isinstance(entry["response"], dict):
                status = entry["response"].get("status")
            
            status_str = str(status) if status is not None else "UNKNOWN"
            status_codes[status_str] = status_codes.get(status_str, 0) + 1
            
            # Count hosts
            host = entry.get("host")
            if not host:
                host = "UNKNOWN"
            hosts[host] = hosts.get(host, 0) + 1
        
        # Get metadata
        metadata = result_data.get("metadata", {})
        file_size = metadata.get("file_size", 0)
        read_bytes = metadata.get("read_bytes", 0)
        has_more = metadata.get("has_more", False)
        file_format = metadata.get("format", "unknown")
        
        # Update offset for next chunk (use a default value if None)
        next_offset = metadata.get("next_offset")
        if next_offset is not None:
            offset = next_offset
        else:
            # If next_offset is None, calculate based on read_bytes (which defaults to 0 if None)
            offset = offset + (read_bytes or 0)
            
            # If we couldn't determine the next offset, break to avoid infinite loops
            if read_bytes == 0 or read_bytes is None:
                print("Warning: Could not determine next read position, stopping.")
                has_more = False
        
        # Print progress (handle None values)
        if file_size and file_size > 0:
            progress = (offset / file_size) * 100
        else:
            progress = 0
        print(f"Chunk {chunks_processed}: {entry_count} entries, format: {file_format}, {progress:.2f}% complete")
    
    # Print final statistics
    print("\nProcessing complete!")
    print(f"Total entries processed: {total_entries}")
    print(f"Total chunks processed: {chunks_processed}")
    
    if methods:
        print("\nTop request methods:")
        for method, count in sorted(methods.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {method}: {count}")
    
    if status_codes:
        print("\nTop status codes:")
        for code, count in sorted(status_codes.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {code}: {count}")
    
    if hosts:
        print("\nTop hosts:")
        for host, count in sorted(hosts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {host}: {count}")
    
    # Save results if output path provided
    if output_path:
        stats = {
            "total_entries": total_entries,
            "chunks_processed": chunks_processed,
            "request_methods": methods,
            "status_codes": status_codes,
            "hosts": hosts
        }
        
        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"\nStatistics saved to: {output_path}")

async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process large Charles log files in chunks')
    parser.add_argument('file_path', help='Path to the Charles log file (.chlsj)')
    parser.add_argument('--output', help='Path to save summary statistics')
    args = parser.parse_args()

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
        
        # Process the large file
        await process_large_file(session, args.file_path, args.output)

if __name__ == "__main__":
    asyncio.run(main()) 
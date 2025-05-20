#!/usr/bin/env python3
import json
import os
from typing import Dict, List, Optional, Union, Literal
from collections import Counter
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Charles-Proxy-Log-Parser")

@mcp.tool()
def parse_charles_log(file_path: str, format_type: str = "summary") -> Dict:
    """
    Parse a Charles log file (.chls or .chlsj) and convert it to a meaningful format.
    
    Args:
        file_path: Path to the Charles log file
        format_type: Type of output format (summary, detailed, or raw)
        
    Returns:
        A dictionary containing the parsed log data
    """
    # Validate file path
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    if not file_path.endswith(('.chls', '.chlsj')):
        return {"error": "File must be a Charles log file (.chls or .chlsj)"}
    
    # For .chlsj files (JSON format)
    if file_path.endswith('.chlsj'):
        try:
            return _parse_chlsj_file(file_path, format_type)
        except Exception as e:
            return {"error": f"Error parsing .chlsj file: {str(e)}"}
    
    # For .chls files (binary format)
    return {"error": "Binary .chls files are not supported yet, please export as .chlsj from Charles"}

@mcp.tool()
def parse_and_save_charles_log(file_path: str, output_dir: str = "./output", format_type: str = "detailed") -> Dict:
    """
    Parse a Charles log file (.chls or .chlsj) and save the result to the specified directory.
    
    Args:
        file_path: Path to the Charles log file
        output_dir: Directory to save the converted JSON file
        format_type: Type of output format (summary, detailed, or raw)
        
    Returns:
        A dictionary containing the result of the operation
    """
    # Validate file path
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    if not file_path.endswith(('.chls', '.chlsj')):
        return {"error": "File must be a Charles log file (.chls or .chlsj)"}
    
    # Validate output directory
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            return {"error": f"Error creating output directory: {str(e)}"}
    
    # For .chlsj files (JSON format)
    if file_path.endswith('.chlsj'):
        try:
            result = _parse_chlsj_file(file_path, format_type)
            
            # Generate output filename
            base_name = os.path.basename(file_path)
            name_without_ext = os.path.splitext(base_name)[0]
            output_file = os.path.join(output_dir, f"{name_without_ext}_parsed.json")
            
            # Write to file
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            return {
                "status": "success",
                "message": f"Successfully parsed and saved to {output_file}",
                "output_file": output_file
            }
        except Exception as e:
            return {"error": f"Error parsing or saving .chlsj file: {str(e)}"}
    
    # For .chls files (binary format)
    return {"error": "Binary .chls files are not supported yet, please export as .chlsj from Charles"}

@mcp.tool()
def read_large_file_part(file_path: str, start_offset: int = 0, length: int = 1000000) -> Dict:
    """
    Read part of a large Charles log file for incremental processing.
    
    Args:
        file_path: Path to the Charles log file
        start_offset: Starting byte offset in the file
        length: Maximum number of bytes to read
        
    Returns:
        A dictionary containing the file part data and metadata
    """
    # Validate file path
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    if not file_path.endswith(('.chls', '.chlsj')):
        return {"error": "File must be a Charles log file (.chls or .chlsj)"}
    
    try:
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Validate offset
        if start_offset < 0 or start_offset >= file_size:
            return {"error": f"Invalid offset: {start_offset}. File size is {file_size} bytes."}
        
        # Adjust length if it goes beyond the end of file
        if start_offset + length > file_size:
            length = file_size - start_offset
        
        # If this is the first read (offset=0), check if the file is a JSON array or line-by-line
        is_json_array = False
        if start_offset == 0:
            # Read a small portion to detect format
            with open(file_path, 'r') as f:
                sample = f.read(min(1000, file_size))
                sample = sample.strip()
                # Check if it starts with '[' which indicates a JSON array
                if sample.startswith('['):
                    is_json_array = True
        
        # Process content for .chlsj files
        if file_path.endswith('.chlsj'):
            entries = []
            
            if is_json_array:
                # For JSON array format
                if start_offset == 0:
                    # Read the entire file if it's a JSON array and this is the first chunk
                    with open(file_path, 'r') as f:
                        try:
                            content = f.read()
                            entries = json.loads(content)
                            # Set flag to indicate we've read everything
                            next_offset = file_size
                        except json.JSONDecodeError as e:
                            return {"error": f"Error parsing JSON array: {str(e)}"}
                else:
                    # For subsequent chunks, we don't re-read the array since we got it all on first pass
                    entries = []
                    next_offset = file_size
            else:
                # For line-by-line format
                with open(file_path, 'r') as f:
                    f.seek(start_offset)
                    content = f.read(length)
                
                lines = content.splitlines()
                
                for line in lines:
                    try:
                        if line.strip():  # Skip empty lines
                            entry = json.loads(line.strip())
                            entries.append(entry)
                    except json.JSONDecodeError:
                        continue  # Skip invalid lines
                
                # Calculate next offset
                next_offset = start_offset + length
            
            return {
                "entries": entries,
                "metadata": {
                    "file_size": file_size,
                    "current_offset": start_offset,
                    "read_bytes": length,
                    "entry_count": len(entries),
                    "has_more": next_offset < file_size,
                    "next_offset": next_offset if next_offset < file_size else None,
                    "format": "json_array" if is_json_array else "line_by_line"
                }
            }
        
        # For .chls files (binary format)
        return {"error": "Binary .chls files are not supported yet, please export as .chlsj from Charles"}
        
    except Exception as e:
        return {"error": f"Error reading file: {str(e)}"}

def _parse_chlsj_file(file_path: str, format_type: str) -> Dict:
    """
    Parse a .chlsj file (Charles log in JSON format)
    
    Args:
        file_path: Path to the .chlsj file
        format_type: Type of output format (summary, detailed, or raw)
        
    Returns:
        Dictionary with parsed data
    """
    # First try to parse the file as a whole JSON array
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            # Try to parse the file as a JSON array
            entries = json.loads(content)
            # If entries is not a list, wrap it in one
            if not isinstance(entries, list):
                entries = [entries]
    except json.JSONDecodeError:
        # If it fails, fall back to line-by-line parsing
        entries = []
        with open(file_path, 'r') as f:
            # .chlsj files may contain one JSON object per line
            for line in f:
                try:
                    if line.strip():  # Skip empty lines
                        entry = json.loads(line.strip())
                        entries.append(entry)
                except json.JSONDecodeError:
                    continue  # Skip invalid lines
    
    # Process based on format type
    if format_type == "raw":
        return {"entries": entries}
    
    elif format_type == "summary":
        summary = {
            "total_entries": len(entries),
            "request_methods": {},
            "status_codes": {},
            "hosts": {},
            "content_types": {},
            "timing": {
                "min": float('inf'),
                "max": 0,
                "avg": 0,
                "total": 0
            }
        }
        
        for entry in entries:
            # Count request methods
            method = entry.get("request", {}).get("method", "UNKNOWN")
            summary["request_methods"][method] = summary["request_methods"].get(method, 0) + 1
            
            # Count status codes
            status = entry.get("response", {}).get("status", 0)
            status_str = str(status)
            summary["status_codes"][status_str] = summary["status_codes"].get(status_str, 0) + 1
            
            # Count hosts
            host = entry.get("host", "UNKNOWN")
            summary["hosts"][host] = summary["hosts"].get(host, 0) + 1
            
            # Count content types
            content_type = None
            response_headers = entry.get("response", {}).get("headers", {})
            if isinstance(response_headers, dict):
                content_type_values = response_headers.get("Content-Type", ["UNKNOWN"])
                if isinstance(content_type_values, list) and len(content_type_values) > 0:
                    content_type = content_type_values[0]
            elif isinstance(response_headers, list):
                # Some Charles formats store headers as a list of objects with name/value
                for header in response_headers:
                    if isinstance(header, dict) and header.get("name") == "Content-Type":
                        content_type = header.get("value")
                        break
            
            if content_type is None:
                content_type = "UNKNOWN"
                
            summary["content_types"][content_type] = summary["content_types"].get(content_type, 0) + 1
            
            # Calculate timing stats
            if "duration" in entry:
                duration = entry["duration"]
                summary["timing"]["min"] = min(summary["timing"]["min"], duration)
                summary["timing"]["max"] = max(summary["timing"]["max"], duration)
                summary["timing"]["total"] += duration
            elif "durations" in entry and isinstance(entry["durations"], dict):
                # Some Charles formats store duration in "durations.total"
                duration = entry["durations"].get("total")
                if duration is not None:
                    summary["timing"]["min"] = min(summary["timing"]["min"], duration)
                    summary["timing"]["max"] = max(summary["timing"]["max"], duration)
                    summary["timing"]["total"] += duration
        
        # Calculate average
        if len(entries) > 0:
            summary["timing"]["avg"] = summary["timing"]["total"] / len(entries)
        
        # If no entries, reset min to 0
        if summary["timing"]["min"] == float('inf'):
            summary["timing"]["min"] = 0
            
        return summary
    
    # Detailed format (default)
    else:
        processed_entries = []
        
        for entry in entries:
            # Extract basic fields
            processed_entry = {
                "url": entry.get("url", ""),
                "host": entry.get("host", ""),
                "path": entry.get("path", ""),
                "status": entry.get("status", ""),  # Some Charles formats use top-level status
                "duration": 0,
            }
            
            # Process request fields
            if "request" in entry:
                request = entry["request"]
                processed_entry["method"] = request.get("method", "")
                processed_entry["request_size"] = request.get("size", 0)
                
                # Process request headers
                if "header" in request and "headers" in request["header"]:
                    # Some Charles formats nest headers under header.headers
                    processed_entry["request_headers"] = {}
                    for header in request["header"]["headers"]:
                        if isinstance(header, dict) and "name" in header and "value" in header:
                            processed_entry["request_headers"][header["name"]] = header["value"]
                elif "headers" in request:
                    # Standard format
                    processed_entry["request_headers"] = request["headers"]
                
                # Add request body if available
                if "body" in request:
                    processed_entry["request_body"] = request["body"]
            
            # Process response fields
            if "response" in entry:
                response = entry["response"]
                if "status" in response:
                    processed_entry["status"] = response["status"]
                processed_entry["response_size"] = response.get("size", 0)
                
                # Process response headers
                if "header" in response and "headers" in response["header"]:
                    # Some Charles formats nest headers under header.headers
                    processed_entry["response_headers"] = {}
                    for header in response["header"]["headers"]:
                        if isinstance(header, dict) and "name" in header and "value" in header:
                            processed_entry["response_headers"][header["name"]] = header["value"]
                elif "headers" in response:
                    # Standard format
                    processed_entry["response_headers"] = response["headers"]
                
                # Add response body if available
                if "body" in response:
                    processed_entry["response_body"] = response["body"]
            
            # Handle different duration fields
            if "duration" in entry:
                processed_entry["duration"] = entry["duration"]
            elif "durations" in entry and isinstance(entry["durations"], dict):
                # Some Charles formats store duration in "durations.total"
                total_duration = entry["durations"].get("total")
                if total_duration is not None:
                    processed_entry["duration"] = total_duration
            
            processed_entries.append(processed_entry)
        
        return {"entries": processed_entries}

@mcp.tool()
def view_charles_log_dashboard(file_path: str) -> Dict:
    """
    Opens a dashboard in the browser to visualize a parsed Charles log file.
    
    Args:
        file_path: Path to the parsed JSON file
        
    Returns:
        A dictionary containing the result of the operation
    """
    # Validate file path
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    if not file_path.endswith('.json'):
        return {"error": "File must be a JSON file"}
    
    try:
        # Import the dashboard module
        import sys
        import tempfile
        import webbrowser
        from collections import Counter
        
        # Load the parsed data
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Create output HTML file
        output_file = os.path.join(tempfile.gettempdir(), "charles_log_dashboard.html")
        
        # Generate HTML report
        html = generate_html_report(data, file_path)
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write(html)
        
        # Open in browser
        webbrowser.open('file://' + os.path.abspath(output_file))
        
        return {
            "status": "success",
            "message": f"Dashboard opened in browser",
            "dashboard_file": output_file
        }
    except Exception as e:
        return {"error": f"Error creating dashboard: {str(e)}"}

def generate_html_report(data, input_file):
    """Generate a HTML report from the parsed data"""
    
    # Start with HTML header
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Charles Log Analysis</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1, h2, h3 { color: #333; }
        .container { display: flex; flex-wrap: wrap; }
        .chart { margin: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) { background-color: #f9f9f9; }
    </style>
</head>
<body>
    <h1>Charles Proxy Log Analysis</h1>
"""
    
    # Add timestamp and filename
    html += f"<p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>\n"
    html += f"<p>File: {os.path.basename(input_file)}</p>\n"
    
    # Handle summary format
    if isinstance(data, dict) and "total_entries" in data:
        html += "<h2>Summary</h2>\n"
        html += f"<p>Total Entries: {data.get('total_entries', 0)}</p>\n"
        
        # Request Methods
        if "request_methods" in data:
            html += "<h3>Request Methods</h3>\n"
            html += "<table>\n"
            html += "<tr><th>Method</th><th>Count</th></tr>\n"
            
            for method, count in sorted(data["request_methods"].items(), key=lambda x: x[1], reverse=True):
                html += f"<tr><td>{method}</td><td>{count}</td></tr>\n"
            
            html += "</table>\n"
        
        # Status Codes
        if "status_codes" in data:
            html += "<h3>Status Codes</h3>\n"
            html += "<table>\n"
            html += "<tr><th>Status</th><th>Count</th></tr>\n"
            
            for status, count in sorted(data["status_codes"].items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
                html += f"<tr><td>{status}</td><td>{count}</td></tr>\n"
            
            html += "</table>\n"
        
        # Hosts
        if "hosts" in data:
            html += "<h3>Top Hosts</h3>\n"
            html += "<table>\n"
            html += "<tr><th>Host</th><th>Count</th></tr>\n"
            
            for host, count in sorted(data["hosts"].items(), key=lambda x: x[1], reverse=True)[:20]:
                html += f"<tr><td>{host}</td><td>{count}</td></tr>\n"
            
            html += "</table>\n"
        
        # Timing
        if "timing" in data:
            html += "<h3>Timing (ms)</h3>\n"
            html += "<table>\n"
            html += "<tr><th>Metric</th><th>Value</th></tr>\n"
            html += f"<tr><td>Minimum</td><td>{data['timing'].get('min', 0)}</td></tr>\n"
            html += f"<tr><td>Maximum</td><td>{data['timing'].get('max', 0)}</td></tr>\n"
            html += f"<tr><td>Average</td><td>{data['timing'].get('avg', 0)}</td></tr>\n"
            html += f"<tr><td>Total</td><td>{data['timing'].get('total', 0)}</td></tr>\n"
            html += "</table>\n"
    
    # Handle detailed format
    elif "entries" in data:
        entries = data["entries"]
        html += "<h2>Detailed Report</h2>\n"
        html += f"<p>Total Entries: {len(entries)}</p>\n"
        
        # Count status codes
        status_counts = Counter()
        host_counts = Counter()
        methods = Counter()
        durations = []
        
        for entry in entries:
            # Status codes
            status = str(entry.get("status", "Unknown"))
            status_counts[status] += 1
            
            # Hosts
            host = entry.get("host", "Unknown")
            host_counts[host] += 1
            
            # Methods
            method = entry.get("method", "Unknown")
            methods[method] += 1
            
            # Durations
            if "duration" in entry:
                try:
                    duration = float(entry["duration"])
                    durations.append(duration)
                except (ValueError, TypeError):
                    pass
        
        # Status Codes
        html += "<h3>Status Codes</h3>\n"
        html += "<table>\n"
        html += "<tr><th>Status</th><th>Count</th></tr>\n"
        
        for status, count in sorted(status_counts.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
            html += f"<tr><td>{status}</td><td>{count}</td></tr>\n"
        
        html += "</table>\n"
        
        # Top Hosts
        html += "<h3>Top Hosts</h3>\n"
        html += "<table>\n"
        html += "<tr><th>Host</th><th>Count</th></tr>\n"
        
        for host, count in host_counts.most_common(20):
            html += f"<tr><td>{host}</td><td>{count}</td></tr>\n"
        
        html += "</table>\n"
        
        # Request Methods
        html += "<h3>Request Methods</h3>\n"
        html += "<table>\n"
        html += "<tr><th>Method</th><th>Count</th></tr>\n"
        
        for method, count in methods.most_common():
            html += f"<tr><td>{method}</td><td>{count}</td></tr>\n"
        
        html += "</table>\n"
        
        # Timing
        if durations:
            html += "<h3>Timing (ms)</h3>\n"
            html += "<table>\n"
            html += "<tr><th>Metric</th><th>Value</th></tr>\n"
            html += f"<tr><td>Minimum</td><td>{min(durations)}</td></tr>\n"
            html += f"<tr><td>Maximum</td><td>{max(durations)}</td></tr>\n"
            html += f"<tr><td>Average</td><td>{sum(durations) / len(durations):.2f}</td></tr>\n"
            html += f"<tr><td>Total</td><td>{sum(durations)}</td></tr>\n"
            html += "</table>\n"
    
    # Close HTML
    html += """</body>
</html>
"""
    
    return html

# Run the server if executed directly
if __name__ == "__main__":
    import sys
    mcp.run(transport='stdio') 
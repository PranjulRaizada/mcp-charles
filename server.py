#!/usr/bin/env python3
import json
import os
import sys
import tempfile
import webbrowser
import shutil
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
def parse_charles_log_by_host(file_path: str, host: str, format_type: str = "detailed", match_type: str = "exact") -> Dict:
    """
    Parse a Charles log file (.chls or .chlsj) and extract only entries for a specific host.
    
    Args:
        file_path: Path to the Charles log file
        host: The hostname to filter by (e.g., "dashboard.paytm.com")
        format_type: Type of output format (summary, detailed, or raw)
        match_type: Type of hostname matching to use ("exact" or "contains")
        
    Returns:
        A dictionary containing the parsed log data for the specified host
    """
    # Validate file path
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    if not file_path.endswith(('.chls', '.chlsj')):
        return {"error": "File must be a Charles log file (.chls or .chlsj)"}
    
    # Validate match_type
    if match_type not in ["exact", "contains"]:
        return {"error": f"Invalid match_type: {match_type}. Must be 'exact' or 'contains'"}
    
    # For .chlsj files (JSON format)
    if file_path.endswith('.chlsj'):
        try:
            return _parse_chlsj_file_by_host(file_path, host, format_type, match_type)
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
def parse_and_save_charles_log_by_host(file_path: str, host: str, output_dir: str = "./output", format_type: str = "detailed", match_type: str = "exact") -> Dict:
    """
    Parse a Charles log file (.chls or .chlsj) for a specific host and save the result to the specified directory.
    
    Args:
        file_path: Path to the Charles log file
        host: The hostname to filter by (e.g., "dashboard.paytm.com")
        output_dir: Directory to save the converted JSON file
        format_type: Type of output format (summary, detailed, or raw)
        match_type: Type of hostname matching to use ("exact" or "contains")
        
    Returns:
        A dictionary containing the result of the operation
    """
    # Validate file path
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    if not file_path.endswith(('.chls', '.chlsj')):
        return {"error": "File must be a Charles log file (.chls or .chlsj)"}
    
    # Validate match_type
    if match_type not in ["exact", "contains"]:
        return {"error": f"Invalid match_type: {match_type}. Must be 'exact' or 'contains'"}
    
    # Validate output directory
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            return {"error": f"Error creating output directory: {str(e)}"}
    
    # For .chlsj files (JSON format)
    if file_path.endswith('.chlsj'):
        try:
            result = _parse_chlsj_file_by_host(file_path, host, format_type, match_type)
            
            # Generate output filename
            base_name = os.path.basename(file_path)
            name_without_ext = os.path.splitext(base_name)[0]
            safe_host = host.replace(".", "_").replace("/", "_").replace(":", "_")
            match_str = "exact" if match_type == "exact" else "contains"
            output_file = os.path.join(output_dir, f"{name_without_ext}_{safe_host}_{match_str}_parsed.json")
            
            # Write to file
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            return {
                "status": "success",
                "message": f"Successfully parsed and saved to {output_file}",
                "output_file": output_file,
                "filtered_by_host": host,
                "match_type": match_type,
                "entry_count": len(result.get("entries", [])) if "entries" in result else 0
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

def _parse_chlsj_file_by_host(file_path: str, host: str, format_type: str, match_type: str = "exact") -> Dict:
    """
    Parse a .chlsj file (Charles log in JSON format) and filter by host
    
    Args:
        file_path: Path to the .chlsj file
        host: Hostname to filter by
        format_type: Type of output format (summary, detailed, or raw)
        match_type: Type of hostname matching to use ("exact" or "contains")
        
    Returns:
        Dictionary with parsed data for the specified host
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
    
    # Filter entries by host based on match_type
    filtered_entries = []
    for entry in entries:
        entry_host = entry.get("host", "")
        
        # Apply filtering based on match type
        if match_type == "exact":
            # Exact match (case-insensitive)
            if entry_host.lower() == host.lower():
                filtered_entries.append(entry)
        else:  # "contains"
            # Substring match (case-insensitive)
            if host.lower() in entry_host.lower():
                filtered_entries.append(entry)
    
    # Process based on format type
    if format_type == "raw":
        return {"entries": filtered_entries, "filtered_by_host": host, "match_type": match_type}
    
    elif format_type == "summary":
        summary = {
            "total_entries": len(filtered_entries),
            "host": host,
            "request_methods": {},
            "status_codes": {},
            "content_types": {},
            "timing": {
                "min": float('inf'),
                "max": 0,
                "avg": 0,
                "total": 0
            }
        }
        
        for entry in filtered_entries:
            # Count request methods
            method = entry.get("request", {}).get("method", "UNKNOWN")
            summary["request_methods"][method] = summary["request_methods"].get(method, 0) + 1
            
            # Count status codes
            status = entry.get("response", {}).get("status", 0)
            status_str = str(status)
            summary["status_codes"][status_str] = summary["status_codes"].get(status_str, 0) + 1
            
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
        if len(filtered_entries) > 0:
            summary["timing"]["avg"] = summary["timing"]["total"] / len(filtered_entries)
        
        # If no entries, reset min to 0
        if summary["timing"]["min"] == float('inf'):
            summary["timing"]["min"] = 0
            
        return summary
    
    # Detailed format (default)
    else:
        processed_entries = []
        
        for entry in filtered_entries:
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
        
        return {"entries": processed_entries, "filtered_by_host": host, "match_type": match_type}

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
        # Import necessary modules
        import sys
        import tempfile
        import webbrowser
        import shutil
        from collections import Counter
        from datetime import datetime
        
        # Load the parsed data
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Create temp directory for dashboard files
        temp_dir = os.path.join(tempfile.gettempdir(), "charles_dashboard")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # Create static directories in temp location
        static_dir = os.path.join(temp_dir, "static")
        css_dir = os.path.join(static_dir, "css")
        js_dir = os.path.join(static_dir, "js")
        
        # Make sure directories exist
        for directory in [static_dir, css_dir, js_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        # Copy static files to temp location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        shutil.copyfile(
            os.path.join(script_dir, "dashboard", "static", "css", "dashboard.css"),
            os.path.join(css_dir, "dashboard.css")
        )
        shutil.copyfile(
            os.path.join(script_dir, "dashboard", "static", "js", "dashboard.js"),
            os.path.join(js_dir, "dashboard.js")
        )
        
        # Create dashboard output file
        output_file = os.path.join(temp_dir, "index.html")
        
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
    
    # Read template file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_dir, "dashboard", "templates", "dashboard.html"), 'r') as f:
        template = f.read()
    
    # Prepare template variables
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    filename = os.path.basename(input_file)
    
    # Initialize variables
    total_entries = 0
    status_code_rows = ""
    request_method_rows = ""
    top_host_rows = ""
    timing_min = 0
    timing_max = 0
    timing_avg = 0
    timing_total = 0
    
    # Data for JavaScript charts
    dashboard_data = {
        "statusCodes": {},
        "requestMethods": {},
        "topHosts": {},
        "timing": {
            "min": 0,
            "max": 0,
            "avg": 0
        }
    }
    
    # Handle summary format (from summary tool)
    if isinstance(data, dict) and "total_entries" in data:
        total_entries = data.get('total_entries', 0)
        
        # Process status codes
        if "status_codes" in data:
            status_codes = data["status_codes"]
            dashboard_data["statusCodes"] = status_codes
            
            total_status = sum(status_codes.values())
            for status, count in sorted(status_codes.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
                percentage = (count / total_status) * 100 if total_status > 0 else 0
                status_code_rows += f"<tr><td>{status}</td><td>{count}</td><td>{percentage:.1f}%</td></tr>\n"
        
        # Process request methods
        if "request_methods" in data:
            request_methods = data["request_methods"]
            dashboard_data["requestMethods"] = request_methods
            
            total_methods = sum(request_methods.values())
            for method, count in sorted(request_methods.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_methods) * 100 if total_methods > 0 else 0
                request_method_rows += f"<tr><td>{method}</td><td>{count}</td><td>{percentage:.1f}%</td></tr>\n"
        
        # Process hosts
        if "hosts" in data:
            hosts = data["hosts"]
            dashboard_data["topHosts"] = hosts
            
            total_hosts = sum(hosts.values())
            for host, count in sorted(hosts.items(), key=lambda x: x[1], reverse=True)[:20]:
                percentage = (count / total_hosts) * 100 if total_hosts > 0 else 0
                top_host_rows += f"<tr><td>{host}</td><td>{count}</td><td>{percentage:.1f}%</td></tr>\n"
        
        # Process timing
        if "timing" in data:
            timing = data["timing"]
            dashboard_data["timing"] = timing
            
            timing_min = timing.get('min', 0)
            timing_max = timing.get('max', 0)
            timing_avg = timing.get('avg', 0)
            timing_total = timing.get('total', 0)
    
    # Handle detailed format (from entries)
    elif "entries" in data:
        entries = data["entries"]
        total_entries = len(entries)
        
        # Count status codes, hosts, methods, durations
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
        
        # Prepare status code rows
        dashboard_data["statusCodes"] = dict(status_counts)
        total_status = sum(status_counts.values())
        for status, count in sorted(status_counts.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
            percentage = (count / total_status) * 100 if total_status > 0 else 0
            status_code_rows += f"<tr><td>{status}</td><td>{count}</td><td>{percentage:.1f}%</td></tr>\n"
        
        # Prepare request method rows
        dashboard_data["requestMethods"] = dict(methods)
        total_methods = sum(methods.values())
        for method, count in methods.most_common():
            percentage = (count / total_methods) * 100 if total_methods > 0 else 0
            request_method_rows += f"<tr><td>{method}</td><td>{count}</td><td>{percentage:.1f}%</td></tr>\n"
        
        # Prepare host rows
        dashboard_data["topHosts"] = dict(host_counts)
        total_hosts = sum(host_counts.values())
        for host, count in host_counts.most_common(20):
            percentage = (count / total_hosts) * 100 if total_hosts > 0 else 0
            top_host_rows += f"<tr><td>{host}</td><td>{count}</td><td>{percentage:.1f}%</td></tr>\n"
        
        # Process timing
        if durations:
            timing_min = min(durations)
            timing_max = max(durations)
            timing_avg = sum(durations) / len(durations)
            timing_total = sum(durations)
            
            dashboard_data["timing"] = {
                "min": timing_min,
                "max": timing_max,
                "avg": timing_avg
            }
            
            # Add duration distribution for the histogram
            dashboard_data["durationDistribution"] = durations
    
    # Determine if we should show the duration distribution chart
    display_duration_distribution = "block" if "durationDistribution" in dashboard_data else "none"
    
    # Replace template variables
    html = template.replace("{{timestamp}}", timestamp)
    html = html.replace("{{filename}}", filename)
    html = html.replace("{{total_entries}}", str(total_entries))
    html = html.replace("{{status_code_rows}}", status_code_rows)
    html = html.replace("{{request_method_rows}}", request_method_rows)
    html = html.replace("{{top_host_rows}}", top_host_rows)
    html = html.replace("{{timing_min}}", str(timing_min))
    html = html.replace("{{timing_max}}", str(timing_max))
    html = html.replace("{{timing_avg}}", f"{timing_avg:.2f}")
    html = html.replace("{{timing_total}}", str(timing_total))
    html = html.replace("{{display_duration_distribution}}", display_duration_distribution)
    
    # JSON encode the data for JavaScript
    dashboard_data_json = json.dumps(dashboard_data)
    html = html.replace("{{dashboard_data_json}}", dashboard_data_json)
    
    return html

# Run the server if executed directly
if __name__ == "__main__":
    import sys
    mcp.run(transport='stdio') 
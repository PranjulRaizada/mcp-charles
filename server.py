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
def parse_charles_log_by_path(file_path: str, path: str, format_type: str = "detailed", match_type: str = "exact") -> Dict:
    """
    Parse a Charles log file (.chls or .chlsj) and extract only entries for a specific :path.
    
    Args:
        file_path: Path to the Charles log file
        path: The :path to filter by (e.g., "/api/v2/fetch?param=value")
        format_type: Type of output format (summary, detailed, or raw)
        match_type: Type of path matching to use ("exact" or "contains")
        
    Returns:
        A dictionary containing the parsed log data for the specified path
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
            return _parse_chlsj_file_by_path(file_path, path, format_type, match_type)
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
        host: The host to filter by (e.g., "paytm.com")
        format_type: Type of output format (summary, detailed, or raw)
        match_type: Type of host matching to use ("exact" or "contains")
        
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
def parse_and_save_charles_log_by_path(file_path: str, path: str, output_dir: str = "./output", format_type: str = "detailed", match_type: str = "exact") -> Dict:
    """
    Parse a Charles log file (.chls or .chlsj) for a specific :path and save the result to the specified directory.
    
    Args:
        file_path: Path to the Charles log file
        path: The :path to filter by (e.g., "/api/v2/fetch?param=value")
        output_dir: Directory to save the converted JSON file
        format_type: Type of output format (summary, detailed, or raw)
        match_type: Type of path matching to use ("exact" or "contains")
        
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
            result = _parse_chlsj_file_by_path(file_path, path, format_type, match_type)
            
            # Generate output filename
            base_name = os.path.basename(file_path)
            name_without_ext = os.path.splitext(base_name)[0]
            safe_path = path.replace("/", "_").replace("?", "_").replace("=", "_").replace("&", "_")
            match_str = "exact" if match_type == "exact" else "contains"
            output_file = os.path.join(output_dir, f"{name_without_ext}_{safe_path}_{match_str}_parsed.json")
            
            # Write to file
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            return {
                "status": "success",
                "message": f"Successfully parsed and saved to {output_file}",
                "output_file": output_file,
                "filtered_by_path": path,
                "match_type": match_type,
                "entry_count": len(result.get("entries", [])) if "entries" in result else 0
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
        host: The host to filter by (e.g., "paytm.com")
        output_dir: Directory to save the converted JSON file
        format_type: Type of output format (summary, detailed, or raw)
        match_type: Type of host matching to use ("exact" or "contains")
        
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
def parse_and_save_charles_log_exclude_host(file_path: str, host: str, output_dir: str = "./output", format_type: str = "detailed", match_type: str = "exact") -> Dict:
    """
    Parse a Charles log file (.chls or .chlsj) and save entries that don't match the specified host.
    
    Args:
        file_path: Path to the Charles log file
        host: The host to exclude (e.g., "paytm.com")
        output_dir: Directory to save the converted JSON file
        format_type: Type of output format (summary, detailed, or raw)
        match_type: Type of host matching to use ("exact" or "contains")
        
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
            # First try to parse the file as a whole JSON array
            with open(file_path, 'r') as f:
                content = f.read()
                # Try to parse the file as a JSON array
                all_entries = json.loads(content)
                # If entries is not a list, wrap it in one
                if not isinstance(all_entries, list):
                    all_entries = [all_entries]
        except json.JSONDecodeError:
            # If it fails, fall back to line-by-line parsing
            all_entries = []
            with open(file_path, 'r') as f:
                # .chlsj files may contain one JSON object per line
                for line in f:
                    try:
                        if line.strip():  # Skip empty lines
                            entry = json.loads(line.strip())
                            all_entries.append(entry)
                    except json.JSONDecodeError:
                        continue  # Skip invalid lines
        
        # Filter entries that don't match the host and exclude .js, .svg, .png files
        filtered_entries = []
        for entry in all_entries:
            entry_host = entry.get("host", "")
            entry_path = entry.get("path", "")
            
            # Skip if path is None or contains .js, .svg, or .png
            if entry_path is None or any(ext in entry_path.lower() for ext in [".js", ".svg", ".png"]):
                continue
            
            # Skip if host is None
            if entry_host is None:
                continue
            
            # Include entries that don't match the host
            if match_type == "exact":
                # Exact match (case-insensitive)
                if entry_host.lower() != host.lower():
                    filtered_entries.append(entry)
            else:  # "contains"
                # Substring match (case-insensitive)
                if host.lower() not in entry_host.lower():
                    filtered_entries.append(entry)
        
        # Process entries based on format type
        result = None
        if format_type == "raw":
            result = {"entries": filtered_entries, "excluded_host": host, "match_type": match_type}
        elif format_type == "summary":
            # Reuse the summary logic from _parse_chlsj_file_by_host
            result = _process_entries_summary(filtered_entries, host, match_type, is_exclude=True)
        else:
            # Reuse the detailed logic from _parse_chlsj_file_by_host
            result = _process_entries_detailed(filtered_entries, host, match_type, is_exclude=True)
        
        # Generate output filename
        base_name = os.path.basename(file_path)
        name_without_ext = os.path.splitext(base_name)[0]
        safe_host = host.replace(".", "_").replace("/", "_").replace(":", "_")
        match_str = "exact" if match_type == "exact" else "contains"
        output_file = os.path.join(output_dir, f"{name_without_ext}_exclude_{safe_host}_{match_str}_parsed.json")
        
        # Write to file
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        return {
            "status": "success",
            "message": f"Successfully parsed and saved to {output_file}",
            "output_file": output_file,
            "excluded_host": host,
            "match_type": match_type,
            "entry_count": len(filtered_entries)
        }
    
    # For .chls files (binary format)
    return {"error": "Binary .chls files are not supported yet, please export as .chlsj from Charles"}

def _process_entries_summary(entries, host, match_type, is_exclude=False):
    """Helper function to generate summary format for entries"""
    summary = {
        "total_entries": len(entries),
        "excluded_host" if is_exclude else "filtered_by_host": host,
        "match_type": match_type,
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
    
    for entry in entries:
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
    if len(entries) > 0:
        summary["timing"]["avg"] = summary["timing"]["total"] / len(entries)
    
    # If no entries, reset min to 0
    if summary["timing"]["min"] == float('inf'):
        summary["timing"]["min"] = 0
        
    return summary

def _process_entries_detailed(entries, host, match_type, is_exclude=False):
    """Helper function to generate detailed format for entries"""
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
    
    return {
        "entries": processed_entries,
        "excluded_host" if is_exclude else "filtered_by_host": host,
        "match_type": match_type
    }

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
            all_entries = json.loads(content)
            # If entries is not a list, wrap it in one
            if not isinstance(all_entries, list):
                all_entries = [all_entries]
    except json.JSONDecodeError:
        # If it fails, fall back to line-by-line parsing
        all_entries = []
        with open(file_path, 'r') as f:
            # .chlsj files may contain one JSON object per line
            for line in f:
                try:
                    if line.strip():  # Skip empty lines
                        entry = json.loads(line.strip())
                        all_entries.append(entry)
                except json.JSONDecodeError:
                    continue  # Skip invalid lines
    
    # Filter out entries with .js, .svg, or .png in the path
    entries = []
    for entry in all_entries:
        path = entry.get("path", "")
        # Skip if path is None or contains .js, .svg, or .png
        if path is not None and not any(ext in path.lower() for ext in [".js", ".svg", ".png"]):
            entries.append(entry)
    
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

def _parse_chlsj_file_by_path(file_path: str, path: str, format_type: str, match_type: str = "exact") -> Dict:
    """
    Parse a .chlsj file (Charles log in JSON format) and filter by path
    
    Args:
        file_path: Path to the .chlsj file
        path: Path to filter by
        format_type: Type of output format (summary, detailed, or raw)
        match_type: Type of path matching to use ("exact" or "contains")
        
    Returns:
        Dictionary with parsed data for the specified path
    """
    # First try to parse the file as a whole JSON array
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            # Try to parse the file as a JSON array
            all_entries = json.loads(content)
            # If entries is not a list, wrap it in one
            if not isinstance(all_entries, list):
                all_entries = [all_entries]
    except json.JSONDecodeError:
        # If it fails, fall back to line-by-line parsing
        all_entries = []
        with open(file_path, 'r') as f:
            # .chlsj files may contain one JSON object per line
            for line in f:
                try:
                    if line.strip():  # Skip empty lines
                        entry = json.loads(line.strip())
                        all_entries.append(entry)
                except json.JSONDecodeError:
                    continue  # Skip invalid lines
    
    # Filter entries by path based on match_type and exclude .js, .svg, .png files
    filtered_entries = []
    for entry in all_entries:
        entry_path = entry.get("path", "")
        
        # Skip if path is None or contains .js, .svg, or .png
        if entry_path is None or any(ext in entry_path.lower() for ext in [".js", ".svg", ".png"]):
            continue
        
        # Apply filtering based on match type
        if match_type == "exact":
            # Exact match (case-insensitive)
            if entry_path.lower() == path.lower():
                filtered_entries.append(entry)
        else:  # "contains"
            # Substring match (case-insensitive)
            if path.lower() in entry_path.lower():
                filtered_entries.append(entry)
    
    # Process based on format type
    if format_type == "raw":
        return {"entries": filtered_entries, "filtered_by_path": path, "match_type": match_type}
    
    elif format_type == "summary":
        summary = {
            "total_entries": len(filtered_entries),
            "filtered_by_path": path,
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
        
        return {"entries": processed_entries, "filtered_by_path": path, "match_type": match_type}

def _parse_chlsj_file_by_host(file_path: str, host: str, format_type: str, match_type: str = "exact") -> Dict:
    """
    Parse a .chlsj file (Charles log in JSON format) and filter by host
    
    Args:
        file_path: Path to the .chlsj file
        host: Host to filter by
        format_type: Type of output format (summary, detailed, or raw)
        match_type: Type of host matching to use ("exact" or "contains")
        
    Returns:
        Dictionary with parsed data for the specified host
    """
    # First try to parse the file as a whole JSON array
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            # Try to parse the file as a JSON array
            all_entries = json.loads(content)
            # If entries is not a list, wrap it in one
            if not isinstance(all_entries, list):
                all_entries = [all_entries]
    except json.JSONDecodeError:
        # If it fails, fall back to line-by-line parsing
        all_entries = []
        with open(file_path, 'r') as f:
            # .chlsj files may contain one JSON object per line
            for line in f:
                try:
                    if line.strip():  # Skip empty lines
                        entry = json.loads(line.strip())
                        all_entries.append(entry)
                except json.JSONDecodeError:
                    continue  # Skip invalid lines
    
    # Filter entries by host based on match_type and exclude .js, .svg, .png files
    filtered_entries = []
    for entry in all_entries:
        entry_host = entry.get("host", "")
        entry_path = entry.get("path", "")
        
        # Skip if path is None or contains .js, .svg, or .png
        if entry_path is None or any(ext in entry_path.lower() for ext in [".js", ".svg", ".png"]):
            continue
        
        # Skip if host is None
        if entry_host is None:
            continue
        
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
            "filtered_by_host": host,
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
        # Load the parsed data
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Create shared directory if it doesn't exist
        shared_dir = "/Users/pranjulraizada/NewAIProject/git/mcp-charles-shared/output"
        if not os.path.exists(shared_dir):
            os.makedirs(shared_dir)
        
        # Copy the file to the shared directory
        output_file = os.path.join(shared_dir, os.path.basename(file_path))
        shutil.copyfile(file_path, output_file)
        
        return {
            "status": "success",
            "message": f"File saved to shared directory: {output_file}",
            "note": "Please run the standalone dashboard from the mcp-charles-dashboard repository to view the data",
            "command": "cd ../mcp-charles-dashboard && ./run_dashboard.sh"
        }
    except Exception as e:
        return {"error": f"Error preparing dashboard: {str(e)}"}

@mcp.tool()
def compare_api_structures(file_paths: List[str], output_dir: str = "./output", comparison_level: str = "detailed") -> Dict:
    """
    Compare multiple Charles log files to identify differences in API structures.
    
    Args:
        file_paths: List of paths to parsed JSON files (2-3 files)
        output_dir: Directory to save the comparison report
        comparison_level: Level of comparison (basic, detailed, comprehensive)
        
    Returns:
        A dictionary containing the comparison results
    """
    # Validate input parameters
    if len(file_paths) < 2:
        return {"error": "At least two files are required for comparison"}
    
    if len(file_paths) > 3:
        return {"error": "Maximum of three files can be compared at once"}
    
    # Validate all files exist and are JSON
    for file_path in file_paths:
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        if not file_path.endswith('.json'):
            return {"error": f"File must be a JSON file: {file_path}"}
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            return {"error": f"Error creating output directory: {str(e)}"}
    
    try:
        # Load all files
        files_data = []
        file_names = []
        
        for file_path in file_paths:
            with open(file_path, 'r') as f:
                data = json.load(f)
                files_data.append(data)
                file_names.append(os.path.basename(file_path))
        
        # Group APIs by endpoints across files
        endpoint_mapping = _map_endpoints_across_files(files_data, file_names)
        
        # Analyze differences
        comparison_results = _analyze_api_differences(endpoint_mapping, comparison_level)
        
        # Count endpoints with changes
        endpoints_with_changes = sum(1 for endpoint in comparison_results.values() if endpoint["has_changes"])
        
        # Generate a summary report
        summary = {
            "comparison_time": datetime.now().isoformat(),
            "files_compared": file_names,
            "total_endpoints_analyzed": len(endpoint_mapping),
            "endpoints_with_changes": endpoints_with_changes,
            "comparison_level": comparison_level,
            "detailed_results": comparison_results
        }
        
        # Write results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"api_comparison_{timestamp}.json")
        
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return {
            "status": "success",
            "message": f"Successfully compared {len(file_paths)} files and saved results to {output_file}",
            "output_file": output_file,
            "summary": {
                "total_endpoints": len(endpoint_mapping),
                "endpoints_with_changes": endpoints_with_changes,
                "files_compared": file_names
            },
            "detailed_results": comparison_results  # Include detailed results in the return value
        }
        
    except Exception as e:
        return {"error": f"Error comparing API structures: {str(e)}"}

def _map_endpoints_across_files(files_data: List[Dict], file_names: List[str]) -> Dict:
    """
    Map endpoints across multiple files to prepare for comparison.
    
    Args:
        files_data: List of parsed data from each file
        file_names: List of file names corresponding to the data
        
    Returns:
        Dictionary mapping endpoints to their occurrences in each file
    """
    endpoint_mapping = {}
    
    for idx, data in enumerate(files_data):
        file_name = file_names[idx]
        
        # Handle both 'data' and 'entries' fields
        entries = data.get('data', data.get('entries', []))
        if not entries:
            continue
        
        # Process each entry
        for entry_idx, entry in enumerate(entries):
            # Create a unique key for this API endpoint using :path as primary key
            method = entry.get("method", entry.get("request", {}).get("method", "UNKNOWN"))
            full_path = entry.get(":path")  # Get the :path field
            
            # If :path is not available, construct it from path and query parameters
            if not full_path:
                path = entry.get("path", "UNKNOWN")
                query = ""
                # Try to get query parameters from different possible locations
                if "request" in entry:
                    request = entry["request"]
                    if "query" in request:
                        query = "?" + request["query"] if request["query"] else ""
                    elif "queryString" in request:
                        query = "?" + request["queryString"] if request["queryString"] else ""
                full_path = path + query
            
            # Use :path as the primary key, with method as secondary key
            endpoint_key = f"{method}:{full_path}"
            
            # Initialize endpoint data if not seen before
            if endpoint_key not in endpoint_mapping:
                endpoint_mapping[endpoint_key] = {
                    "method": method,
                    "path": full_path,  # Store the full path including query parameters
                    "has_changes": False,
                    "present_in": [],
                    "missing_in": [],
                    "instance_counts": {},
                    "differences": {
                        "request": {},
                        "response": {},
                        "headers": {},
                        "status_codes": {},
                        "parameters": {}
                    }
                }
            
            # Update presence information
            if file_name not in endpoint_mapping[endpoint_key]["present_in"]:
                endpoint_mapping[endpoint_key]["present_in"].append(file_name)
            
            # Store this occurrence with instance index
            if file_name not in endpoint_mapping[endpoint_key]["instance_counts"]:
                endpoint_mapping[endpoint_key]["instance_counts"][file_name] = 0
            endpoint_mapping[endpoint_key]["instance_counts"][file_name] += 1
            
            # Store complete instance data
            instance_data = {
                "index": entry_idx,
                "status": entry.get("status", entry.get("response", {}).get("status")),
                "timestamp": entry.get("timestamp"),
                "request": {
                    "headers": entry.get("request_headers", entry.get("request", {}).get("headers", {})),
                    "body": entry.get("request_body", entry.get("request", {}).get("body")),
                    "cookies": entry.get("request_cookies", entry.get("request", {}).get("cookies", [])),
                    "query_params": entry.get("request_query_params", entry.get("request", {}).get("query_params", []))
                },
                "response": {
                    "headers": entry.get("response_headers", entry.get("response", {}).get("headers", {})),
                    "body": entry.get("response_body", entry.get("response", {}).get("body")),
                    "cookies": entry.get("response_cookies", entry.get("response", {}).get("cookies", []))
                }
            }
            
            # Compare with previous instances if they exist
            for other_file in endpoint_mapping[endpoint_key]["present_in"]:
                if other_file != file_name:
                    comparison_key = f"{file_name}_vs_{other_file}"
                    if comparison_key not in endpoint_mapping[endpoint_key]["differences"]:
                        endpoint_mapping[endpoint_key]["differences"][comparison_key] = {}
                    
                    # Compare request/response data
                    endpoint_mapping[endpoint_key]["differences"][comparison_key] = {
                        "instance_details": {
                            file_name: {
                                "available": True,
                                "index": instance_data["index"],
                                "timestamp": instance_data["timestamp"]
                            }
                        }
                    }
                    
                    # Compare status codes
                    if instance_data["status"] is not None:
                        endpoint_mapping[endpoint_key]["differences"][comparison_key]["status_difference"] = {
                            file_name: instance_data["status"]
                        }
                    
                    # Compare request/response data
                    _compare_request_response(
                        instance_data["request"],
                        instance_data["response"],
                        file_name,
                        endpoint_mapping[endpoint_key]["differences"][comparison_key]
                    )
    
    return endpoint_mapping

def _compare_request_response(request: Dict, response: Dict, file_name: str, result_container: Dict) -> None:
    """
    Compare request and response data between two API calls.
    
    Args:
        request: Request data from current file
        response: Response data from current file
        file_name: Name of the current file
        result_container: Dictionary to store comparison results
    """
    # Compare request data
    if request:
        if "request_differences" not in result_container:
            result_container["request_differences"] = {}
        result_container["request_differences"][file_name] = request

    # Compare response data
    if response:
        if "response_differences" not in result_container:
            result_container["response_differences"] = {}
        result_container["response_differences"][file_name] = response
        
        # Extract and store response status and message
        if response.get("body"):
            try:
                if isinstance(response["body"], str):
                    body = json.loads(response["body"])
                else:
                    body = response["body"]
                    
                if isinstance(body, dict):
                    status = body.get("status") or body.get("statusCode") or body.get("code")
                    message = body.get("message") or body.get("statusMessage")
                    
                    if status or message:
                        if "response_status_summary" not in result_container:
                            result_container["response_status_summary"] = {}
                        result_container["response_status_summary"][file_name] = {
                            "status": status,
                            "message": message
                        }
            except:
                pass

def _compare_parameters(param1, param2, file1: str, file2: str, path: List[str] = None) -> Dict:
    """
    Perform a detailed comparison of parameters between two API entries.
    
    Args:
        param1: Parameter from first file
        param2: Parameter from second file
        file1: Name of first file
        file2: Name of second file
        path: Current path in the parameter hierarchy
        
    Returns:
        Dictionary containing detailed parameter differences
    """
    if path is None:
        path = []
        
    differences = {}
    current_path = ".".join(path) if path else "root"
    
    # Handle None values
    if param1 is None and param2 is None:
        return differences
    elif param1 is None:
        differences[current_path] = {
            "type": "missing_in_first",
            "value": str(param2)[:100] if param2 is not None else "None"
        }
        return differences
    elif param2 is None:
        differences[current_path] = {
            "type": "missing_in_second",
            "value": str(param1)[:100] if param1 is not None else "None"
        }
        return differences
    
    # Compare dictionaries
    if isinstance(param1, dict) and isinstance(param2, dict):
        # Compare all keys in both dictionaries
        all_keys = set(param1.keys()) | set(param2.keys())
        for key in all_keys:
            new_path = path + [key]
            if key not in param1:
                differences[".".join(new_path)] = {
                    "type": "missing_in_first",
                    "value": str(param2[key])[:100]
                }
            elif key not in param2:
                differences[".".join(new_path)] = {
                    "type": "missing_in_second",
                    "value": str(param1[key])[:100]
                }
            else:
                nested_diff = _compare_parameters(param1[key], param2[key], file1, file2, new_path)
                differences.update(nested_diff)
    
    # Compare lists
    elif isinstance(param1, list) and isinstance(param2, list):
        # Compare list lengths
        if len(param1) != len(param2):
            differences[current_path] = {
                "type": "length_mismatch",
                f"{file1}_length": len(param1),
                f"{file2}_length": len(param2)
            }
        
        # Compare list items
        max_items = min(len(param1), len(param2))
        for i in range(max_items):
            new_path = path + [f"[{i}]"]
            nested_diff = _compare_parameters(param1[i], param2[i], file1, file2, new_path)
            differences.update(nested_diff)
        
        # Report extra items
        for i in range(max_items, len(param1)):
            new_path = path + [f"[{i}]"]
            differences[".".join(new_path)] = {
                "type": "extra_in_first",
                "value": str(param1[i])[:100]
            }
        for i in range(max_items, len(param2)):
            new_path = path + [f"[{i}]"]
            differences[".".join(new_path)] = {
                "type": "extra_in_second",
                "value": str(param2[i])[:100]
            }
    
    # Compare primitive values
    else:
        # Try to parse JSON strings
        parsed1 = _try_parse_json(param1)
        parsed2 = _try_parse_json(param2)
        
        if type(parsed1) != type(parsed2):
            differences[current_path] = {
                "type": "type_mismatch",
                f"{file1}_type": type(parsed1).__name__,
                f"{file2}_type": type(parsed2).__name__,
                f"{file1}_value": str(parsed1)[:100],
                f"{file2}_value": str(parsed2)[:100]
            }
        elif parsed1 != parsed2:
            differences[current_path] = {
                "type": "value_mismatch",
                f"{file1}_value": str(parsed1)[:100],
                f"{file2}_value": str(parsed2)[:100]
            }
    
    return differences

def _analyze_api_differences(endpoint_mapping: Dict, comparison_level: str) -> Dict:
    """
    Analyze differences between API endpoints across files.
    
    Args:
        endpoint_mapping: Mapping of endpoints to their occurrences in each file
        comparison_level: Level of detail for the comparison
        
    Returns:
        Dictionary of comparison results for each endpoint
    """
    comparison_results = {}
    
    for endpoint_key, endpoint_data in endpoint_mapping.items():
        # Skip endpoints that are only present in one file
        if len(endpoint_data["present_in"]) < 2:
            continue
            
        file_names = endpoint_data["present_in"]
        
        # Initialize result structure
        result = {
            "method": endpoint_data["method"],
            "path": endpoint_data["path"],
            "has_changes": False,
            "present_in": file_names,
            "missing_in": endpoint_data["missing_in"],
            "instance_counts": endpoint_data["instance_counts"],
            "differences": endpoint_data["differences"],
            "response_status_summary": {},
            "response_body_differences": {}
        }
        
        # Extract and summarize response differences
        for comparison_key, comparison_data in endpoint_data["differences"].items():
            if "response_differences" in comparison_data:
                for file_name, response_data in comparison_data["response_differences"].items():
                    body = response_data.get("body", {})
                    if isinstance(body, dict) and body.get("text"):
                        try:
                            parsed_body = json.loads(body["text"])
                            if isinstance(parsed_body, dict):
                                # Store response status
                                status_code = parsed_body.get("statusCode") or parsed_body.get("code")
                                status_message = parsed_body.get("statusMessage") or parsed_body.get("message")
                                if status_code or status_message:
                                    result["response_status_summary"][file_name] = {
                                        "code": status_code,
                                        "message": status_message
                                    }
                                
                                # Store response body differences
                                if "response_body_differences" not in result:
                                    result["response_body_differences"] = {}
                                result["response_body_differences"][file_name] = parsed_body
                                
                                # Compare response bodies between files
                                for other_file in file_names:
                                    if other_file != file_name:
                                        comparison_key = f"{file_name}_vs_{other_file}"
                                        if comparison_key not in result["response_body_differences"]:
                                            result["response_body_differences"][comparison_key] = {}
                                            
                                        # Deep compare response structures
                                        if other_file in result["response_body_differences"]:
                                            other_body = result["response_body_differences"][other_file]
                                            differences = _deep_compare_structures(parsed_body, other_body, [], include_values=True)
                                            if differences:
                                                result["response_body_differences"][comparison_key]["differences"] = differences
                                                result["has_changes"] = True
                        except:
                            pass
        
        # Check if there are any differences
        for comparison_key, comparison_data in endpoint_data["differences"].items():
            if comparison_data:
                result["has_changes"] = True
                break
        
        # Add this endpoint's comparison results
        comparison_results[endpoint_key] = result
    
    return comparison_results

def _compare_headers(headers1: Dict, headers2: Dict, file1: str, file2: str, header_type: str, result_container: Dict) -> None:
    """
    Compare headers between two API entries and record differences.
    
    Args:
        headers1: Headers from first file
        headers2: Headers from second file
        file1: Name of first file
        file2: Name of second file
        header_type: Type of headers (request or response)
        result_container: Dictionary to store results in
    """
    comparison_key = f"{file1}_vs_{file2}_{header_type}"
    result_container[comparison_key] = {}
    
    # Find headers in file1 but not in file2
    for header_name, header_value in headers1.items():
        if header_name not in headers2:
            result_container[comparison_key][f"only_in_{file1}"] = result_container[comparison_key].get(f"only_in_{file1}", {})
            result_container[comparison_key][f"only_in_{file1}"][header_name] = header_value
        elif headers2[header_name] != header_value:
            result_container[comparison_key][f"different_values"] = result_container[comparison_key].get("different_values", {})
            result_container[comparison_key][f"different_values"][header_name] = {
                file1: header_value,
                file2: headers2[header_name]
            }
    
    # Find headers in file2 but not in file1
    for header_name, header_value in headers2.items():
        if header_name not in headers1:
            result_container[comparison_key][f"only_in_{file2}"] = result_container[comparison_key].get(f"only_in_{file2}", {})
            result_container[comparison_key][f"only_in_{file2}"][header_name] = header_value
    
    # Remove empty comparison if no differences found
    if not result_container[comparison_key]:
        del result_container[comparison_key]

def _try_parse_json(payload):
    """
    Try to parse a string as JSON, return the original if not possible.
    """
    if isinstance(payload, str):
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            return payload
    return payload

def _deep_compare_structures(obj1, obj2, path, include_values=False):
    """
    Recursively compare two objects and return differences in their structure and values.
    
    Args:
        obj1: First object
        obj2: Second object
        path: Current path in the object hierarchy
        include_values: Whether to include actual values in the comparison
        
    Returns:
        List of differences found
    """
    differences = []
    
    # If both are dictionaries
    if isinstance(obj1, dict) and isinstance(obj2, dict):
        # Check for keys in obj1 not in obj2
        for key in obj1:
            if key not in obj2:
                differences.append({
                    "path": ".".join(path + [key]),
                    "difference": "field_missing_in_second",
                    "value": str(obj1[key])[:100] if include_values else None
                })
            else:
                # Always compare values for primitive types
                if not isinstance(obj1[key], (dict, list)):
                    if obj1[key] != obj2[key]:
                        differences.append({
                            "path": ".".join(path + [key]),
                            "difference": "value_changed",
                            "value1": str(obj1[key])[:100],
                            "value2": str(obj2[key])[:100]
                        })
                # Recursively compare nested structures
                else:
                    nested_diffs = _deep_compare_structures(obj1[key], obj2[key], path + [key], include_values)
                    differences.extend(nested_diffs)
        
        # Check for keys in obj2 not in obj1
        for key in obj2:
            if key not in obj1:
                differences.append({
                    "path": ".".join(path + [key]),
                    "difference": "field_missing_in_first",
                    "value": str(obj2[key])[:100] if include_values else None
                })
    
    # If both are lists, compare all items
    elif isinstance(obj1, list) and isinstance(obj2, list):
        # Compare lengths
        if len(obj1) != len(obj2):
            differences.append({
                "path": ".".join(path) or "root",
                "difference": "array_length_changed",
                "length1": len(obj1),
                "length2": len(obj2)
            })
        
        # Compare all items up to the length of the shorter list
        max_items = min(len(obj1), len(obj2))
        for i in range(max_items):
            item_path = path + [f"[{i}]"]
            # For primitive types, compare values directly
            if not isinstance(obj1[i], (dict, list)):
                if obj1[i] != obj2[i]:
                    differences.append({
                        "path": ".".join(item_path),
                        "difference": "array_item_changed",
                        "value1": str(obj1[i])[:100],
                        "value2": str(obj2[i])[:100]
                    })
            # For complex types, compare recursively
            else:
                item_diffs = _deep_compare_structures(obj1[i], obj2[i], item_path, include_values)
                differences.extend(item_diffs)
        
        # Report extra items in longer list
        if len(obj1) > len(obj2):
            for i in range(len(obj2), len(obj1)):
                differences.append({
                    "path": ".".join(path + [f"[{i}]"]),
                    "difference": "extra_item_in_first",
                    "value": str(obj1[i])[:100] if include_values else None
                })
        elif len(obj2) > len(obj1):
            for i in range(len(obj1), len(obj2)):
                differences.append({
                    "path": ".".join(path + [f"[{i}]"]),
                    "difference": "extra_item_in_second",
                    "value": str(obj2[i])[:100] if include_values else None
                })
    
    # If types are different, record the difference
    elif type(obj1) != type(obj2):
        differences.append({
            "path": ".".join(path) or "root",
            "difference": "type_changed",
            "type1": str(type(obj1).__name__),
            "type2": str(type(obj2).__name__),
            "value1": str(obj1)[:100] if include_values else None,
            "value2": str(obj2)[:100] if include_values else None
        })
    # For primitive types, compare values if they're different
    elif obj1 != obj2:
        differences.append({
            "path": ".".join(path) or "root",
            "difference": "value_changed",
            "value1": str(obj1)[:100],
            "value2": str(obj2)[:100]
        })
    
    return differences

# Run the server if executed directly
if __name__ == "__main__":
    import sys
    mcp.run(transport='stdio') 
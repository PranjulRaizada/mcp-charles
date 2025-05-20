# Charles Proxy Log Parser MCP Server

This is an MCP (Model Context Protocol) server implementation for parsing Charles Proxy log files (.chlsj). It provides tools for quickly extracting and analyzing data from Charles Proxy HTTP session logs.

## Features

- Parse Charles Proxy log files (.chlsj)
- Generate different views of the log data:
  - Summary view: statistics on methods, status codes, hosts, etc.
  - Detailed view: all HTTP request and response details
  - Raw view: the original JSON data
- Process large log files efficiently by breaking them into manageable chunks
- Support for different Charles log formats:
  - Line-by-line JSON objects (one JSON object per line)
  - Single JSON array containing all records
- Save parsed results to JSON files
- Interactive dashboard for visualizing log data with charts and tables

## Requirements

- Python 3.7 or higher
- `mcp` library

## Installation

Clone this repository and install the requirements:

```bash
git clone https://github.com/yourusername/charles-proxy-log-parser-mcp.git
cd charles-proxy-log-parser-mcp
```

### Setting up the environment

#### On Windows:
```bash
setup_venv.bat
```

#### On macOS/Linux:
```bash
chmod +x setup_venv.sh
./setup_venv.sh
```

## Usage

```bash
python client.py /path/to/your-file.chlsj [options]
```

### Options:

- `--format {summary,detailed,raw}` - Output format (default: summary)
- `--save` - Save parsed results to a file
- `--output-dir DIR` - Directory to save results (default: ./output)
- `--dashboard` - Open an interactive dashboard in your browser to visualize the results

### Examples:

```bash
# Parse a file and print summary information
python client.py /path/to/your-file.chlsj

# Parse a file and save detailed information
python client.py /path/to/your-file.chlsj --format detailed --save

# Parse a file and open the dashboard
python client.py /path/to/your-file.chlsj --dashboard

# Parse a file, save the detailed results, and open the dashboard
python client.py /path/to/your-file.chlsj --format detailed --save --dashboard --output-dir ./output
```

## Available Dashboards

### Interactive Dashboard

When using the `--dashboard` option, an interactive dashboard will open in your web browser showing:

- Summary statistics of the log file
- Request methods distribution
- Status codes distribution
- Top hosts
- Timing information
- Detailed data explorer with filtering options

### Simple Dashboard

For environments where installing many dependencies might be challenging, a simple HTML-based dashboard is also available:

```bash
python simple_dashboard.py /path/to/parsed-file.json
```

## Output Formats

### Summary Format
```json
{
  "total_entries": 123,
  "request_methods": {
    "GET": 80,
    "POST": 30,
    "PUT": 10,
    "DELETE": 3
  },
  "status_codes": {
    "200": 95,
    "404": 10,
    "500": 5,
    "302": 13
  },
  "hosts": {
    "api.example.com": 40,
    "cdn.example.com": 75,
    "analytics.example.com": 8
  },
  "content_types": {
    "application/json": 50,
    "text/html": 30,
    "image/jpeg": 43
  },
  "timing": {
    "min": 50,
    "max": 2500,
    "avg": 350,
    "total": 43050
  }
}
```

### Detailed Format
```json
{
  "entries": [
    {
      "url": "https://api.example.com/users",
      "host": "api.example.com",
      "path": "/users",
      "method": "GET",
      "status": 200,
      "duration": 150,
      "request_headers": {
        "User-Agent": "...",
        "Accept": "application/json"
      },
      "response_headers": {
        "Content-Type": "application/json",
        "Content-Length": "1024"
      },
      "request_body": "...",
      "response_body": "..."
    },
    ...
  ]
}
```

## Processing Large Files

For very large log files, use the `large_file_example.py` script, which processes the file in chunks:

```bash
python large_file_example.py /path/to/large-file.chlsj --output results.json
```

## Notes

- Binary `.chls` files are not supported yet. Please export as `.chlsj` from Charles.
- When dealing with large files, it's recommended to use the `large_file_example.py` script which processes the file in chunks.
- Different versions of Charles Proxy may generate slightly different JSON structures. The parser tries to handle these variations gracefully.

## Limitations

- Currently only supports .chlsj files (JSON format)
- Binary .chls files are not supported yet 
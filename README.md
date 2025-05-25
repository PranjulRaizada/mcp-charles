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
- `--host HOSTNAME` - Filter logs by hostname
- `--match-type {exact,contains}` - Type of hostname matching to use (default: exact)

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

# Filter logs by exact hostname match (default behavior)
python client.py /path/to/your-file.chlsj --format detailed --save --host api.example.com

# Filter logs by hostname containing a substring
python client.py /path/to/your-file.chlsj --format detailed --save --host example.com --match-type contains

# Real-world example: Filter Paytm dashboard logs (exact match)
python client.py /path/to/your-file.chlsj --format detailed --save --output-dir ./output --host dashboard.paytm.com

# Real-world example: Filter all Paytm related logs (substring match)
python client.py /path/to/your-file.chlsj --format detailed --save --output-dir ./output --host paytm.com --match-type contains
```

### Host Filtering

The host filtering functionality allows you to extract only the entries for specific hosts from your Charles logs:

- **Exact Matching (Default)**: Use `--host hostname` to filter logs by exact hostname match
- **Substring Matching**: Use `--host hostname --match-type contains` to filter logs by hostnames containing the specified string

This is particularly useful when debugging specific services in logs with many domains. Examples:

1. `--host dashboard.paytm.com` - Returns only exact matches for "dashboard.paytm.com"
2. `--host paytm.com --match-type contains` - Returns all hosts containing "paytm.com" (like "dashboard.paytm.com", "api.paytm.com", etc.)

The filtered results can be saved and visualized just like normal parsing results.

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

# API Comparison Dashboard

This tool provides automated comparison of API structures between different versions of Charles proxy logs, helping you identify changes in API contracts over time.

## Features

- Compare API structures between two or three JSON files
- Identify added, removed, and modified endpoints
- Detailed analysis of changes in request/response structures
- Visual dashboard for exploring API differences
- Support for custom metadata to track versions

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mcp-charles-dashboard-comparision.git
   cd mcp-charles-dashboard-comparision
   ```

2. Run the dashboard:
   ```bash
   ./run_dashboard.sh
   ```
   This will:
   - Create a virtual environment if it doesn't exist
   - Install required dependencies
   - Start the dashboard on http://localhost:5000

## Usage

### 1. Generate Comparison Data

Use the `dashboard_ready_comparison.py` script to compare API logs and generate dashboard-ready data:

```bash
python dashboard_ready_comparison.py \
  --file_paths '["/path/to/file1.json", "/path/to/file2.json"]' \
  --output_dir "./dashboard_data" \
  --comparison_level "comprehensive" \
  --metadata '{"version_labels": ["v1.0", "v2.0"]}'
```

Parameters:
- `file_paths`: JSON array of file paths to compare (2-3 files)
- `output_dir`: Directory to save comparison results (default: "./dashboard_data")
- `comparison_level`: Level of detail for comparison (choices: "basic", "detailed", "comprehensive")
- `metadata`: Optional JSON string of metadata to include in the results

### 2. View the Dashboard

Once you've generated comparison data, you can view it in the dashboard:

1. Start the dashboard if not already running:
   ```bash
   ./run_dashboard.sh
   ```

2. Open your browser to http://localhost:5000

## Dashboard Features

The dashboard provides:

- List of all comparisons with timestamps
- Summary statistics for each comparison
- Visual representation of API changes
- Detailed view of differences for each endpoint
- Filtering options to focus on specific change types
- Sortable tables for easy navigation

## Example

```bash
# Compare two API logs
python dashboard_ready_comparison.py \
  --file_paths '["/path/to/old_api.json", "/path/to/new_api.json"]' \
  --output_dir "./dashboard_data" \
  --comparison_level "comprehensive" \
  --metadata '{"version_labels": ["v1.2.3", "v1.3.0"], "release_date": "2024-03-20"}'

# Start the dashboard
./run_dashboard.sh
```

## Project Structure

```
.
├── README.md
├── requirements.txt
├── run_dashboard.sh
├── dashboard_ready_comparison.py
├── simple_dashboard.py
├── comparison_utils.py
└── templates/
    ├── base.html
    ├── comparison.html
    ├── error.html
    └── index.html
```

## Integration

This tool can be integrated into your CI/CD pipeline to automatically generate comparison reports between different releases or environments. 
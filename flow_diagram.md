# Charles Log Parser Project Flow Diagram

```mermaid
graph TD
    %% Main components and flows
    User([User]) -->|Provides .chlsj file| Parser
    User -->|Views| Dashboard
    
    %% Core components with separation
    subgraph "mcp-charles"
        Parser[Parser Tools] -->|Process data| LogData[Parsed Data]
        LogData -->|Save to shared dir| SharedOutput[Shared Output]
    end
    
    subgraph "mcp-charles-shared"
        SharedOutput -->|JSON files| SharedDir[/output/ dir]
    end
    
    subgraph "mcp-charles-dashboard"
        SharedDir -->|Read JSON| Dashboard[Dashboard]
    end
    
    %% Parser tools
    Parser -->|Basic parse| Basic[parse_charles_log]
    Parser -->|Save results| Save[parse_and_save_charles_log]
    Parser -->|Large files| Large[read_large_file_part]
    Parser -->|Filter by host| Filter[parse_by_host]
    
    %% Output options
    Dashboard -->|Streamlit| StreamView[Interactive View]
    
    %% Output formats
    LogData -->|Raw| RawJSON[Raw JSON]
    LogData -->|Summary| SummaryStats[Statistics]
    LogData -->|Detailed| DetailedView[Detailed Data]
    
    %% Styling
    classDef core fill:#f9f,stroke:#333,stroke-width:2px;
    classDef shared fill:#ffc,stroke:#333,stroke-width:2px;
    classDef dashboard fill:#bbf,stroke:#333,stroke-width:1px;
    classDef tool fill:#bfb,stroke:#333,stroke-width:1px;
    
    class Parser,LogData core;
    class SharedOutput,SharedDir shared;
    class Dashboard,StreamView dashboard;
    class Basic,Save,Large,Filter tool;
```

# Simplified Flow Diagram

For a simpler understanding of the project workflow:

```mermaid
graph TD
    A[Charles Proxy] -->|Export logs as .chlsj| B[Log File]
    B --> C{Parse Log}
    C -->|Basic parsing| D[All Entries]
    C -->|Filter by host| E[Host-specific Entries]
    
    D --> F[Generate Output]
    E --> F
    
    F -->|Raw format| G[Raw JSON]
    F -->|Summary format| H[Summary Statistics]
    F -->|Detailed format| I[Detailed Entries]
    
    G --> J[Save to Shared Directory]
    H --> J
    I --> J
    
    J --> K[Dashboard Reads Files]
    K --> L[Visualize in Streamlit]
    
    style A fill:#f9d5e5,stroke:#333,stroke-width:2px
    style B fill:#eeeeee,stroke:#333,stroke-width:2px
    style C fill:#e3f2fd,stroke:#333,stroke-width:2px
    style D fill:#e8f5e9,stroke:#333,stroke-width:2px
    style E fill:#e8f5e9,stroke:#333,stroke-width:2px
    style F fill:#fff9c4,stroke:#333,stroke-width:2px
    style G fill:#f5f5f5,stroke:#333,stroke-width:2px
    style H fill:#f5f5f5,stroke:#333,stroke-width:2px
    style I fill:#f5f5f5,stroke:#333,stroke-width:2px
    style J fill:#ffe0b2,stroke:#333,stroke-width:2px
    style K fill:#d1c4e9,stroke:#333,stroke-width:2px
    style L fill:#bbdefb,stroke:#333,stroke-width:2px
```

## Project Components Explanation

### Component Separation
The project is now divided into three separate components:
- **mcp-charles**: Contains the parser functionality
- **mcp-charles-dashboard**: Contains the dashboard visualization
- **mcp-charles-shared**: Shared directory for communication between components

### mcp-charles (Parser Component)
- **server.py**: MCP server implementing the parser tools
- **client.py**: Client interface for users to parse Charles log files
- **parse_charles_log**: Tool to parse a log file and return data
- **parse_and_save_charles_log**: Tool to parse and save results to the shared directory
- **large_file_example.py**: Script to process large files in chunks

### mcp-charles-shared (Shared Directory)
- **output/**: Directory where parsed JSON files are stored
- Used for communication between the parser and dashboard components

### mcp-charles-dashboard (Dashboard Component)
- **dashboard.py**: Streamlit app for data visualization
- **run_dashboard.sh/.bat**: Scripts to launch the Streamlit dashboard
- **requirements.txt**: Dashboard-specific dependencies

### Data Flow
1. User provides a Charles log file (.chlsj)
2. File is parsed using MCP tools in the mcp-charles component
3. Results are saved to the shared directory (mcp-charles-shared/output)
4. User runs the dashboard from the mcp-charles-dashboard component
5. Dashboard reads parsed files from the shared directory
6. Dashboard visualizes the data using Streamlit

### Alternative Flows
- **Large File Processing**: For very large log files, using large_file_example.py in the mcp-charles component for chunk-by-chunk processing
- **Direct API Usage**: Clients can use the MCP API directly for custom integrations 
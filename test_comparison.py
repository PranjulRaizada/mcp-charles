import json
from server import _map_endpoints_across_files, _analyze_api_differences

def format_comparison_results(results):
    """Format comparison results in a more readable way."""
    output = []
    
    for endpoint_key, result in results.items():
        # Endpoint header
        output.append("\n" + "="*80)
        output.append(f"\nEndpoint: {result['method']} {result['host']}{result['path']}")
        output.append("-"*80)
        
        # Instance counts
        output.append("\nInstances found:")
        for file_name, count in result['instance_counts'].items():
            output.append(f"  - {file_name}: {count} instance(s)")
        
        # Changes summary
        if result['has_changes']:
            output.append("\n🔍 Differences detected!")
        else:
            output.append("\n✅ No differences found")
        
        # Detailed differences
        for diff_key, diff_data in result['differences'].items():
            if diff_key in ['request', 'response', 'headers', 'status_codes', 'parameters']:
                continue
                
            if 'instance' in diff_key:
                output.append(f"\nComparing {diff_key}:")
                
                # Instance details
                if 'instance_details' in diff_data:
                    details = diff_data['instance_details']
                    for file_name, file_details in details.items():
                        status = "✅ Present" if file_details['available'] else "❌ Missing"
                        output.append(f"  {file_name}:")
                        output.append(f"    - Status: {status}")
                        if file_details['available']:
                            output.append(f"    - Index: {file_details['index']}")
                            output.append(f"    - Timestamp: {file_details['timestamp']}")
                
                # Request differences
                if 'request_differences' in diff_data:
                    output.append("\n  Request Differences:")
                    for path, change in diff_data['request_differences'].items():
                        output.append(f"    - {path}:")
                        if change['type'] == 'missing_in_first':
                            output.append(f"      ❌ Missing in first file")
                            output.append(f"      ✅ Present in second file: {change['value']}")
                        elif change['type'] == 'missing_in_second':
                            output.append(f"      ✅ Present in first file: {change['value']}")
                            output.append(f"      ❌ Missing in second file")
                        elif change['type'] == 'value_mismatch':
                            output.append(f"      First file: {change['file1_value']}")
                            output.append(f"      Second file: {change['file2_value']}")
                
                # Response differences
                if 'response_differences' in diff_data:
                    output.append("\n  Response Differences:")
                    for path, change in diff_data['response_differences'].items():
                        output.append(f"    - {path}:")
                        if change['type'] == 'missing_in_first':
                            output.append(f"      ❌ Missing in first file")
                            output.append(f"      ✅ Present in second file: {change['value']}")
                        elif change['type'] == 'missing_in_second':
                            output.append(f"      ✅ Present in first file: {change['value']}")
                            output.append(f"      ❌ Missing in second file")
                        elif change['type'] == 'value_mismatch':
                            output.append(f"      First file: {change['file1_value']}")
                            output.append(f"      Second file: {change['file2_value']}")
                
                # Status differences
                if 'status_difference' in diff_data:
                    output.append("\n  Status Differences:")
                    for file_name, status in diff_data['status_difference'].items():
                        output.append(f"    - {file_name}: {status}")
                
                # No differences note
                if 'note' in diff_data and 'No differences' in diff_data['note']:
                    output.append("\n  ✅ Instances are identical")
        
        output.append("\n" + "="*80)
    
    return "\n".join(output)

# Create test data
data1 = {
    "data": [
        {
            "method": "GET",
            "host": "api.example.com",
            "path": "/api/v1/merchantprofile/kyc-banks",
            "status": "COMPLETE",
            "timestamp": "2024-05-23T10:00:00",
            "request": {
                "headers": {},
                "body": None
            },
            "response": {
                "headers": {},
                "body": "{}"
            }
        },
        {
            "method": "GET",
            "host": "api.example.com",
            "path": "/api/v1/merchantprofile/kyc-banks",
            "status": "COMPLETE",
            "timestamp": "2024-05-23T10:01:00",
            "request": {
                "headers": {},
                "body": None
            },
            "response": {
                "headers": {},
                "body": "{}"
            }
        }
    ]
}

data2 = {
    "data": [
        {
            "method": "GET",
            "host": "api.example.com",
            "path": "/api/v1/merchantprofile/kyc-banks",
            "status": "COMPLETE",
            "timestamp": "2024-05-23T10:00:00",
            "request": {
                "headers": {},
                "body": "dadadadadad"
            },
            "response": {
                "headers": {},
                "body": "{}"
            }
        },
        {
            "method": "GET",
            "host": "api.example.com",
            "path": "/api/v1/merchantprofile/kyc-banks",
            "status": "COMPLETE",
            "timestamp": "2024-05-23T10:01:00",
            "request": {
                "headers": {},
                "body": None
            },
            "response": {
                "headers": {},
                "body": "{}"
            }
        }
    ]
}

# Run comparison
endpoint_mapping = _map_endpoints_across_files([data1, data2], ["file1.json", "file2.json"])
results = _analyze_api_differences(endpoint_mapping, "detailed")

# Print results in both formats
print("\nDetailed JSON Results:")
print(json.dumps(results, indent=2))

print("\nFormatted Results:")
print(format_comparison_results(results)) 
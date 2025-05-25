import json
import sys
from datetime import datetime

def analyze_structure(data, file_name):
    print(f"\nAnalyzing structure of {file_name}:")
    if isinstance(data, dict):
        print("Top-level keys:", list(data.keys()))
    elif isinstance(data, list):
        print("Top-level is a list with", len(data), "items")
        if data:
            print("First item keys:", list(data[0].keys()) if isinstance(data[0], dict) else "not a dictionary")
    else:
        print("Unexpected top-level type:", type(data))

def find_kyc_endpoints(data, file_name):
    print(f"\nSearching for KYC endpoints in {file_name}:")
    
    def search_in_item(item):
        if isinstance(item, dict):
            path = item.get('path', '')
            if isinstance(path, str) and 'kyc' in path.lower():
                print(f"\nFound endpoint: {path}")
                print("Method:", item.get('method', 'N/A'))
                if 'request' in item:
                    print("Request body:", item['request'].get('body', 'No body'))
                return True
        return False
    
    if isinstance(data, dict):
        # Try to find entries in various possible locations
        for key, value in data.items():
            if isinstance(value, list):
                for item in value:
                    search_in_item(item)
    elif isinstance(data, list):
        for item in data:
            search_in_item(item)

def get_endpoint_instances(data, target_path):
    instances = []
    if isinstance(data, dict):
        entries = data.get('data', [])
        if isinstance(entries, list):
            for entry in entries:
                if isinstance(entry, dict) and entry.get('path') == target_path:
                    instances.append(entry)
    return instances

def compare_endpoints(file1_path, file2_path, target_path):
    # Read files
    with open(file1_path, 'r') as f:
        data1 = json.load(f)
    with open(file2_path, 'r') as f:
        data2 = json.load(f)
    
    # Get all instances of the endpoint from both files
    instances1 = get_endpoint_instances(data1, target_path)
    instances2 = get_endpoint_instances(data2, target_path)
    
    print(f"\nEndpoint: {target_path}")
    print(f"Found {len(instances1)} instances in file 1")
    print(f"Found {len(instances2)} instances in file 2")
    
    print("\nDetailed comparison:")
    
    # Compare each instance
    for i, inst1 in enumerate(instances1):
        print(f"\nFile 1 - Instance {i+1}:")
        print(f"Method: {inst1.get('method')}")
        print(f"Request body: {inst1.get('request', {}).get('body')}")
        print(f"Status: {inst1.get('status')}")
        print(f"Timestamp: {inst1.get('timestamp')}")
    
    print("\n" + "="*50 + "\n")
    
    for i, inst2 in enumerate(instances2):
        print(f"\nFile 2 - Instance {i+1}:")
        print(f"Method: {inst2.get('method')}")
        print(f"Request body: {inst2.get('request', {}).get('body')}")
        print(f"Status: {inst2.get('status')}")
        print(f"Timestamp: {inst2.get('timestamp')}")

# Run analysis
file1 = "/Users/pranjulraizada/NewAIProject/git/mcp-charles-shared/output/Pranjul_detailed.json"
file2 = "/Users/pranjulraizada/NewAIProject/git/mcp-charles-shared/output/Pranjul_detailed_1.json"
target_endpoint = "/api/v1/merchantprofile/kyc-banks"

try:
    with open(file1, 'r') as f:
        data1 = json.load(f)
        analyze_structure(data1, "File 1")
        find_kyc_endpoints(data1, "File 1")
except Exception as e:
    print(f"\nError reading File 1: {str(e)}")

try:
    with open(file2, 'r') as f:
        data2 = json.load(f)
        analyze_structure(data2, "File 2")
        find_kyc_endpoints(data2, "File 2")
except Exception as e:
    print(f"\nError reading File 2: {str(e)}")

compare_endpoints(file1, file2, target_endpoint) 
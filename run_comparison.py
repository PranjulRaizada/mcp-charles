#!/usr/bin/env python3
import json
import os
import sys
import argparse
from server import compare_api_structures

def main():
    parser = argparse.ArgumentParser(description='Compare API structures between Charles log files')
    parser.add_argument('--file_paths', type=str, required=True, help='JSON string array of file paths to compare')
    parser.add_argument('--output_dir', type=str, default='./output', help='Directory to save comparison results')
    parser.add_argument('--comparison_level', type=str, default='detailed', choices=['basic', 'detailed', 'comprehensive'], help='Level of comparison detail')
    
    args = parser.parse_args()
    
    try:
        # Parse the file_paths JSON string into a list
        file_paths = json.loads(args.file_paths)
        
        # Ensure file_paths is a list
        if not isinstance(file_paths, list):
            print("Error: file_paths must be a JSON array of strings")
            sys.exit(1)
            
        # Create output directory if it doesn't exist
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Run the comparison
        result = compare_api_structures(file_paths, args.output_dir, args.comparison_level)
        
        # Print the result
        print(json.dumps(result, indent=2))
        
        # Exit with appropriate status code
        if "error" in result:
            sys.exit(1)
        sys.exit(0)
        
    except json.JSONDecodeError:
        print("Error: file_paths must be a valid JSON array string")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
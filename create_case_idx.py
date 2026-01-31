#!/usr/bin/env python3
import json
import csv
import os
from pathlib import Path

def find_case_files(base_path):
    """Find all case JSON files"""
    case_files = []
    for root, dirs, files in os.walk(base_path):
        if 'cases' in root:
            for file in files:
                if file.endswith('.json'):
                    case_files.append(os.path.join(root, file))
    return case_files

def extract_case_info(file_path):
    """Extract case information from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        case_id = data.get('id', '')
        decision_date = data.get('decision_date', '')
        jurisdiction_id = data.get('jurisdiction', {}).get('id', '')
        court_id = data.get('court', {}).get('id', '')
        
        return {
            'id': case_id,
            'decision_date': decision_date,
            'jurisdiction_id': jurisdiction_id,
            'court_id': court_id,
            'path': file_path
        }
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def main():
    base_path = '/Users/vs/product/case-law'
    output_file = 'case_idx.csv'
    
    print(f"Searching for case files in {base_path}...")
    case_files = find_case_files(base_path)
    print(f"Found {len(case_files)} case files")
    
    print(f"Processing cases and creating {output_file}...")
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'decision_date', 'jurisdiction_id', 'court_id', 'path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        count = 0
        for i, file_path in enumerate(case_files, 1):
            if i % 10000 == 0:
                print(f"Processed {i}/{len(case_files)} files...")
            
            case_info = extract_case_info(file_path)
            if case_info:
                writer.writerow(case_info)
                count += 1
    
    print(f"Done! Created {output_file} with {count} cases")

if __name__ == '__main__':
    main()

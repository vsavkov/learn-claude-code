#!/usr/bin/env python3
"""
Deep analysis of why so many cases are 'unclear'
"""
import json
import os
import re

def analyze_unclear_cases(base_path, num_cases=30):
    """Analyze cases that appear unclear to understand the pattern"""
    
    case_files = []
    for root, dirs, files in os.walk(base_path):
        if 'cases' in root:
            for file in files:
                if file.endswith('.json'):
                    case_files.append(os.path.join(root, file))
                    if len(case_files) >= num_cases:
                        break
        if len(case_files) >= num_cases:
            break
    
    print(f"Deep analysis of {len(case_files)} cases...\n")
    
    for i, file_path in enumerate(case_files, 1):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            opinions = data.get('opinions', [])
            if not opinions:
                opinions = data.get('casebody', {}).get('opinions', [])
            
            majority_opinion = None
            for opinion in opinions:
                if opinion.get('type') == 'majority':
                    majority_opinion = opinion
                    break
            
            if not majority_opinion:
                continue
            
            text = majority_opinion.get('text', '')
            if not text:
                continue
            
            # Get various endings
            last_200 = text[-200:].strip()
            last_500 = text[-500:].strip()
            
            # Check what's actually there
            has_affirmed = 'affirmed' in last_500.lower()
            has_reversed = 'reversed' in last_500.lower()
            has_dismissed = 'dismissed' in last_500.lower()
            has_remanded = 'remanded' in last_500.lower()
            has_vacated = 'vacated' in last_500.lower()
            
            print("="*80)
            print(f"Case {i}: {data.get('name_abbreviation', 'N/A')[:70]}")
            print(f"Court: {data.get('court', {}).get('name_abbreviation', 'N/A')}")
            print("-"*80)
            print(f"Keywords in last 500 chars:")
            print(f"  affirmed={has_affirmed}, reversed={has_reversed}, dismissed={has_dismissed}")
            print(f"  remanded={has_remanded}, vacated={has_vacated}")
            print(f"\nLast 200 characters:")
            print(f"  {last_200}")
            print()
                
        except Exception as e:
            continue

def main():
    base_path = '/Users/vs/product/case-law'
    analyze_unclear_cases(base_path, 30)

if __name__ == '__main__':
    main()

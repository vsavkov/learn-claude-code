#!/usr/bin/env python3
import json
import os
import re

def analyze_opinion_endings(base_path, num_cases=30):
    """Look at the endings of majority opinions to find disposition patterns"""
    
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
    
    print(f"Analyzing endings of {len(case_files)} majority opinions...\n")
    
    for i, file_path in enumerate(case_files, 1):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Get opinions
            opinions = data.get('opinions', [])
            if not opinions:
                opinions = data.get('casebody', {}).get('opinions', [])
            
            # Find majority opinion
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
            
            # Get the last 800 characters (where disposition usually is)
            ending = text[-800:].strip()
            
            # Clean up some whitespace
            ending = ' '.join(ending.split())
            
            print("="*80)
            print(f"Case {i}: {data.get('name_abbreviation', 'N/A')[:80]}")
            print(f"ID: {data.get('id')} | Date: {data.get('decision_date')}")
            print("-"*80)
            print(f"Last ~800 characters of majority opinion:")
            print(ending)
            print()
                
        except Exception as e:
            continue

def main():
    base_path = '/Users/vs/product/case-law'
    analyze_opinion_endings(base_path, 30)

if __name__ == '__main__':
    main()

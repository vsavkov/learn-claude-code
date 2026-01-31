#!/usr/bin/env python3
"""
Diagnose why extraction is difficult
"""
import json
import os
import re

def check_actual_structure(base_path, num_cases=15):
    """Check what's really at the end of opinions"""
    
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
    
    print("DIAGNOSIS: What's really in the opinion endings?\n")
    print("="*80)
    
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
            if len(text) < 100:
                continue
            
            # Look for "Decision" sections
            has_decision_section = bool(re.search(r'(?:IV|V|4|5)\.?\s+(?:DECISION|CONCLUSION|DISPOSITION)', text, re.IGNORECASE))
            
            # Check what's in last parts
            last_500 = text[-500:]
            last_1000 = text[-1000:]
            
            # Count different content types
            citation_count = len(re.findall(r'\d+\s+[A-Z]\.[\w\s\.]+\d+', last_500))
            period_count = last_500.count('.')
            
            # Look for disposition words
            disp_words = []
            for word in ['affirmed', 'reversed', 'dismissed', 'remanded', 'vacated', 'granted', 'denied']:
                if word in last_1000.lower():
                    disp_words.append(word)
            
            print(f"Case {i}: {data.get('name_abbreviation', 'N/A')[:60]}")
            print(f"  Length: {len(text):,} chars")
            print(f"  Has 'Decision' section: {has_decision_section}")
            print(f"  Disposition words found: {', '.join(disp_words) if disp_words else 'NONE'}")
            print(f"  Last 500 chars - Citations: {citation_count}, Periods: {period_count}")
            print(f"  Last 150 chars:")
            
            # Clean up for display
            display_text = ' '.join(last_500[-150:].split())
            print(f"    ...{display_text}")
            print()
                
        except Exception as e:
            continue

def main():
    base_path = '/Users/vs/product/case-law'
    check_actual_structure(base_path, 20)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
import json
import os
from collections import Counter
from pathlib import Path

def analyze_opinion_types(base_path, sample_size=50000):
    """Analyze opinion types in case files"""
    opinion_types = Counter()
    cases_with_opinions = 0
    cases_without_opinions = 0
    total_cases = 0
    sample_cases = {}  # Dict to store samples by type
    
    # Find case files
    case_files = []
    for root, dirs, files in os.walk(base_path):
        if 'cases' in root:
            for file in files:
                if file.endswith('.json'):
                    case_files.append(os.path.join(root, file))
                    if len(case_files) >= sample_size:
                        break
        if len(case_files) >= sample_size:
            break
    
    print(f"Analyzing {len(case_files)} case files...")
    
    for i, file_path in enumerate(case_files, 1):
        if i % 10000 == 0:
            print(f"  Processed {i}/{len(case_files)}...")
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            total_cases += 1
            
            # Try both locations for opinions
            opinions = data.get('opinions', [])
            if not opinions:
                opinions = data.get('casebody', {}).get('opinions', [])
            
            if opinions:
                cases_with_opinions += 1
                for opinion in opinions:
                    opinion_type = opinion.get('type', 'unknown')
                    opinion_types[opinion_type] += 1
                    
                    # Collect samples for each type (max 3 per type)
                    if opinion_type not in sample_cases:
                        sample_cases[opinion_type] = []
                    
                    if len(sample_cases[opinion_type]) < 3:
                        text = opinion.get('text', '')
                        sample_cases[opinion_type].append({
                            'case_id': data.get('id'),
                            'case_name': data.get('name_abbreviation', 'N/A')[:80],
                            'decision_date': data.get('decision_date', 'N/A'),
                            'type': opinion_type,
                            'has_text': bool(text.strip()),
                            'text_length': len(text),
                            'author': opinion.get('author', 'N/A'),
                            'text_preview': text[:300].strip() if text else 'N/A'
                        })
            else:
                cases_without_opinions += 1
                
        except Exception as e:
            # print(f"Error processing {file_path}: {e}")
            continue
    
    return opinion_types, cases_with_opinions, cases_without_opinions, total_cases, sample_cases

def main():
    base_path = '/Users/vs/product/case-law'
    
    print("Analyzing opinion types in case files...\n")
    opinion_types, with_opinions, without_opinions, total, samples = analyze_opinion_types(base_path)
    
    print("\n" + "="*80)
    print("OPINION TYPES ANALYSIS")
    print("="*80)
    
    print(f"\nTotal cases analyzed: {total:,}")
    print(f"Cases with opinions: {with_opinions:,} ({with_opinions/total*100:.1f}%)")
    print(f"Cases without opinions: {without_opinions:,} ({without_opinions/total*100:.1f}%)")
    if opinion_types:
        print(f"Total opinion instances: {sum(opinion_types.values()):,}")
    
    print(f"\n" + "-"*80)
    print("OPINION TYPES FOUND (sorted by frequency):")
    print("-"*80)
    
    if opinion_types:
        for opinion_type, count in opinion_types.most_common():
            percentage = count / sum(opinion_types.values()) * 100
            print(f"{opinion_type:25s}: {count:8,} occurrences ({percentage:5.1f}%)")
    else:
        print("No opinions found in the sample.")
    
    if samples:
        print(f"\n" + "="*80)
        print("SAMPLE OPINIONS BY TYPE:")
        print("="*80)
        
        for opinion_type in sorted(samples.keys()):
            print(f"\n{'='*80}")
            print(f"TYPE: {opinion_type.upper()}")
            print(f"{'='*80}")
            
            for i, sample in enumerate(samples[opinion_type], 1):
                print(f"\nSample {i}:")
                print(f"  Case ID: {sample['case_id']}")
                print(f"  Case: {sample['case_name']}")
                print(f"  Date: {sample['decision_date']}")
                print(f"  Author: {sample['author']}")
                print(f"  Has text: {sample['has_text']}")
                print(f"  Text length: {sample['text_length']:,} characters")
                if sample['has_text'] and sample['text_preview'] != 'N/A':
                    print(f"  Preview: {sample['text_preview']}...")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
import json
import os
import re
from collections import Counter

def extract_decision(opinion_text, case_data):
    """
    Analyze majority opinion text to determine if decision favors plaintiff or defendant.
    Returns: 'plaintiff', 'defendant', 'unclear', or classification details
    """
    
    text_lower = opinion_text.lower()
    
    # Common indicators of outcomes
    plaintiff_indicators = [
        r'\baffirm(?:ed|ing)?\b.*\bfor.*\bplaintiff',
        r'\bjudgment for.*\bplaintiff',
        r'\bplaintiff.*\bprevail',
        r'\bin favor of.*\bplaintiff',
        r'\bplaintiff.*\bentitled to',
        r'\bplaintiff.*\bjudgment',
        r'\brevers(?:ed|ing)?\b.*\bfor.*\bplaintiff',
        r'\bplaintiff.*\bwins?\b',
        r'\bgrant.*\bplaintiff.*\brelief',
    ]
    
    defendant_indicators = [
        r'\baffirm(?:ed|ing)?\b.*\bfor.*\bdefendant',
        r'\bjudgment for.*\bdefendant',
        r'\bdefendant.*\bprevail',
        r'\bin favor of.*\bdefendant',
        r'\bdefendant.*\bentitled to',
        r'\bdefendant.*\bjudgment',
        r'\brevers(?:ed|ing)?\b.*\bfor.*\bdefendant',
        r'\bdismiss(?:ed|ing)?\b',
        r'\bdefendant.*\bwins?\b',
    ]
    
    # Look for affirmed/reversed patterns
    affirmed = bool(re.search(r'\baffirm(?:ed)?\b', text_lower))
    reversed = bool(re.search(r'\brevers(?:ed)?\b', text_lower))
    remanded = bool(re.search(r'\bremand(?:ed)?\b', text_lower))
    dismissed = bool(re.search(r'\bdismiss(?:ed)?\b', text_lower))
    
    # Count indicators
    plaintiff_score = sum(1 for pattern in plaintiff_indicators if re.search(pattern, text_lower))
    defendant_score = sum(1 for pattern in defendant_indicators if re.search(pattern, text_lower))
    
    # Extract disposition phrases (usually at the end)
    disposition_patterns = [
        r'(affirmed|reversed|remanded|dismissed|vacated|granted|denied)',
        r'judgment (?:is )?(?:for|in favor of) (?:the )?(appellant|appellee|plaintiff|defendant)',
        r'(appellant|appellee|plaintiff|defendant) (?:is )?entitled to',
    ]
    
    dispositions = []
    for pattern in disposition_patterns:
        matches = re.findall(pattern, text_lower[-2000:])  # Check last 2000 chars
        dispositions.extend(matches)
    
    return {
        'affirmed': affirmed,
        'reversed': reversed,
        'remanded': remanded,
        'dismissed': dismissed,
        'plaintiff_score': plaintiff_score,
        'defendant_score': defendant_score,
        'dispositions': dispositions[:10],  # Limit to 10
        'text_length': len(opinion_text)
    }

def analyze_sample_cases(base_path, sample_size=100):
    """Analyze sample cases to understand decision patterns"""
    
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
    
    print(f"Analyzing {len(case_files)} cases for decision patterns...\n")
    
    results = []
    affirmed_count = 0
    reversed_count = 0
    remanded_count = 0
    dismissed_count = 0
    
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
            
            # Analyze decision
            analysis = extract_decision(text, data)
            
            if analysis['affirmed']:
                affirmed_count += 1
            if analysis['reversed']:
                reversed_count += 1
            if analysis['remanded']:
                remanded_count += 1
            if analysis['dismissed']:
                dismissed_count += 1
            
            # Store interesting cases for examples
            if i <= 20 or analysis['dispositions']:  # Keep first 20 and any with dispositions
                results.append({
                    'case_id': data.get('id'),
                    'case_name': data.get('name_abbreviation', 'N/A')[:100],
                    'decision_date': data.get('decision_date', 'N/A'),
                    'analysis': analysis,
                    'text_preview': text[:500]
                })
                
        except Exception as e:
            continue
    
    return results, affirmed_count, reversed_count, remanded_count, dismissed_count

def main():
    base_path = '/Users/vs/product/case-law'
    
    results, affirmed, reversed, remanded, dismissed = analyze_sample_cases(base_path, 200)
    
    print("="*80)
    print("DECISION ANALYSIS - DISPOSITION PATTERNS")
    print("="*80)
    
    print(f"\nDisposition Keyword Frequencies (in {len(results)} cases):")
    print(f"  Affirmed: {affirmed}")
    print(f"  Reversed: {reversed}")
    print(f"  Remanded: {remanded}")
    print(f"  Dismissed: {dismissed}")
    
    print("\n" + "="*80)
    print("SAMPLE CASES WITH ANALYSIS")
    print("="*80)
    
    for i, result in enumerate(results[:15], 1):
        print(f"\n{'-'*80}")
        print(f"Case {i}: {result['case_name']}")
        print(f"ID: {result['case_id']} | Date: {result['decision_date']}")
        print(f"\nAnalysis:")
        print(f"  Affirmed: {result['analysis']['affirmed']}")
        print(f"  Reversed: {result['analysis']['reversed']}")
        print(f"  Remanded: {result['analysis']['remanded']}")
        print(f"  Dismissed: {result['analysis']['dismissed']}")
        print(f"  Plaintiff indicators: {result['analysis']['plaintiff_score']}")
        print(f"  Defendant indicators: {result['analysis']['defendant_score']}")
        if result['analysis']['dispositions']:
            print(f"  Disposition terms found: {', '.join(result['analysis']['dispositions'][:5])}")
        
        print(f"\nOpinion preview:")
        print(f"  {result['text_preview'][:300]}...")
    
    print("\n" + "="*80)
    print("COMMON DISPOSITION PATTERNS")
    print("="*80)
    
    all_dispositions = []
    for r in results:
        all_dispositions.extend(r['analysis']['dispositions'])
    
    disposition_counts = Counter(all_dispositions)
    print("\nMost common disposition terms:")
    for term, count in disposition_counts.most_common(20):
        print(f"  {term:30s}: {count:3d}")

if __name__ == '__main__':
    main()

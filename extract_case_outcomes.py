#!/usr/bin/env python3
"""
Extract case outcomes from majority opinions to determine if decision favors
plaintiff or defendant.
"""
import json
import os
import re
from collections import Counter

def extract_outcome(opinion_text, case_name=''):
    """
    Extract outcome from majority opinion text.
    
    Returns dict with:
    - outcome: 'plaintiff', 'defendant', 'mixed', 'unclear'
    - confidence: 'high', 'medium', 'low'
    - disposition: the key disposition words found
    - reasoning: explanation of classification
    """
    
    text_lower = opinion_text.lower()
    last_section = text_lower[-1500:]  # Focus on ending where dispositions typically appear
    
    # Key disposition patterns
    disposition_keywords = {
        'affirmed': re.search(r'\baffirm(?:ed)?\b', last_section),
        'reversed': re.search(r'\brevers(?:ed)?\b', last_section),
        'remanded': re.search(r'\bremand(?:ed)?\b', last_section),
        'dismissed': re.search(r'\bdismiss(?:ed)?\b', last_section),
        'vacated': re.search(r'\bvacat(?:ed)?\b', last_section),
        'granted': re.search(r'\bgrant(?:ed)?\b', last_section),
        'denied': re.search(r'\bdeni(?:ed)?\b', last_section),
    }
    
    # Specific outcome patterns
    outcome_patterns = {
        'plaintiff_favor': [
            r'\bjudgment (?:is )?(?:for|in favor of) (?:the )?(?:appellant|plaintiff)',
            r'\b(?:appellant|plaintiff)(?:\s+\w+){0,3}\s+(?:entitled to|prevails?)',
            r'\b(?:grant|granting)(?:\s+\w+){0,3}\s+(?:for|to) (?:the )?(?:appellant|plaintiff)',
            r'\brevers(?:ed|ing)\b.*\bfor\b.*\b(?:appellant|plaintiff)',
            r'\b(?:appellant|plaintiff)\b.*\bwins?\b',
        ],
        'defendant_favor': [
            r'\bjudgment (?:is )?(?:for|in favor of) (?:the )?(?:appellee|defendant)',
            r'\b(?:appellee|defendant)(?:\s+\w+){0,3}\s+(?:entitled to|prevails?)',
            r'\baffirm(?:ed|ing)?\b(?!.*revers)',  # Affirmed (when not followed by reversed)
            r'\bdismiss(?:ed|ing)?\b',
            r'\b(?:appellee|defendant)\b.*\bwins?\b',
            r'\bdenied\b.*\brelief',
        ],
    }
    
    # Count pattern matches
    plaintiff_matches = []
    defendant_matches = []
    
    for pattern in outcome_patterns['plaintiff_favor']:
        matches = re.findall(pattern, last_section)
        plaintiff_matches.extend(matches)
    
    for pattern in outcome_patterns['defendant_favor']:
        matches = re.findall(pattern, last_section)
        defendant_matches.extend(matches)
    
    # Determine outcome
    plaintiff_score = len(plaintiff_matches)
    defendant_score = len(defendant_matches)
    
    # Special logic for appellate cases
    # "Affirmed" generally means lower court decision upheld (often favoring defendant)
    # "Reversed" generally means lower court overturned (often favoring plaintiff/appellant)
    if disposition_keywords['affirmed'] and not disposition_keywords['reversed']:
        defendant_score += 2  # Strong signal for defendant
    
    if disposition_keywords['reversed'] and not disposition_keywords['affirmed']:
        plaintiff_score += 2  # Strong signal for plaintiff/appellant
    
    if disposition_keywords['dismissed']:
        defendant_score += 1
    
    # Determine outcome and confidence
    if plaintiff_score > defendant_score:
        if plaintiff_score >= 2:
            outcome = 'plaintiff'
            confidence = 'high' if plaintiff_score >= 3 else 'medium'
        else:
            outcome = 'plaintiff'
            confidence = 'low'
    elif defendant_score > plaintiff_score:
        if defendant_score >= 2:
            outcome = 'defendant'
            confidence = 'high' if defendant_score >= 3 else 'medium'
        else:
            outcome = 'defendant'
            confidence = 'low'
    elif plaintiff_score == defendant_score and plaintiff_score > 0:
        outcome = 'mixed'
        confidence = 'medium'
    else:
        outcome = 'unclear'
        confidence = 'low'
    
    # Build disposition summary
    found_dispositions = [k for k, v in disposition_keywords.items() if v]
    
    # Build reasoning
    reasoning_parts = []
    if found_dispositions:
        reasoning_parts.append(f"Dispositions: {', '.join(found_dispositions)}")
    if plaintiff_score > 0:
        reasoning_parts.append(f"Plaintiff indicators: {plaintiff_score}")
    if defendant_score > 0:
        reasoning_parts.append(f"Defendant indicators: {defendant_score}")
    
    reasoning = "; ".join(reasoning_parts) if reasoning_parts else "No clear indicators found"
    
    return {
        'outcome': outcome,
        'confidence': confidence,
        'dispositions': found_dispositions,
        'reasoning': reasoning,
        'plaintiff_score': plaintiff_score,
        'defendant_score': defendant_score,
    }

def analyze_cases(base_path, sample_size=100):
    """Analyze sample cases and extract outcomes"""
    
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
    
    print(f"Analyzing outcomes for {len(case_files)} cases...\n")
    
    results = []
    outcome_counts = Counter()
    confidence_counts = Counter()
    
    for file_path in case_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Get majority opinion
            opinions = data.get('opinions', [])
            if not opinions:
                opinions = data.get('casebody', {}).get('opinions', [])
            
            majority_opinion = None
            for opinion in opinions:
                if opinion.get('type') == 'majority':
                    majority_opinion = opinion
                    break
            
            if not majority_opinion or not majority_opinion.get('text'):
                continue
            
            # Extract outcome
            outcome_data = extract_outcome(
                majority_opinion['text'],
                data.get('name_abbreviation', '')
            )
            
            outcome_counts[outcome_data['outcome']] += 1
            confidence_counts[outcome_data['confidence']] += 1
            
            results.append({
                'case_id': data.get('id'),
                'case_name': data.get('name_abbreviation', 'N/A')[:80],
                'decision_date': data.get('decision_date', 'N/A'),
                'outcome': outcome_data['outcome'],
                'confidence': outcome_data['confidence'],
                'dispositions': outcome_data['dispositions'],
                'reasoning': outcome_data['reasoning'],
            })
            
        except Exception as e:
            continue
    
    return results, outcome_counts, confidence_counts

def main():
    base_path = '/Users/vs/product/case-law'
    
    results, outcome_counts, confidence_counts = analyze_cases(base_path, 150)
    
    print("="*80)
    print("CASE OUTCOME EXTRACTION ANALYSIS")
    print("="*80)
    
    print(f"\nTotal cases analyzed: {len(results)}")
    
    print("\n" + "-"*80)
    print("OUTCOME DISTRIBUTION:")
    print("-"*80)
    for outcome, count in outcome_counts.most_common():
        percentage = (count / len(results)) * 100
        print(f"{outcome:15s}: {count:4d} ({percentage:5.1f}%)")
    
    print("\n" + "-"*80)
    print("CONFIDENCE LEVELS:")
    print("-"*80)
    for confidence, count in confidence_counts.most_common():
        percentage = (count / len(results)) * 100
        print(f"{confidence:15s}: {count:4d} ({percentage:5.1f}%)")
    
    print("\n" + "="*80)
    print("SAMPLE CASES WITH EXTRACTED OUTCOMES")
    print("="*80)
    
    # Show examples by outcome type
    for outcome_type in ['plaintiff', 'defendant', 'mixed', 'unclear']:
        examples = [r for r in results if r['outcome'] == outcome_type][:3]
        if examples:
            print(f"\n{outcome_type.upper()} OUTCOMES:")
            print("-"*80)
            for example in examples:
                print(f"\nCase: {example['case_name']}")
                print(f"  ID: {example['case_id']} | Date: {example['decision_date']}")
                print(f"  Outcome: {example['outcome']} (confidence: {example['confidence']})")
                print(f"  Dispositions: {', '.join(example['dispositions']) if example['dispositions'] else 'None detected'}")
                print(f"  Reasoning: {example['reasoning']}")
    
    # Save results to CSV
    print("\n" + "="*80)
    print("Saving results to outcomes_sample.csv...")
    print("="*80)
    
    import csv
    with open('outcomes_sample.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['case_id', 'case_name', 'decision_date', 'outcome', 'confidence', 'dispositions', 'reasoning']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            result['dispositions'] = '; '.join(result['dispositions'])
            writer.writerow(result)
    
    print(f"Saved {len(results)} case outcomes to outcomes_sample.csv")

if __name__ == '__main__':
    main()

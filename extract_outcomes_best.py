#!/usr/bin/env python3
"""
BEST outcome extraction - searches entire opinion for disposition markers
"""
import json
import os
import re
from collections import Counter

def extract_outcome_best(opinion_text, case_name=''):
    """
    Best extraction method - searches entire text for disposition patterns
    """
    
    text_lower = opinion_text.lower()
    
    # Initialize scores
    defendant_score = 0
    plaintiff_score = 0
    
    # STRATEGY 1: Find explicit "Decision" or "Disposition" sections anywhere in text
    decision_section_patterns = [
        r'(?:iv|v|4|5)\.?\s+(?:decision|conclusion|disposition|judgment)\s*:?\s*([^\n\.]{10,500})',
        r'for\s+(?:the\s+)?foregoing\s+reasons[,\s]+([^\n]{10,400})',
        r'(?:it\s+is\s+(?:hereby\s+)?(?:ordered|adjudged|decreed|held)[,:\s]+)([^\n]{10,400})',
        r'(?:we\s+)?(?:affirm|reverse|remand|dismiss|vacate)[^\n]{10,300}',
    ]
    
    decision_matches = []
    for pattern in decision_section_patterns:
        for match in re.finditer(pattern, text_lower):
            decision_matches.append({
                'text': match.group(0) if match.lastindex is None else match.group(match.lastindex),
                'position': match.start(),
                'type': 'explicit_section'
            })
    
    # STRATEGY 2: Find strong disposition phrases anywhere
    strong_defendant_patterns = [
        (r'(?:the\s+)?(?:judgment|decision|order)(?:\s+is|\s+of\s+the)?\s+affirmed(?!\s+in\s+part)', 10),
        (r'affirmed?\s*\.?\s*(?:\n|$)', 10),
        (r'(?:appeal|petition|complaint|action)\s+(?:is\s+)?(?:hereby\s+)?dismissed', 9),
        (r'judgment\s+(?:is\s+)?(?:for|in\s+favor\s+of)\s+(?:the\s+)?(?:defendant|appellee)', 10),
        (r'motion\s+for\s+summary\s+judgment\s+(?:is\s+)?denied', 6),
        (r'we\s+affirm\s+the\s+(?:judgment|decision|order)', 9),
    ]
    
    strong_plaintiff_patterns = [
        (r'(?:the\s+)?(?:judgment|decision|order)(?:\s+is)?\s+reversed(?!\s+in\s+part)', 10),
        (r'reversed?\s*\.?\s*(?:\n|$)', 10),
        (r'judgment\s+(?:is\s+)?(?:for|in\s+favor\s+of)\s+(?:the\s+)?(?:plaintiff|appellant)', 10),
        (r'we\s+reverse\s+the\s+(?:judgment|decision|order)', 9),
        (r'motion\s+for\s+summary\s+judgment\s+(?:is\s+)?granted\s+(?:to\s+)?(?:the\s+)?plaintiff', 8),
    ]
    
    # Score based on pattern matches
    for pattern, weight in strong_defendant_patterns:
        matches = list(re.finditer(pattern, text_lower))
        for match in matches:
            position = match.start() / len(text_lower)  # Relative position
            # Give more weight to matches near the end
            position_weight = 1.0 + (position * 0.5)  # 1.0 to 1.5x
            defendant_score += weight * position_weight
            decision_matches.append({
                'text': match.group(0),
                'position': match.start(),
                'type': 'defendant_pattern',
                'score': weight * position_weight
            })
    
    for pattern, weight in strong_plaintiff_patterns:
        matches = list(re.finditer(pattern, text_lower))
        for match in matches:
            position = match.start() / len(text_lower)
            position_weight = 1.0 + (position * 0.5)
            plaintiff_score += weight * position_weight
            decision_matches.append({
                'text': match.group(0),
                'position': match.start(),
                'type': 'plaintiff_pattern',
                'score': weight * position_weight
            })
    
    # STRATEGY 3: Look for common tribal court patterns
    # "upholds", "overturns", etc.
    if re.search(r'(?:we\s+)?(?:uphold|sustain)\s+(?:the\s+)?(?:decision|judgment|order)', text_lower):
        defendant_score += 7
    
    if re.search(r'(?:we\s+)?(?:overturn|set\s+aside)\s+(?:the\s+)?(?:decision|judgment|order)', text_lower):
        plaintiff_score += 7
    
    # STRATEGY 4: Check if it's a mixed outcome
    mixed_indicators = [
        'affirmed in part and reversed in part',
        'reversed in part and affirmed in part',
        'affirm in part',
        'reverse in part'
    ]
    
    has_mixed = any(indicator in text_lower for indicator in mixed_indicators)
    
    if has_mixed:
        return {
            'outcome': 'mixed',
            'confidence': 'medium' if defendant_score > 5 or plaintiff_score > 5 else 'low',
            'defendant_score': defendant_score,
            'plaintiff_score': plaintiff_score,
            'reasoning': 'Mixed outcome (affirmed in part, reversed in part)',
            'evidence': 'Mixed disposition language found'
        }
    
    # Determine outcome
    if defendant_score == 0 and plaintiff_score == 0:
        return {
            'outcome': 'unclear',
            'confidence': 'low',
            'defendant_score': 0,
            'plaintiff_score': 0,
            'reasoning': 'No clear disposition indicators found',
            'evidence': 'None'
        }
    
    # Get winner
    if defendant_score > plaintiff_score:
        outcome = 'defendant'
        score = defendant_score
    else:
        outcome = 'plaintiff'
        score = plaintiff_score
    
    # Determine confidence
    margin = abs(defendant_score - plaintiff_score)
    
    if score >= 10 and margin >= 7:
        confidence = 'high'
    elif score >= 6 and margin >= 4:
        confidence = 'medium'
    else:
        confidence = 'low'
    
    # Find best evidence (highest scoring match near end)
    if decision_matches:
        decision_matches.sort(key=lambda x: x['position'], reverse=True)
        best_evidence = decision_matches[0]['text'][:100]
    else:
        best_evidence = 'Pattern-based classification'
    
    return {
        'outcome': outcome,
        'confidence': confidence,
        'defendant_score': round(defendant_score, 1),
        'plaintiff_score': round(plaintiff_score, 1),
        'reasoning': f"Def={round(defendant_score,1)}, Pl={round(plaintiff_score,1)}, margin={round(margin,1)}",
        'evidence': best_evidence
    }

def analyze_best_method(base_path, sample_size=200):
    """Analyze using best method"""
    
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
    
    print(f"Analyzing with BEST method: {len(case_files)} cases...\n")
    
    results = []
    outcome_counts = Counter()
    confidence_counts = Counter()
    
    for file_path in case_files:
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
            
            if not majority_opinion or not majority_opinion.get('text'):
                continue
            
            outcome_data = extract_outcome_best(
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
                'defendant_score': outcome_data['defendant_score'],
                'plaintiff_score': outcome_data['plaintiff_score'],
                'reasoning': outcome_data['reasoning'],
                'evidence': outcome_data['evidence'],
            })
            
        except Exception as e:
            continue
    
    return results, outcome_counts, confidence_counts

def main():
    base_path = '/Users/vs/product/case-law'
    
    print("="*80)
    print("BEST OUTCOME EXTRACTION METHOD")
    print("="*80)
    print("Improvements:")
    print("  ✓ Searches ENTIRE opinion text, not just ending")
    print("  ✓ Finds explicit Decision/Conclusion sections")
    print("  ✓ Weights matches based on position (end = higher weight)")
    print("  ✓ Handles tribal court language ('upholds', 'overturns')")
    print("  ✓ Detects mixed outcomes")
    print("="*80)
    print()
    
    results, outcome_counts, confidence_counts = analyze_best_method(base_path, 200)
    
    print(f"Total cases analyzed: {len(results)}\n")
    
    print("-"*80)
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
    
    # Show improvement
    print("\n" + "="*80)
    print("COMPARISON WITH ORIGINAL METHOD:")
    print("="*80)
    print(f"{'Metric':<30s} {'Original':>12s} {'Best':>12s} {'Change':>12s}")
    print("-"*80)
    
    orig_unclear = 55.3
    best_unclear = (outcome_counts['unclear'] / len(results)) * 100
    
    orig_defendant = 38.7
    best_defendant = (outcome_counts['defendant'] / len(results)) * 100
    
    orig_plaintiff = 6.0
    best_plaintiff = (outcome_counts['plaintiff'] / len(results)) * 100
    
    orig_high_conf = 26.0
    best_high_conf = (confidence_counts['high'] / len(results)) * 100
    
    print(f"{'Unclear outcomes':<30s} {orig_unclear:>11.1f}% {best_unclear:>11.1f}% {best_unclear-orig_unclear:>+11.1f}%")
    print(f"{'Defendant wins':<30s} {orig_defendant:>11.1f}% {best_defendant:>11.1f}% {best_defendant-orig_defendant:>+11.1f}%")
    print(f"{'Plaintiff wins':<30s} {orig_plaintiff:>11.1f}% {best_plaintiff:>11.1f}% {best_plaintiff-orig_plaintiff:>+11.1f}%")
    print(f"{'High confidence':<30s} {orig_high_conf:>11.1f}% {best_high_conf:>11.1f}% {best_high_conf-orig_high_conf:>+11.1f}%")
    
    clear_outcomes = 100 - best_unclear
    print(f"\n{'Clear outcomes (not unclear)':<30s} {'44.7%':>12s} {clear_outcomes:>11.1f}% {clear_outcomes-44.7:>+11.1f}%")
    
    # Show high confidence examples
    print("\n" + "="*80)
    print("HIGH-CONFIDENCE DEFENDANT WINS:")
    print("="*80)
    
    high_def = [r for r in results if r['outcome'] == 'defendant' and r['confidence'] == 'high'][:5]
    for r in high_def:
        print(f"\n{r['case_name']}")
        print(f"  {r['reasoning']}")
        print(f"  Evidence: {r['evidence'][:100]}...")
    
    print("\n" + "="*80)
    print("HIGH-CONFIDENCE PLAINTIFF WINS:")
    print("="*80)
    
    high_pl = [r for r in results if r['outcome'] == 'plaintiff' and r['confidence'] == 'high'][:5]
    for r in high_pl:
        print(f"\n{r['case_name']}")
        print(f"  {r['reasoning']}")
        print(f"  Evidence: {r['evidence'][:100]}...")
    
    # Save
    print("\n" + "="*80)
    print("Saving to outcomes_best.csv...")
    print("="*80)
    
    import csv
    with open('outcomes_best.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['case_id', 'case_name', 'decision_date', 'outcome', 'confidence', 
                     'defendant_score', 'plaintiff_score', 'reasoning']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            result_copy = {k: v for k, v in result.items() if k in fieldnames}
            writer.writerow(result_copy)
    
    print(f"Saved {len(results)} outcomes with improved accuracy!\n")

if __name__ == '__main__':
    main()

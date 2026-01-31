#!/usr/bin/env python3
"""
Final improved outcome extraction - finds the actual disposition before citations/footnotes
"""
import json
import os
import re
from collections import Counter

def find_disposition_section(text):
    """
    Find the actual disposition text, excluding citations and footnotes
    """
    # Common patterns that mark the END of substantive opinion (before citations/notes)
    end_markers = [
        r'\n\s*\.\s+[A-Z]',  # Footnote markers (. Footnote)
        r'\n\s*\d+\.\s+[A-Z]',  # Numbered footnotes
        r'(?:see|cf\.|id\.|supra)\s+[\w\s,]+\d+\s+[\w\.]+\s+\d+',  # Legal citations
        r'\d+\s+[A-Z]\.[\w\s]+\d+',  # Case citations like "123 F.3d 456"
    ]
    
    # Find where citations/footnotes start (work backwards from end)
    lines = text.split('\n')
    
    # Find last substantive line (before citations dominate)
    substantive_end = len(text)
    
    # Look for concentration of citations in last portion
    last_1000 = text[-1000:]
    citation_density = len(re.findall(r'\d+\s+[A-Z]\.[\w\s\.]+\d+', last_1000))
    
    if citation_density > 5:  # Heavy citations at end
        # Find where substantive content likely ends
        # Look for last sentence before citation-heavy section
        matches = list(re.finditer(r'[.!]\s+[A-Z]', text))
        if matches:
            # Find last substantive sentence
            for match in reversed(matches):
                pos = match.start()
                # Check if rest is mostly citations
                remaining = text[pos:]
                if len(remaining) < 2000:  # Check last 2000 chars
                    remaining_citations = len(re.findall(r'\d+\s+[A-Z]\.[\w\s\.]+\d+', remaining))
                    remaining_words = len(remaining.split())
                    if remaining_words > 20 and remaining_citations / remaining_words < 0.1:
                        # This looks like substantive content
                        substantive_end = pos + 500  # Include a bit more
                        break
    
    return text[:substantive_end]

def extract_outcome_final(opinion_text, case_name=''):
    """
    Final improved extraction focusing on actual disposition language
    """
    
    # First, find the substantive portion (before heavy citations)
    substantive_text = find_disposition_section(opinion_text)
    text_lower = substantive_text.lower()
    
    # Focus on different sections
    last_300 = text_lower[-300:]
    last_800 = text_lower[-800:]
    last_2000 = text_lower[-2000:]
    
    # Initialize scores
    defendant_score = 0
    plaintiff_score = 0
    procedural_score = 0
    mixed_score = 0
    
    # STRATEGY 1: Look for explicit "Decision" or "Conclusion" sections
    decision_section_patterns = [
        r'(?:iv\.?|v\.?)\s+(?:decision|conclusion|disposition)\s*:?\s*([^\n]{10,300})',
        r'(?:for\s+(?:the\s+)?(?:foregoing|these)\s+reasons?[,\s]+)([^\n]{10,300})',
        r'(?:it\s+is\s+(?:hereby\s+)?(?:ordered|adjudged|decreed)[,\s]+)([^\n]{10,300})',
    ]
    
    decision_text = ''
    for pattern in decision_section_patterns:
        match = re.search(pattern, last_2000)
        if match:
            decision_text = match.group(1).lower()
            break
    
    if not decision_text:
        # No explicit section, use last 300 chars
        decision_text = last_300
    
    # STRATEGY 2: Look for very specific outcome phrases
    
    # Defendant wins (high confidence)
    if re.search(r'(?:judgment|decision|order)\s+(?:is\s+)?affirmed(?!\s+in\s+part)', decision_text):
        defendant_score += 10
    elif re.search(r'affirmed?\s*\.?\s*$', decision_text):
        defendant_score += 10
    
    if re.search(r'(?:appeal|petition|complaint|action)\s+(?:is\s+)?(?:hereby\s+)?dismissed', decision_text):
        defendant_score += 8
    
    if re.search(r'motion\s+(?:for\s+summary\s+judgment\s+)?(?:is\s+)?denied', decision_text):
        defendant_score += 5
        
    if re.search(r'judgment\s+for\s+(?:the\s+)?defendant', decision_text):
        defendant_score += 10
        
    # Plaintiff wins (high confidence)
    if re.search(r'(?:judgment|decision|order)\s+(?:is\s+)?reversed(?!\s+in\s+part)', decision_text):
        plaintiff_score += 10
    elif re.search(r'reversed?\s*\.?\s*$', decision_text):
        plaintiff_score += 10
    
    if re.search(r'judgment\s+for\s+(?:the\s+)?plaintiff', decision_text):
        plaintiff_score += 10
    
    if re.search(r'motion\s+(?:for\s+summary\s+judgment\s+)?(?:is\s+)?granted\s+to\s+(?:the\s+)?plaintiff', decision_text):
        plaintiff_score += 8
    
    # Look for "overturns" "upholds" etc.
    if re.search(r'(?:we\s+)?(?:uphold|sustain)\s+(?:the\s+)?(?:decision|judgment)', decision_text):
        defendant_score += 6
    
    if re.search(r'(?:we\s+)?(?:overturn|reverse)\s+(?:the\s+)?(?:decision|judgment)', decision_text):
        plaintiff_score += 6
    
    # Mixed outcomes
    if re.search(r'affirmed\s+in\s+part\s+and\s+reversed\s+in\s+part', decision_text):
        mixed_score += 10
    elif re.search(r'reversed\s+in\s+part\s+and\s+affirmed\s+in\s+part', decision_text):
        mixed_score += 10
    
    # Procedural (remanded without clear winner)
    if re.search(r'remanded\s+for\s+(?:further\s+)?proceedings', decision_text):
        procedural_score += 5
    
    if re.search(r'vacated\s+and\s+remanded', decision_text):
        procedural_score += 5
    
    # STRATEGY 3: Check broader context if no clear winner yet
    if max(defendant_score, plaintiff_score, mixed_score, procedural_score) < 5:
        # Broaden search to last 800 chars
        if 'affirmed' in last_800 and 'reversed' not in last_800:
            defendant_score += 4
        if 'reversed' in last_800 and 'affirmed' not in last_800:
            plaintiff_score += 4
        if 'dismissed' in last_800:
            defendant_score += 3
        if 'remanded' in last_800:
            procedural_score += 2
    
    # Determine outcome
    scores = {
        'defendant': defendant_score,
        'plaintiff': plaintiff_score,
        'mixed': mixed_score,
        'procedural': procedural_score
    }
    
    max_score = max(scores.values())
    
    if max_score == 0:
        return {
            'outcome': 'unclear',
            'confidence': 'low',
            'scores': scores,
            'reasoning': 'No clear disposition found',
            'decision_text': decision_text[:100] if decision_text else 'None'
        }
    
    # Get winner
    outcome = max(scores.items(), key=lambda x: x[1])[0]
    
    # Convert procedural to unclear if score is too low
    if outcome == 'procedural' and procedural_score < 5:
        outcome = 'unclear'
    
    # Determine confidence
    second_highest = sorted(scores.values(), reverse=True)[1]
    margin = max_score - second_highest
    
    if max_score >= 8 and margin >= 5:
        confidence = 'high'
    elif max_score >= 5 and margin >= 3:
        confidence = 'medium'
    else:
        confidence = 'low'
    
    return {
        'outcome': outcome,
        'confidence': confidence,
        'scores': scores,
        'reasoning': f"Max score: {max_score}, Margin: {margin}",
        'decision_text': decision_text[:150] if decision_text else 'None'
    }

def analyze_with_final_method(base_path, sample_size=200):
    """Analyze using final improved method"""
    
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
    
    print(f"Analyzing with final improved method: {len(case_files)} cases...\n")
    
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
            
            outcome_data = extract_outcome_final(
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
                'scores': outcome_data['scores'],
                'reasoning': outcome_data['reasoning'],
                'decision_text': outcome_data['decision_text'],
            })
            
        except Exception as e:
            continue
    
    return results, outcome_counts, confidence_counts

def main():
    base_path = '/Users/vs/product/case-law'
    
    print("="*80)
    print("FINAL IMPROVED OUTCOME EXTRACTION")
    print("="*80)
    print("Improvements:")
    print("  - Filters out citations and footnotes")
    print("  - Finds explicit 'Decision' sections")
    print("  - Uses weighted scoring system")
    print("  - Focuses on actual disposition language")
    print("="*80)
    print()
    
    results, outcome_counts, confidence_counts = analyze_with_final_method(base_path, 200)
    
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
    print("COMPARISON WITH ORIGINAL:")
    print("="*80)
    print(f"{'Metric':<25s} {'Original':>15s} {'Final':>15s} {'Change':>15s}")
    print("-"*80)
    
    orig_unclear = 55.3
    final_unclear = (outcome_counts['unclear'] / len(results)) * 100
    
    orig_defendant = 38.7
    final_defendant = (outcome_counts['defendant'] / len(results)) * 100
    
    orig_plaintiff = 6.0
    final_plaintiff = (outcome_counts['plaintiff'] / len(results)) * 100
    
    orig_high_conf = 26.0
    final_high_conf = (confidence_counts['high'] / len(results)) * 100
    
    print(f"{'Unclear rate':<25s} {orig_unclear:>14.1f}% {final_unclear:>14.1f}% {final_unclear-orig_unclear:>+14.1f}%")
    print(f"{'Defendant wins':<25s} {orig_defendant:>14.1f}% {final_defendant:>14.1f}% {final_defendant-orig_defendant:>+14.1f}%")
    print(f"{'Plaintiff wins':<25s} {orig_plaintiff:>14.1f}% {final_plaintiff:>14.1f}% {final_plaintiff-orig_plaintiff:>+14.1f}%")
    print(f"{'High confidence':<25s} {orig_high_conf:>14.1f}% {final_high_conf:>14.1f}% {final_high_conf-orig_high_conf:>+14.1f}%")
    
    # Show examples
    print("\n" + "="*80)
    print("SAMPLE HIGH-CONFIDENCE CASES:")
    print("="*80)
    
    high_conf_cases = [r for r in results if r['confidence'] == 'high'][:10]
    for example in high_conf_cases:
        print(f"\nCase: {example['case_name']}")
        print(f"  Outcome: {example['outcome']} (HIGH confidence)")
        print(f"  Scores: " + ", ".join([f"{k}={v}" for k, v in example['scores'].items() if v > 0]))
        print(f"  Decision text: {example['decision_text'][:120]}...")
    
    # Save results
    print("\n" + "="*80)
    print("Saving to outcomes_final.csv...")
    print("="*80)
    
    import csv
    with open('outcomes_final.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['case_id', 'case_name', 'decision_date', 'outcome', 'confidence', 'reasoning']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            result_copy = {k: v for k, v in result.items() if k in fieldnames}
            writer.writerow(result_copy)
    
    print(f"Saved {len(results)} outcomes\n")

if __name__ == '__main__':
    main()

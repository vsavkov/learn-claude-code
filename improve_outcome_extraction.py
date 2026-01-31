#!/usr/bin/env python3
"""
Improved outcome extraction with enhanced pattern matching and context analysis.
"""
import json
import os
import re
from collections import Counter

def extract_outcome_improved(opinion_text, case_name=''):
    """
    Improved outcome extraction using multiple strategies.
    """
    
    text_lower = opinion_text.lower()
    
    # Strategy 1: Look at multiple sections
    last_500 = text_lower[-500:]      # Very end - often has final disposition
    last_1500 = text_lower[-1500:]    # Broader ending section
    last_3000 = text_lower[-3000:]    # Even broader for context
    
    # Strategy 2: More comprehensive disposition patterns
    
    # CLEAR DEFENDANT WINS
    defendant_patterns = [
        r'(?:the\s+)?(?:judgment|decision|order)(?:\s+is)?\s+affirmed(?!\s+in\s+part)',
        r'affirmed?\s*\.?\s*$',  # Affirmed at very end
        r'(?:appeal|petition)\s+is\s+(?:hereby\s+)?dismissed',
        r'(?:we\s+)?dismiss\s+(?:the\s+)?(?:appeal|petition|complaint|action)',
        r'judgment\s+(?:is\s+)?(?:for|in\s+favor\s+of)\s+(?:the\s+)?(?:defendant|appellee)',
        r'(?:the\s+)?defendant\s+(?:is\s+)?entitled\s+to\s+judgment',
        r'(?:we\s+)?affirm\s+the\s+(?:judgment|decision|order|dismissal)',
        r'motion\s+to\s+dismiss\s+(?:is\s+)?granted',
        r'summary\s+judgment\s+(?:is\s+)?granted\s+(?:to|for)\s+(?:the\s+)?defendant',
        r'(?:the\s+)?defendant\s+prevails?',
        r'affirmed\s+and\s+remanded',  # Usually still a defense win
    ]
    
    # CLEAR PLAINTIFF WINS
    plaintiff_patterns = [
        r'(?:the\s+)?(?:judgment|decision|order)(?:\s+is)?\s+reversed(?!\s+in\s+part)',
        r'reversed?\s*\.?\s*$',  # Reversed at very end
        r'reversed\s+and\s+remanded\s+for\s+(?:trial|proceedings|entry\s+of\s+judgment)',
        r'judgment\s+(?:is\s+)?(?:for|in\s+favor\s+of)\s+(?:the\s+)?(?:plaintiff|appellant)',
        r'(?:the\s+)?plaintiff\s+(?:is\s+)?entitled\s+to\s+judgment',
        r'(?:we\s+)?reverse\s+(?:the\s+)?(?:judgment|decision|order|dismissal)',
        r'motion\s+for\s+summary\s+judgment\s+(?:is\s+)?denied',
        r'(?:the\s+)?plaintiff\s+prevails?',
        r'(?:we\s+)?grant\s+(?:the\s+)?(?:plaintiff|appellant)',
        r'verdict\s+for\s+(?:the\s+)?plaintiff',
    ]
    
    # MIXED OUTCOMES
    mixed_patterns = [
        r'affirmed\s+in\s+part\s+and\s+reversed\s+in\s+part',
        r'reversed\s+in\s+part\s+and\s+affirmed\s+in\s+part',
        r'partially\s+(?:affirmed|reversed)',
        r'affirmed\s+in\s+part.*?reversed\s+in\s+part',
    ]
    
    # PROCEDURAL (neither side wins clearly)
    procedural_patterns = [
        r'remanded\s+for\s+(?:further\s+)?proceedings',
        r'vacated\s+and\s+remanded(?!\s+for\s+entry)',
        r'(?:case|action)\s+(?:is\s+)?remanded',
        r'remanded\s+to\s+(?:the\s+)?(?:trial\s+)?court',
    ]
    
    # Strategy 3: Score each section
    def count_matches(patterns, text):
        return sum(1 for p in patterns if re.search(p, text))
    
    # Count in last 500 chars (highest weight)
    defendant_score_500 = count_matches(defendant_patterns, last_500) * 3
    plaintiff_score_500 = count_matches(plaintiff_patterns, last_500) * 3
    mixed_score_500 = count_matches(mixed_patterns, last_500) * 3
    procedural_score_500 = count_matches(procedural_patterns, last_500) * 2
    
    # Count in last 1500 chars (medium weight)
    defendant_score_1500 = count_matches(defendant_patterns, last_1500) * 2
    plaintiff_score_1500 = count_matches(plaintiff_patterns, last_1500) * 2
    mixed_score_1500 = count_matches(mixed_patterns, last_1500) * 2
    procedural_score_1500 = count_matches(procedural_patterns, last_1500) * 1
    
    # Total scores
    defendant_score = defendant_score_500 + defendant_score_1500
    plaintiff_score = plaintiff_score_500 + plaintiff_score_1500
    mixed_score = mixed_score_500 + mixed_score_1500
    procedural_score = procedural_score_500 + procedural_score_1500
    
    # Strategy 4: Look for specific phrases that are very reliable
    very_end = text_lower[-100:].strip()
    
    if re.search(r'affirmed\s*\.?\s*$', very_end):
        defendant_score += 5
    elif re.search(r'reversed\s*\.?\s*$', very_end):
        plaintiff_score += 5
    elif re.search(r'dismissed\s*\.?\s*$', very_end):
        defendant_score += 5
    
    # Strategy 5: Check for "IT IS SO ORDERED" section (common in final disposition)
    if 'it is so ordered' in last_1500:
        # Extract the sentence before "IT IS SO ORDERED"
        match = re.search(r'([^.!?]+)\.?\s*it is so ordered', last_1500)
        if match:
            order_text = match.group(1)
            if 'affirmed' in order_text:
                defendant_score += 3
            elif 'reversed' in order_text:
                plaintiff_score += 3
            elif 'dismissed' in order_text:
                defendant_score += 3
            elif 'granted' in order_text and 'plaintiff' in order_text:
                plaintiff_score += 3
            elif 'denied' in order_text and 'plaintiff' in order_text:
                defendant_score += 3
    
    # Strategy 6: Look for conclusion/disposition sections
    conclusion_markers = [
        r'(?:conclusion|disposition|decision|judgment)\s*:?\s*([^.]{20,200})',
        r'for (?:the )?(?:foregoing|these) reasons?,\s*([^.]{20,200})',
    ]
    
    for marker in conclusion_markers:
        match = re.search(marker, last_1500)
        if match:
            conclusion_text = match.group(1).lower()
            if 'affirmed' in conclusion_text:
                defendant_score += 2
            elif 'reversed' in conclusion_text:
                plaintiff_score += 2
            elif 'dismissed' in conclusion_text:
                defendant_score += 2
    
    # Strategy 7: Determine outcome with confidence
    all_scores = {
        'defendant': defendant_score,
        'plaintiff': plaintiff_score,
        'mixed': mixed_score,
        'procedural': procedural_score
    }
    
    max_score = max(all_scores.values())
    
    if max_score == 0:
        return {
            'outcome': 'unclear',
            'confidence': 'low',
            'scores': all_scores,
            'reasoning': 'No clear disposition indicators found'
        }
    
    # Get outcome with highest score
    outcome = max(all_scores.items(), key=lambda x: x[1])[0]
    
    # Adjust procedural to unclear if it's the winner but score is low
    if outcome == 'procedural' and procedural_score < 3:
        outcome = 'unclear'
    
    # Determine confidence based on score margin
    second_highest = sorted(all_scores.values(), reverse=True)[1] if len(all_scores) > 1 else 0
    margin = max_score - second_highest
    
    if max_score >= 8 and margin >= 4:
        confidence = 'high'
    elif max_score >= 4 and margin >= 2:
        confidence = 'medium'
    else:
        confidence = 'low'
    
    # Build reasoning
    reasoning_parts = []
    for outcome_type, score in all_scores.items():
        if score > 0:
            reasoning_parts.append(f"{outcome_type}={score}")
    reasoning = "Scores: " + ", ".join(reasoning_parts)
    
    return {
        'outcome': outcome,
        'confidence': confidence,
        'scores': all_scores,
        'reasoning': reasoning
    }

def compare_methods(base_path, sample_size=150):
    """Compare old vs new extraction methods"""
    
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
    
    print(f"Comparing extraction methods on {len(case_files)} cases...\n")
    
    results = []
    new_outcome_counts = Counter()
    new_confidence_counts = Counter()
    
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
            
            # Use improved extraction
            outcome_data = extract_outcome_improved(
                majority_opinion['text'],
                data.get('name_abbreviation', '')
            )
            
            new_outcome_counts[outcome_data['outcome']] += 1
            new_confidence_counts[outcome_data['confidence']] += 1
            
            results.append({
                'case_id': data.get('id'),
                'case_name': data.get('name_abbreviation', 'N/A')[:80],
                'decision_date': data.get('decision_date', 'N/A'),
                'outcome': outcome_data['outcome'],
                'confidence': outcome_data['confidence'],
                'scores': outcome_data['scores'],
                'reasoning': outcome_data['reasoning'],
            })
            
        except Exception as e:
            continue
    
    return results, new_outcome_counts, new_confidence_counts

def main():
    base_path = '/Users/vs/product/case-law'
    
    print("="*80)
    print("IMPROVED OUTCOME EXTRACTION")
    print("="*80)
    
    results, outcome_counts, confidence_counts = compare_methods(base_path, 200)
    
    print(f"\nTotal cases analyzed: {len(results)}")
    
    print("\n" + "-"*80)
    print("NEW OUTCOME DISTRIBUTION:")
    print("-"*80)
    for outcome, count in outcome_counts.most_common():
        percentage = (count / len(results)) * 100
        print(f"{outcome:15s}: {count:4d} ({percentage:5.1f}%)")
    
    print("\n" + "-"*80)
    print("NEW CONFIDENCE LEVELS:")
    print("-"*80)
    for confidence, count in confidence_counts.most_common():
        percentage = (count / len(results)) * 100
        print(f"{confidence:15s}: {count:4d} ({percentage:5.1f}%)")
    
    # Calculate improvement
    old_unclear_pct = 55.3  # From original analysis
    new_unclear_pct = (outcome_counts['unclear'] / len(results)) * 100
    improvement = old_unclear_pct - new_unclear_pct
    
    print("\n" + "="*80)
    print("IMPROVEMENT METRICS:")
    print("="*80)
    print(f"Old unclear rate: {old_unclear_pct:.1f}%")
    print(f"New unclear rate: {new_unclear_pct:.1f}%")
    print(f"Improvement: {improvement:.1f} percentage points")
    
    # Show examples by outcome and confidence
    print("\n" + "="*80)
    print("SAMPLE CASES BY OUTCOME (showing scores):")
    print("="*80)
    
    for outcome_type in ['plaintiff', 'defendant', 'mixed', 'procedural', 'unclear']:
        examples = [r for r in results if r['outcome'] == outcome_type][:3]
        if examples:
            print(f"\n{outcome_type.upper()} OUTCOMES:")
            print("-"*80)
            for example in examples:
                print(f"\nCase: {example['case_name']}")
                print(f"  Date: {example['decision_date']}")
                print(f"  Outcome: {example['outcome']} (confidence: {example['confidence']})")
                print(f"  {example['reasoning']}")
    
    # Save improved results
    print("\n" + "="*80)
    print("Saving improved results to outcomes_improved.csv...")
    print("="*80)
    
    import csv
    with open('outcomes_improved.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['case_id', 'case_name', 'decision_date', 'outcome', 'confidence', 'reasoning']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            result_copy = result.copy()
            result_copy.pop('scores')  # Remove scores dict for CSV
            writer.writerow(result_copy)
    
    print(f"Saved {len(results)} improved outcomes to outcomes_improved.csv")

if __name__ == '__main__':
    main()

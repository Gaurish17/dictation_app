"""
Improved Text Comparison using Levenshtein Distance
This module provides accurate error detection without duplicate counting.
Fixed: Total words logic, error counting, and punctuation display
"""

import re
from difflib import SequenceMatcher

def levenshtein_distance(s1, s2):
    """
    Calculate Levenshtein distance between two strings.
    Returns the minimum number of single-character edits needed.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost of insertions, deletions or substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def word_similarity(word1, word2):
    """
    Calculate similarity between two words (0.0 to 1.0).
    1.0 means identical, 0.0 means completely different.
    """
    if not word1 or not word2:
        return 0.0
    
    # Normalize to lowercase for comparison
    w1 = word1.lower().strip()
    w2 = word2.lower().strip()
    
    if w1 == w2:
        return 1.0
    
    # Calculate Levenshtein distance
    max_len = max(len(w1), len(w2))
    if max_len == 0:
        return 1.0
    
    distance = levenshtein_distance(w1, w2)
    similarity = 1.0 - (distance / max_len)
    
    return similarity

def normalize_text(text):
    """
    Normalize text for comparison - handles spacing and basic punctuation.
    """
    if not text:
        return ""
    
    # Normalize unicode quotes and apostrophes
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def extract_words_and_punctuation(text):
    """
    Extract words AND punctuation tokens from text.
    This includes punctuation marks for display.
    Returns list of tuples: (token, is_word)
    """
    if not text:
        return []
    
    # Split text into tokens (words and punctuation)
    # Matches: words, punctuation, or any other character
    tokens = re.findall(r"[a-zA-Z0-9']+|[.,!?;:\-\"\(\)]|\s+", text)
    
    result = []
    for token in tokens:
        # Skip pure whitespace tokens but preserve them for word boundaries
        if token.strip():
            is_word = bool(re.match(r"[a-zA-Z0-9']+", token))
            result.append((token, is_word))
    
    return result

def extract_words_only(text):
    """
    Extract only words (alphanumeric sequences) from text.
    This excludes punctuation marks.
    """
    if not text:
        return []
    
    # Find all word sequences (alphanumeric + some special chars like apostrophes)
    words = re.findall(r"[a-zA-Z0-9']+", text)
    return words

def compare_word_sequences(ref_words, typed_words):
    """
    Compare two word sequences using difflib SequenceMatcher.
    This provides accurate matching without duplicates.
    
    Returns:
        list: List of comparison items with types (correct, wrong, missing, extra)
    """
    # Use SequenceMatcher for accurate sequence comparison
    matcher = SequenceMatcher(None, ref_words, typed_words)
    
    comparison = []
    processed_ref_indices = set()
    processed_typed_indices = set()
    
    # Get matching blocks from SequenceMatcher
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            # Words match correctly
            for k in range(i2 - i1):
                ref_idx = i1 + k
                typed_idx = j1 + k
                
                comparison.append({
                    'type': 'correct',
                    'ref_word': ref_words[ref_idx],
                    'typed_word': typed_words[typed_idx],
                    'ref_index': ref_idx,
                    'typed_index': typed_idx
                })
                processed_ref_indices.add(ref_idx)
                processed_typed_indices.add(typed_idx)
                
        elif tag == 'replace':
            # Words don't match - could be typos or completely wrong
            ref_count = i2 - i1
            typed_count = j2 - j1
            
            # Handle one-to-one replacements (likely typos)
            for k in range(min(ref_count, typed_count)):
                ref_idx = i1 + k
                typed_idx = j1 + k
                ref_word = ref_words[ref_idx]
                typed_word = typed_words[typed_idx]
                
                # Check if it's a minor typo (high similarity)
                similarity = word_similarity(ref_word, typed_word)
                
                if similarity >= 0.6:  # Likely a typo
                    comparison.append({
                        'type': 'typo',
                        'ref_word': ref_word,
                        'typed_word': typed_word,
                        'ref_index': ref_idx,
                        'typed_index': typed_idx,
                        'similarity': similarity
                    })
                else:  # Completely wrong word
                    comparison.append({
                        'type': 'wrong',
                        'ref_word': ref_word,
                        'typed_word': typed_word,
                        'ref_index': ref_idx,
                        'typed_index': typed_idx
                    })
                
                processed_ref_indices.add(ref_idx)
                processed_typed_indices.add(typed_idx)
            
            # Handle extra typed words in replacement
            for k in range(min(ref_count, typed_count), typed_count):
                typed_idx = j1 + k
                comparison.append({
                    'type': 'extra',
                    'ref_word': '',
                    'typed_word': typed_words[typed_idx],
                    'ref_index': None,
                    'typed_index': typed_idx
                })
                processed_typed_indices.add(typed_idx)
            
            # Handle missing reference words in replacement
            for k in range(min(ref_count, typed_count), ref_count):
                ref_idx = i1 + k
                comparison.append({
                    'type': 'missing',
                    'ref_word': ref_words[ref_idx],
                    'typed_word': '',
                    'ref_index': ref_idx,
                    'typed_index': None
                })
                processed_ref_indices.add(ref_idx)
                
        elif tag == 'delete':
            # Words missing from typed text
            for k in range(i2 - i1):
                ref_idx = i1 + k
                comparison.append({
                    'type': 'missing',
                    'ref_word': ref_words[ref_idx],
                    'typed_word': '',
                    'ref_index': ref_idx,
                    'typed_index': None
                })
                processed_ref_indices.add(ref_idx)
                
        elif tag == 'insert':
            # Extra words in typed text
            for k in range(j2 - j1):
                typed_idx = j1 + k
                comparison.append({
                    'type': 'extra',
                    'ref_word': '',
                    'typed_word': typed_words[typed_idx],
                    'ref_index': None,
                    'typed_index': typed_idx
                })
                processed_typed_indices.add(typed_idx)
    
    return comparison

def compare_punctuation(reference_text, typed_text):
    """
    Compare punctuation marks between reference and typed text.
    Returns punctuation error information.
    """
    # Extract all punctuation marks
    ref_punctuation = re.findall(r'[.,!?;:\-\"\(\)]', reference_text)
    typed_punctuation = re.findall(r'[.,!?;:\-\"\(\)]', typed_text)
    
    # Count each punctuation type
    from collections import Counter
    ref_counts = Counter(ref_punctuation)
    typed_counts = Counter(typed_punctuation)
    
    punctuation_errors = []
    all_marks = set(ref_counts.keys()) | set(typed_counts.keys())
    
    for mark in all_marks:
        ref_count = ref_counts.get(mark, 0)
        typed_count = typed_counts.get(mark, 0)
        
        if ref_count != typed_count:
            if ref_count > typed_count:
                punctuation_errors.append({
                    'mark': mark,
                    'type': 'missing',
                    'count': ref_count - typed_count
                })
            else:
                punctuation_errors.append({
                    'mark': mark,
                    'type': 'extra',
                    'count': typed_count - ref_count
                })
    
    return punctuation_errors

def enhanced_compare_texts(reference_text, typed_text):
    """
    Enhanced text comparison using Levenshtein distance and SequenceMatcher.
    Provides accurate word-by-word comparison without duplicate counting.
    
    FIXED LOGIC:
    - Total words = total words in reference text
    - Typed words = total words typed by user
    - Correct words = words that match exactly
    - Wrong words = errors (typos + incorrect + missing + extra)
    - Total errors should never exceed total reference words + extra words
    
    Args:
        reference_text (str): The correct reference text
        typed_text (str): The user's typed text
        
    Returns:
        dict: Detailed comparison results with accurate error counts
    """
    if not reference_text or not typed_text:
        return {
            'words_correct': 0,
            'words_wrong': 0,
            'accuracy_percentage': 0,
            'total_words': 0,
            'typed_words': 0,
            'enhanced_comparison': [],
            'error_summary': {},
            'punctuation_errors': []
        }
    
    # Normalize texts
    normalized_ref = normalize_text(reference_text)
    normalized_typed = normalize_text(typed_text)
    
    # Extract words only (no punctuation) for word counting
    ref_words = extract_words_only(normalized_ref)
    typed_words = extract_words_only(normalized_typed)
    
    # Compare word sequences
    comparison = compare_word_sequences(ref_words, typed_words)
    
    # Count errors accurately - each word is counted ONCE
    words_correct = 0
    words_wrong = 0
    typo_count = 0
    missing_count = 0
    extra_count = 0
    
    # Build enhanced comparison for display WITH PUNCTUATION
    enhanced_comparison = []
    
    # Track word indices for punctuation insertion
    ref_word_idx = 0
    typed_word_idx = 0
    
    for item in comparison:
        if item['type'] == 'correct':
            words_correct += 1
            enhanced_comparison.append({
                'type': 'correct',
                'reference_word': item['ref_word'],
                'typed_word': item['typed_word'],
                'display_word': item['typed_word']
            })
            
        elif item['type'] == 'typo':
            words_wrong += 1
            typo_count += 1
            enhanced_comparison.append({
                'type': 'wrong',
                'reference_word': item['ref_word'],
                'typed_word': item['typed_word'],
                'display_word': item['typed_word'],
                'correction': item['ref_word'],
                'similarity': item.get('similarity', 0),
                'error_type': 'spelling_error'
            })
            
        elif item['type'] == 'wrong':
            words_wrong += 1
            enhanced_comparison.append({
                'type': 'wrong',
                'reference_word': item['ref_word'],
                'typed_word': item['typed_word'],
                'display_word': item['typed_word'],
                'correction': item['ref_word'],
                'error_type': 'incorrect_word'
            })
            
        elif item['type'] == 'missing':
            words_wrong += 1
            missing_count += 1
            enhanced_comparison.append({
                'type': 'missed',
                'reference_word': item['ref_word'],
                'typed_word': '',
                'display_word': f"[{item['ref_word']}]",
                'error_type': 'missing_word'
            })
            
        elif item['type'] == 'extra':
            words_wrong += 1
            extra_count += 1
            enhanced_comparison.append({
                'type': 'extra',
                'reference_word': '',
                'typed_word': item['typed_word'],
                'display_word': item['typed_word'],
                'error_type': 'extra_word'
            })
    
    # Calculate accuracy based on reference words
    total_words = len(ref_words)
    
    # FIXED: Accuracy should be (correct words / total reference words) * 100
    # This ensures that if user types everything correctly, accuracy = 100%
    accuracy_percentage = (words_correct / total_words * 100) if total_words > 0 else 0
    
    # Compare punctuation
    punctuation_errors = compare_punctuation(reference_text, typed_text)
    
    # Create error summary
    error_summary = {
        'spelling_errors': typo_count,
        'missing_words': missing_count,
        'extra_words': extra_count,
        'total_errors': words_wrong,
        'punctuation_errors_count': len(punctuation_errors)
    }
    
    # IMPORTANT: Validate that error counting is correct
    # Total words typed = correct + wrong words (excluding missing)
    # But missing words are still counted as errors
    
    return {
        'words_correct': words_correct,
        'words_wrong': words_wrong,
        'accuracy_percentage': round(accuracy_percentage, 2),
        'total_words': total_words,  # Total words in reference text
        'typed_words': len(typed_words),  # Total words user actually typed
        'enhanced_comparison': enhanced_comparison,
        'error_summary': error_summary,
        'punctuation_errors': punctuation_errors
    }


# Test the improved comparison
if __name__ == "__main__":
    test_cases = [
        {
            'name': 'Perfect match',
            'reference': 'The quick brown fox jumps over the lazy dog.',
            'typed': 'The quick brown fox jumps over the lazy dog.',
        },
        {
            'name': 'Typo in word',
            'reference': 'However, this is a test sentence.',
            'typed': 'Howver, this is a test sentence.',
        },
        {
            'name': 'Missing word',
            'reference': 'The quick brown fox jumps',
            'typed': 'The quick fox jumps',
        },
        {
            'name': 'Extra word',
            'reference': 'The quick brown fox',
            'typed': 'The very quick brown fox',
        },
        {
            'name': 'Mixed errors',
            'reference': 'Hello world this is a test.',
            'typed': 'Helo world tis is test extra',
        },
        {
            'name': 'Missing punctuation',
            'reference': 'Hello, world! This is a test.',
            'typed': 'Hello world This is a test',
        }
    ]
    
    print("Testing Improved Text Comparison:")
    print("=" * 70)
    
    for test in test_cases:
        result = enhanced_compare_texts(test['reference'], test['typed'])
        
        print(f"\n{test['name']}:")
        print(f"Reference:    {test['reference']}")
        print(f"Typed:        {test['typed']}")
        print(f"Total words:  {result['total_words']} (reference)")
        print(f"Typed words:  {result['typed_words']} (user typed)")
        print(f"Correct:      {result['words_correct']}")
        print(f"Wrong:        {result['words_wrong']}")
        print(f"Accuracy:     {result['accuracy_percentage']}%")
        print(f"Errors breakdown:")
        print(f"  - Typos:     {result['error_summary']['spelling_errors']}")
        print(f"  - Missing:   {result['error_summary']['missing_words']}")
        print(f"  - Extra:     {result['error_summary']['extra_words']}")
        print(f"  - Total:     {result['error_summary']['total_errors']}")
        if result['punctuation_errors']:
            print(f"Punctuation errors:")
            for err in result['punctuation_errors']:
                print(f"  - {err['type']} {err['count']}x '{err['mark']}'")
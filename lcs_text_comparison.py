"""
Enhanced Text Comparison using Longest Common Subsequence (LCS) Strategy
This module provides improved error detection and highlighting for typing/dictation practice.
"""

import re

def longest_common_subsequence(text1, text2):
    """
    Calculate the Longest Common Subsequence (LCS) between two texts.
    Returns both the LCS length and the actual sequence for detailed comparison.
    
    Args:
        text1 (str): Reference text
        text2 (str): User typed text
        
    Returns:
        dict: Contains LCS length, sequence, and alignment information
    """
    words1 = text1.lower().split()
    words2 = text2.lower().split()
    
    m, n = len(words1), len(words2)
    
    # Create DP table for LCS calculation
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Fill the DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if words1[i-1] == words2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    # Backtrack to find the actual LCS
    lcs_sequence = []
    lcs_positions_ref = []
    lcs_positions_typed = []
    
    i, j = m, n
    while i > 0 and j > 0:
        if words1[i-1] == words2[j-1]:
            lcs_sequence.append(words1[i-1])
            lcs_positions_ref.append(i-1)
            lcs_positions_typed.append(j-1)
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1
    
    # Reverse to get correct order
    lcs_sequence.reverse()
    lcs_positions_ref.reverse()
    lcs_positions_typed.reverse()
    
    return {
        'length': dp[m][n],
        'sequence': lcs_sequence,
        'ref_positions': lcs_positions_ref,
        'typed_positions': lcs_positions_typed,
        'similarity_ratio': dp[m][n] / max(m, n) if max(m, n) > 0 else 0
    }

def calculate_edit_distance(str1, str2):
    """
    Calculate the Levenshtein distance between two strings.
    Used for character-level comparison within words.
    """
    if not str1:
        return len(str2)
    if not str2:
        return len(str1)
    
    # Create matrix
    matrix = [[0] * (len(str2) + 1) for _ in range(len(str1) + 1)]
    
    # Initialize first row and column
    for i in range(len(str1) + 1):
        matrix[i][0] = i
    for j in range(len(str2) + 1):
        matrix[0][j] = j
    
    # Fill matrix
    for i in range(1, len(str1) + 1):
        for j in range(1, len(str2) + 1):
            if str1[i-1] == str2[j-1]:
                cost = 0
            else:
                cost = 1
            
            matrix[i][j] = min(
                matrix[i-1][j] + 1,      # deletion
                matrix[i][j-1] + 1,      # insertion
                matrix[i-1][j-1] + cost  # substitution
            )
    
    return matrix[len(str1)][len(str2)]

def is_similar_word(word1, word2, threshold=0.7):
    """
    Determine if two words are similar based on edit distance.
    Helps identify typos vs completely different words.
    """
    if not word1 or not word2:
        return False
    
    # Exact match (case-insensitive)
    if word1.lower() == word2.lower():
        return True
    
    # Calculate similarity ratio
    max_len = max(len(word1), len(word2))
    if max_len == 0:
        return True
    
    edit_dist = calculate_edit_distance(word1.lower(), word2.lower())
    similarity = 1 - (edit_dist / max_len)
    
    return similarity >= threshold

def normalize_punctuation(text):
    """
    Normalize punctuation for better comparison.
    Handle common punctuation variations and spacing issues.
    """
    import re
    
    # Remove extra spaces around punctuation
    text = re.sub(r'\s+([,.!?;:])', r'\1', text)
    
    # Ensure single space after punctuation
    text = re.sub(r'([,.!?;:])\s*', r'\1 ', text)
    
    # Handle quotes and apostrophes - use unicode escape sequences
    text = re.sub(r'[\u201c\u201d]', '"', text)  # Normalize smart quotes
    text = re.sub(r'[\u2018\u2019]', "'", text)  # Normalize smart apostrophes
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def split_text_with_punctuation(text):
    """
    Split text into words while preserving punctuation as separate tokens.
    This helps with better punctuation analysis.
    """
    import re
    # Split on whitespace and punctuation, but keep punctuation as separate tokens
    tokens = re.findall(r'\w+|[.,!?;:"\'()]', text)
    return tokens

def enhanced_word_alignment(ref_tokens, typed_tokens, lcs_data):
    """
    Create enhanced word alignment using LCS information.
    Provides detailed mapping between reference and typed tokens (words + punctuation).
    """
    alignment = []
    ref_idx = 0
    typed_idx = 0
    lcs_idx = 0
    
    lcs_ref_positions = set(lcs_data['ref_positions'])
    lcs_typed_positions = set(lcs_data['typed_positions'])
    
    while ref_idx < len(ref_tokens) or typed_idx < len(typed_tokens):
        # Check if current positions are in LCS (correct matches)
        if (ref_idx in lcs_ref_positions and typed_idx in lcs_typed_positions and
            lcs_idx < len(lcs_data['ref_positions']) and
            lcs_data['ref_positions'][lcs_idx] == ref_idx and
            lcs_data['typed_positions'][lcs_idx] == typed_idx):
            
            alignment.append({
                'type': 'correct',
                'ref_word': ref_tokens[ref_idx] if ref_idx < len(ref_tokens) else '',
                'typed_word': typed_tokens[typed_idx] if typed_idx < len(typed_tokens) else '',
                'ref_index': ref_idx,
                'typed_index': typed_idx
            })
            ref_idx += 1
            typed_idx += 1
            lcs_idx += 1
            
        # Reference token missing in typed text
        elif ref_idx < len(ref_tokens) and ref_idx not in lcs_ref_positions:
            alignment.append({
                'type': 'missing',
                'ref_word': ref_tokens[ref_idx],
                'typed_word': '',
                'ref_index': ref_idx,
                'typed_index': None
            })
            ref_idx += 1
            
        # Extra token in typed text
        elif typed_idx < len(typed_tokens) and typed_idx not in lcs_typed_positions:
            # Check if it's a similar word (typo) to nearby reference words
            is_typo = False
            typo_ref_idx = None
            
            # Only check for typos with actual words (not punctuation)
            if re.match(r'\w+', typed_tokens[typed_idx]):
                # Look for similar words in a small window around current position
                window_start = max(0, ref_idx - 2)
                window_end = min(len(ref_tokens), ref_idx + 3)
                
                for check_idx in range(window_start, window_end):
                    if (check_idx not in lcs_ref_positions and
                        re.match(r'\w+', ref_tokens[check_idx]) and
                        is_similar_word(ref_tokens[check_idx], typed_tokens[typed_idx])):
                        is_typo = True
                        typo_ref_idx = check_idx
                        break
            
            if is_typo and typo_ref_idx is not None:
                alignment.append({
                    'type': 'typo',
                    'ref_word': ref_tokens[typo_ref_idx],
                    'typed_word': typed_tokens[typed_idx],
                    'ref_index': typo_ref_idx,
                    'typed_index': typed_idx,
                    'similarity': 1 - (calculate_edit_distance(ref_tokens[typo_ref_idx].lower(),
                                                             typed_tokens[typed_idx].lower()) /
                                     max(len(ref_tokens[typo_ref_idx]), len(typed_tokens[typed_idx])))
                })
                # Skip the reference word that was matched as typo
                if typo_ref_idx == ref_idx:
                    ref_idx += 1
            else:
                alignment.append({
                    'type': 'extra',
                    'ref_word': '',
                    'typed_word': typed_tokens[typed_idx],
                    'ref_index': None,
                    'typed_index': typed_idx
                })
            
            typed_idx += 1
            
        else:
            # Move to next available position
            if ref_idx < len(ref_tokens):
                ref_idx += 1
            if typed_idx < len(typed_tokens):
                typed_idx += 1
    
    return alignment

def analyze_punctuation_errors(ref_text, typed_text):
    """
    Analyze punctuation errors with better context awareness.
    Handles cases where punctuation is correctly typed but in different positions.
    """
    import re
    
    # Extract punctuation with positions
    ref_punct = [(m.group(), m.start()) for m in re.finditer(r'[,.!?;:"\'()]', ref_text)]
    typed_punct = [(m.group(), m.start()) for m in re.finditer(r'[,.!?;:"\'()]', typed_text)]
    
    punct_errors = []
    
    # Count each punctuation type
    ref_counts = {}
    typed_counts = {}
    
    for punct, _ in ref_punct:
        ref_counts[punct] = ref_counts.get(punct, 0) + 1
    
    for punct, _ in typed_punct:
        typed_counts[punct] = typed_counts.get(punct, 0) + 1
    
    # Compare counts
    all_punct = set(list(ref_counts.keys()) + list(typed_counts.keys()))
    
    for punct in all_punct:
        ref_count = ref_counts.get(punct, 0)
        typed_count = typed_counts.get(punct, 0)
        
        if ref_count != typed_count:
            if ref_count > typed_count:
                punct_errors.append({
                    'type': 'missing_punctuation',
                    'punctuation': punct,
                    'count': ref_count - typed_count,
                    'message': f'Missing {ref_count - typed_count} "{punct}"'
                })
            else:
                punct_errors.append({
                    'type': 'extra_punctuation',
                    'punctuation': punct,
                    'count': typed_count - ref_count,
                    'message': f'Extra {typed_count - ref_count} "{punct}"'
                })
    
    return punct_errors

def enhanced_compare_texts(reference_text, typed_text):
    """
    Enhanced text comparison using LCS strategy with improved error detection.
    
    This function addresses the original issue where correctly typed words like "However..."
    were incorrectly marked as errors by using token-based comparison that handles
    words and punctuation separately.
    
    Args:
        reference_text (str): The correct reference text
        typed_text (str): The user's typed text
        
    Returns:
        dict: Detailed comparison results with enhanced error highlighting
    """
    if not reference_text or not typed_text:
        return {
            'words_correct': 0,
            'words_wrong': 0,
            'accuracy_percentage': 0,
            'total_words': 0,
            'typed_words': 0,
            'enhanced_comparison': [],
            'lcs_analysis': {},
            'punctuation_errors': [],
            'error_summary': {}
        }
    
    # Normalize texts for better comparison
    normalized_ref = normalize_punctuation(reference_text)
    normalized_typed = normalize_punctuation(typed_text)
    
    # Split into tokens (words + punctuation) for more accurate analysis
    ref_tokens = split_text_with_punctuation(normalized_ref)
    typed_tokens = split_text_with_punctuation(normalized_typed)
    
    # Also get word-only counts for accuracy calculation
    ref_words = [token for token in ref_tokens if re.match(r'\w+', token)]
    typed_words = [token for token in typed_tokens if re.match(r'\w+', token)]
    
    # Calculate LCS for token-level comparison
    ref_tokens_text = ' '.join(ref_tokens)
    typed_tokens_text = ' '.join(typed_tokens)
    lcs_data = longest_common_subsequence(ref_tokens_text, typed_tokens_text)
    
    # Create enhanced token alignment
    alignment = enhanced_word_alignment(ref_tokens, typed_tokens, lcs_data)
    
    # Count correct and incorrect items (focus on words, not punctuation for main score)
    words_correct = 0
    words_wrong = 0
    enhanced_comparison = []
    
    for item in alignment:
        is_word = re.match(r'\w+', item.get('ref_word', '')) or re.match(r'\w+', item.get('typed_word', ''))
        
        if item['type'] == 'correct':
            if is_word:
                words_correct += 1
            enhanced_comparison.append({
                'type': 'correct',
                'reference_word': item['ref_word'],
                'typed_word': item['typed_word'],
                'display_word': item['typed_word']
            })
        elif item['type'] == 'typo':
            if is_word:
                words_wrong += 1
            enhanced_comparison.append({
                'type': 'wrong',
                'reference_word': item['ref_word'],
                'typed_word': item['typed_word'],
                'display_word': item['typed_word'],
                'correction': item['ref_word'],
                'similarity': item.get('similarity', 0),
                'error_type': 'spelling_error'
            })
        elif item['type'] == 'missing':
            if re.match(r'\w+', item['ref_word']):
                words_wrong += 1
            enhanced_comparison.append({
                'type': 'missed',
                'reference_word': item['ref_word'],
                'typed_word': '',
                'display_word': item['ref_word']
            })
        elif item['type'] == 'extra':
            if re.match(r'\w+', item['typed_word']):
                words_wrong += 1
            enhanced_comparison.append({
                'type': 'extra',
                'reference_word': '',
                'typed_word': item['typed_word'],
                'display_word': item['typed_word']
            })
    
    # Calculate accuracy based on words only
    total_words = len(ref_words)
    accuracy_percentage = (words_correct / total_words * 100) if total_words > 0 else 0
    
    # Analyze punctuation errors
    punctuation_errors = analyze_punctuation_errors(reference_text, typed_text)
    
    # Create error summary
    error_summary = {
        'spelling_errors': len([item for item in enhanced_comparison if item.get('error_type') == 'spelling_error']),
        'missing_words': len([item for item in enhanced_comparison if item['type'] == 'missed' and re.match(r'\w+', item.get('reference_word', ''))]),
        'extra_words': len([item for item in enhanced_comparison if item['type'] == 'extra' and re.match(r'\w+', item.get('typed_word', ''))]),
        'punctuation_errors': len(punctuation_errors),
        'similarity_score': lcs_data['similarity_ratio']
    }
    
    return {
        'words_correct': words_correct,
        'words_wrong': words_wrong,
        'accuracy_percentage': round(accuracy_percentage, 2),
        'total_words': total_words,
        'typed_words': len(typed_words),
        'enhanced_comparison': enhanced_comparison,
        'lcs_analysis': lcs_data,
        'punctuation_errors': punctuation_errors,
        'error_summary': error_summary
    }

def test_comparison_examples():
    """
    Test the enhanced comparison with various examples including the "However..." case.
    """
    test_cases = [
        {
            'name': 'Correct "However" case',
            'reference': 'However, this is a test sentence.',
            'typed': 'However, this is a test sentence.',
            'expected_errors': 0
        },
        {
            'name': 'Typo in "However"',
            'reference': 'However, this is a test sentence.',
            'typed': 'Howver, this is a test sentence.',
            'expected_errors': 1
        },
        {
            'name': 'Missing punctuation',
            'reference': 'Hello, world! How are you?',
            'typed': 'Hello world How are you',
            'expected_errors': 3  # Missing comma, exclamation, question mark
        },
        {
            'name': 'Extra word',
            'reference': 'The quick brown fox',
            'typed': 'The very quick brown fox',
            'expected_errors': 1
        },
        {
            'name': 'Missing word',
            'reference': 'The quick brown fox jumps',
            'typed': 'The quick fox jumps',
            'expected_errors': 1
        }
    ]
    
    print("Running LCS Text Comparison Tests:")
    print("=" * 50)
    
    for test in test_cases:
        result = enhanced_compare_texts(test['reference'], test['typed'])
        
        print(f"\nTest: {test['name']}")
        print(f"Reference: {test['reference']}")
        print(f"Typed:     {test['typed']}")
        print(f"Accuracy:  {result['accuracy_percentage']}%")
        print(f"Errors:    {result['words_wrong']} (expected: {test['expected_errors']})")
        print(f"LCS Similarity: {result['lcs_analysis']['similarity_ratio']:.2f}")
        
        # Show detailed comparison
        for item in result['enhanced_comparison']:
            if item['type'] != 'correct':
                print(f"  Error: {item['type']} - '{item.get('typed_word', '')}' -> '{item.get('reference_word', '')}'")

if __name__ == "__main__":
    test_comparison_examples()
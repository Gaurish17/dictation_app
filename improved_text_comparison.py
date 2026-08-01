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

def _align_block(ref_words, typed_words, ref_off, typed_off):
    """
    Optimally align two SHORT word sub-sequences using Needleman-Wunsch
    global alignment, returning classified comparison items with indices
    offset back into the full sequences.

    This is the core fix for false errors: within a mismatched region,
    identical words align at zero cost, so a correctly-typed word can never
    be mis-flagged just because a neighbouring word was inserted or dropped.
    Indices are offset by (ref_off, typed_off) so callers can run this on a
    slice of the full text.
    """
    n = len(ref_words)
    m = len(typed_words)

    if n == 0:
        return [{'type': 'extra', 'ref_word': '', 'typed_word': w,
                 'ref_index': None, 'typed_index': typed_off + j}
                for j, w in enumerate(typed_words)]
    if m == 0:
        return [{'type': 'missing', 'ref_word': w, 'typed_word': '',
                 'ref_index': ref_off + i, 'typed_index': None}
                for i, w in enumerate(ref_words)]

    # Guard: the O(n*m) DP is only worth running on reasonably sized regions.
    # A huge mismatched region means the texts diverged wildly (near-zero
    # accuracy there anyway), so fall back to cheap positional pairing to keep
    # the request fast. Realistic passages produce small regions and never hit
    # this; it exists only to bound worst-case time on garbage input.
    if n * m > 40000:
        fb = []
        for k in range(min(n, m)):
            rw, tw = ref_words[k], typed_words[k]
            if rw.lower() == tw.lower():
                fb.append({'type': 'correct', 'ref_word': rw, 'typed_word': tw,
                           'ref_index': ref_off + k, 'typed_index': typed_off + k})
            else:
                sim = word_similarity(rw, tw)
                fb.append({'type': 'typo' if sim >= 0.6 else 'wrong', 'ref_word': rw,
                           'typed_word': tw, 'ref_index': ref_off + k,
                           'typed_index': typed_off + k, 'similarity': sim})
        for k in range(min(n, m), n):
            fb.append({'type': 'missing', 'ref_word': ref_words[k], 'typed_word': '',
                       'ref_index': ref_off + k, 'typed_index': None})
        for k in range(min(n, m), m):
            fb.append({'type': 'extra', 'ref_word': '', 'typed_word': typed_words[k],
                       'ref_index': None, 'typed_index': typed_off + k})
        return fb

    r_lc = [w.lower() for w in ref_words]
    t_lc = [w.lower() for w in typed_words]

    GAP = 1.0          # cost of a missing (ref) or extra (typed) word
    SUB_DIFF = 2.0     # cost of aligning two unrelated words (== two gaps)

    # Cache substitution costs so we don't recompute Levenshtein in backtrace
    _sub_cache = {}
    def sub_cost(i, j):
        key = (i, j)
        c = _sub_cache.get(key)
        if c is not None:
            return c
        if r_lc[i] == t_lc[j]:
            c = 0.0
        else:
            sim = word_similarity(ref_words[i], typed_words[j])
            # A typo (high similarity) is cheaper than two gaps, so similar
            # words align to each other; unrelated words cost the same as
            # deleting one and inserting the other.
            c = (1.0 - sim) if sim >= 0.6 else SUB_DIFF
        _sub_cache[key] = c
        return c

    # DP cost matrix
    dp = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        dp[i][0] = i * GAP
    for j in range(1, m + 1):
        dp[0][j] = j * GAP
    for i in range(1, n + 1):
        row = dp[i]
        prev = dp[i - 1]
        for j in range(1, m + 1):
            diag = prev[j - 1] + sub_cost(i - 1, j - 1)
            up = prev[j] + GAP        # reference word missing from typed text
            left = row[j - 1] + GAP   # extra word in typed text
            row[j] = diag if (diag <= up and diag <= left) else (up if up <= left else left)

    # Backtrace. Prefer the diagonal on ties so a genuine one-to-one change
    # is reported as a single substitution rather than missing + extra.
    i, j = n, m
    aligned = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + sub_cost(i - 1, j - 1):
            aligned.append(('sub', i - 1, j - 1))
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + GAP:
            aligned.append(('missing', i - 1, None))
            i -= 1
        else:
            aligned.append(('extra', None, j - 1))
            j -= 1
    aligned.reverse()

    comparison = []
    for kind, ri, tj in aligned:
        if kind == 'sub':
            ref_word = ref_words[ri]
            typed_word = typed_words[tj]
            if ref_word.lower() == typed_word.lower():
                comparison.append({
                    'type': 'correct',
                    'ref_word': ref_word,
                    'typed_word': typed_word,
                    'ref_index': ref_off + ri,
                    'typed_index': typed_off + tj
                })
            else:
                similarity = word_similarity(ref_word, typed_word)
                comparison.append({
                    'type': 'typo' if similarity >= 0.6 else 'wrong',
                    'ref_word': ref_word,
                    'typed_word': typed_word,
                    'ref_index': ref_off + ri,
                    'typed_index': typed_off + tj,
                    'similarity': similarity
                })
        elif kind == 'missing':
            comparison.append({
                'type': 'missing',
                'ref_word': ref_words[ri],
                'typed_word': '',
                'ref_index': ref_off + ri,
                'typed_index': None
            })
        else:  # extra
            comparison.append({
                'type': 'extra',
                'ref_word': '',
                'typed_word': typed_words[tj],
                'ref_index': None,
                'typed_index': typed_off + tj
            })

    return comparison


def compare_word_sequences(ref_words, typed_words):
    """
    Compare two word sequences and classify each position as
    correct / typo / wrong / missing / extra.

    Hybrid strategy for speed AND correctness:
      * difflib SequenceMatcher finds the long runs that genuinely match
        (fast, and reliable anchors), plus the small mismatched regions
        between them.
      * Each mismatched ("replace") region is realigned with an optimal
        word-level Needleman-Wunsch alignment (_align_block).

    difflib alone paired the words inside a mismatched region purely by
    position, so a single extra or omitted word (common when a typist
    self-corrects, e.g. "of of" / "the the") shifted the pairing and every
    correct word after it was marked wrong. Realigning those regions removes
    the false errors, while the anchor-based structure keeps it fast enough
    for long passages (the expensive alignment only runs on the small gaps).
    """
    # Match case-insensitively; disable autojunk so frequent short words
    # (the, of, a) are not treated as junk in long passages.
    matcher = SequenceMatcher(None, [w.lower() for w in ref_words],
                              [w.lower() for w in typed_words], autojunk=False)

    comparison = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            for k in range(i2 - i1):
                comparison.append({
                    'type': 'correct',
                    'ref_word': ref_words[i1 + k],
                    'typed_word': typed_words[j1 + k],
                    'ref_index': i1 + k,
                    'typed_index': j1 + k
                })
        elif tag == 'delete':
            for k in range(i2 - i1):
                comparison.append({
                    'type': 'missing',
                    'ref_word': ref_words[i1 + k],
                    'typed_word': '',
                    'ref_index': i1 + k,
                    'typed_index': None
                })
        elif tag == 'insert':
            for k in range(j2 - j1):
                comparison.append({
                    'type': 'extra',
                    'ref_word': '',
                    'typed_word': typed_words[j1 + k],
                    'ref_index': None,
                    'typed_index': j1 + k
                })
        elif tag == 'replace':
            comparison.extend(
                _align_block(ref_words[i1:i2], typed_words[j1:j2], i1, j1)
            )

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
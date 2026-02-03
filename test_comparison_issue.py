#!/usr/bin/env python3
"""Test to identify why correctly typed words show as wrong"""

from improved_text_comparison import enhanced_compare_texts

# Test cases with common issues
test_cases = [
    {
        'name': 'Case sensitivity',
        'reference': 'The Quick Brown Fox',
        'typed': 'the quick brown fox'
    },
    {
        'name': 'Extra spaces',
        'reference': 'Hello world test',
        'typed': 'Hello  world  test'
    },
    {
        'name': 'Unicode quotes',
        'reference': 'He said "hello"',
        'typed': 'He said "hello"'
    },
    {
        'name': 'Apostrophe variants',
        'reference': "don't can't won't",
        'typed': "don't can't won't"
    },
    {
        'name': 'Perfect match',
        'reference': 'Hello world this is a test',
        'typed': 'Hello world this is a test'
    }
]

print("=" * 60)
print("TESTING FOR COMPARISON ISSUES")
print("=" * 60)

for test in test_cases:
    result = enhanced_compare_texts(test['reference'], test['typed'])
    print(f'\n{test["name"]}:')
    print(f'  Reference: "{test["reference"]}"')
    print(f'  Typed:     "{test["typed"]}"')
    print(f'  Correct: {result["words_correct"]}/{result["total_words"]}')
    print(f'  Wrong: {result["words_wrong"]}')
    print(f'  Accuracy: {result["accuracy_percentage"]}%')
    
    if result['words_wrong'] > 0 and test['name'] != 'Case sensitivity':
        print(f'  ❌ ISSUE DETECTED - Words marked wrong incorrectly!')
        # Show which words are wrong
        for item in result['enhanced_comparison']:
            if item['type'] != 'correct':
                print(f'     - {item["type"]}: ref="{item.get("reference_word", "")}" typed="{item.get("typed_word", "")}"')
    elif result['words_correct'] == result['total_words']:
        print(f'  ✅ All words correct')

print("\n" + "=" * 60)
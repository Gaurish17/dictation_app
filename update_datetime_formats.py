#!/usr/bin/env python3
"""
Script to update datetime formats in templates to use IST timezone filters
Converts all .strftime() calls to use the new Jinja2 filters
"""

import os
import re

# Directory containing templates
TEMPLATES_DIR = 'templates'

# Mapping of old formats to new filter usage
REPLACEMENTS = [
    # DateTime formats - DD-MM-YYYY HH:MM AM/PM
    (r"\.strftime\('%d-%m-%Y %H:%M'\)", "|format_datetime('%d-%m-%Y %I:%M %p')"),
    (r"\.strftime\('%Y-%m-%d %H:%M'\)", "|format_datetime('%d-%m-%Y %I:%M %p')"),
    (r"\.strftime\('%d %B %Y at %I:%M %p'\)", "|format_datetime('%d %B %Y at %I:%M %p')"),
    (r"\.strftime\('%m/%d %H:%M'\)", "|format_datetime('%d-%m-%Y %I:%M %p')"),
    
    # Date only formats - DD-MM-YYYY
    (r"\.strftime\('%Y-%m-%d'\)", "|format_date('%d-%m-%Y')"),
    (r"\.strftime\('%d-%m-%Y'\)", "|format_date('%d-%m-%Y')"),
    (r"\.strftime\('%m/%d'\)", "|format_date('%d-%m-%Y')"),
    
    # Time only formats - HH:MM AM/PM
    (r"\.strftime\('%H:%M'\)", "|format_time('%I:%M %p')"),
    (r"\.strftime\('%I:%M %p'\)", "|format_time('%I:%M %p')"),
]

def update_template(filepath):
    """Update a single template file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Apply all replacements
    for old_pattern, new_filter in REPLACEMENTS:
        content = re.sub(old_pattern, new_filter, content)
    
    # Only write if changes were made
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Update all template files"""
    updated_count = 0
    
    for filename in os.listdir(TEMPLATES_DIR):
        if filename.endswith('.html'):
            filepath = os.path.join(TEMPLATES_DIR, filename)
            if update_template(filepath):
                print(f"✅ Updated: {filename}")
                updated_count += 1
            else:
                print(f"⏭️  Skipped: {filename} (no changes)")
    
    print(f"\n📊 Total files updated: {updated_count}")

if __name__ == '__main__':
    main()
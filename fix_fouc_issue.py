#!/usr/bin/env python3
"""
Fix FOUC (Flash of Unstyled Content) issue across all HTML templates.
This script adds critical CSS and resource hints to prevent icons from appearing oversized.
"""

import os
import re

CRITICAL_CSS_BLOCK = """    <!-- Preconnect to CDN for faster resource loading -->
    <link rel="preconnect" href="https://cdn.tailwindcss.com" crossorigin>
    <link rel="dns-prefetch" href="https://cdn.tailwindcss.com">
    
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Critical CSS to prevent FOUC */
        svg {
            width: 1.5rem;
            height: 1.5rem;
            display: inline-block;
            vertical-align: middle;
        }
        
        body {
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        }
        
        * {
            box-sizing: border-box;
        }
        
"""

def fix_html_file(filepath):
    """Fix a single HTML file by adding critical CSS and resource hints."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'Preconnect to CDN for faster resource loading' in content:
            print(f"✓ Already fixed: {filepath}")
            return False
        
        if 'cdn.tailwindcss.com' not in content:
            print(f"⊗ No Tailwind CDN: {filepath}")
            return False
        
        pattern = r'(\s*)<script src="https://cdn\.tailwindcss\.com"></script>\s*\n(\s*)<style>'
        
        if re.search(pattern, content):
            new_content = re.sub(
                pattern,
                r'\1' + CRITICAL_CSS_BLOCK.replace('\n', '\n' + r'\1'),
                content
            )
        else:
            pattern2 = r'(\s*)<script src="https://cdn\.tailwindcss\.com"></script>'
            if re.search(pattern2, content):
                new_content = re.sub(
                    pattern2,
                    r'\1' + CRITICAL_CSS_BLOCK.replace('\n', '\n' + r'\1').rstrip(),
                    content
                )
            else:
                print(f"⚠ Pattern not found: {filepath}")
                return False
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✓ Fixed: {filepath}")
        return True
        
    except Exception as e:
        print(f"✗ Error fixing {filepath}: {e}")
        return False

def main():
    """Main function to fix all HTML templates."""
    templates_dir = 'templates'
    
    if not os.path.exists(templates_dir):
        print(f"Error: {templates_dir} directory not found!")
        return
    
    print("🔧 Fixing FOUC issue in HTML templates...\n")
    
    fixed_count = 0
    total_count = 0
    
    for filename in sorted(os.listdir(templates_dir)):
        if filename.endswith('.html'):
            filepath = os.path.join(templates_dir, filename)
            total_count += 1
            
            if fix_html_file(filepath):
                fixed_count += 1
    
    print(f"\n{'='*60}")
    print(f"✓ Fixed {fixed_count} out of {total_count} HTML files")
    print(f"{'='*60}")
    
    if fixed_count > 0:
        print("\n📋 Summary of changes:")
        print("  • Added DNS prefetch and preconnect to Tailwind CDN")
        print("  • Added critical CSS to prevent icon size issues")
        print("  • SVG icons now have default size before CSS loads")
        print("  • Body and box-sizing defaults set immediately")
        print("\n✨ The FOUC issue should now be resolved!")

if __name__ == '__main__':
    main()
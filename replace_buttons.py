import os
import re

def process_file(filepath):
    if not os.path.exists(filepath):
        return False
        
    with open(filepath, 'r') as f:
        content = f.read()
        
    # Check if there's any <button to replace
    if '<button' not in content:
        return False
        
    original = content
    
    # We will ONLY replace <button if it has className that implies a standard button, or we can just replace all <button with <Button if it's safe.
    # Actually, replacing all might break things if not careful, but the user asked for full replacement.
    
    # Let's replace <button -> <Button, </button> -> </Button>
    # And add import { Button } from "@/components/ui/button"; at the top
    
    content = content.replace('<button', '<Button')
    content = content.replace('</button>', '</Button>')
    
    if '<Button' in content and 'import { Button }' not in content:
        # insert import after last import
        lines = content.split('\n')
        last_import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('import '):
                last_import_idx = i
        
        lines.insert(last_import_idx + 1, 'import { Button } from "@/components/ui/button";')
        content = '\n'.join(lines)
        
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Updated {filepath}")
        return True
    return False

# List of files we know have buttons that are safe to just capitalize because they already have full tailwind classes.
# Shadcn Button injects default variants. We should probably append variant="ghost" to raw buttons to remove the default background!
# No, if we do that, we need a smarter parser.

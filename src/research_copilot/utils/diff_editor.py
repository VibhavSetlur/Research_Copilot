import os

def patch_file(root_dir, filepath, search_block, replace_block):
    full_path = os.path.join(root_dir, filepath)
    if not os.path.exists(full_path):
        return f"Error: File {filepath} not found."
    
    with open(full_path, 'r') as f:
        content = f.read()

    if search_block not in content:
        return f"Error: search_block not found exactly as provided in {filepath}."
        
    new_content = content.replace(search_block, replace_block, 1)
    
    with open(full_path, 'w') as f:
        f.write(new_content)
        
    return f"Successfully patched {filepath}."

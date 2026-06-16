# inspect_repo.py
import os

def generate_repo_map(startpath):
    print(f"=== REPOSITORY MAP FOR: {os.path.basename(os.path.abspath(startpath))} ===")
    
    # Folders we want to list, but not dump their thousands of internal files
    skip_internal_contents = {'venv', '__pycache__', 'chart_frames', '.git'}
    
    for root, dirs, files in os.walk(startpath):
        # Calculate current depth level for formatting tree structure
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * level
        folder_name = os.path.basename(root)
        
        if folder_name:
            print(f"{indent}📁 {folder_name}/")
            
        # Check if we should skip printing the files inside this directory
        if folder_name in skip_internal_contents:
            print(f"{indent}    [... contents hidden to prevent clutter ...]")
            # Modify dirs in-place so os.walk doesn't recurse deeper into skipped folders
            dirs.clear()
            continue
            
        sub_indent = ' ' * 4 * (level + 1)
        for f in sorted(files):
            # Skip the inspection script itself from the final printout
            if f == 'inspect_repo.py':
                continue
            print(f"{sub_indent}📄 {f}")

if __name__ == "__main__":
    # Runs in whichever folder the script is placed
    current_directory = os.path.dirname(os.path.abspath(__file__))
    generate_repo_map(current_directory)
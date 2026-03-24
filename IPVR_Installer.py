import webview
import os
import sys
import shutil
import zipfile
import subprocess
import glob
import json
from pyshortcuts import make_shortcut  # Reemplazamos win32com.client por pyshortcuts

def get_base_path():
    # Get execution path (supports PyInstaller)
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

class InstallApi:
    # API exposed to the webview frontend
    def __init__(self):
        self.local_app_data = os.environ.get('LOCALAPPDATA', '')
        self.app_data = os.environ.get('APPDATA', '')
        self.desktop_path = os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop')
        self.base_dir = get_base_path()

    def check_system(self):
        # Bypass system checks for now
        return True

    def select_folder(self):
        # Open OS folder selection dialog
        try:
            window = webview.windows[0]
            result = window.create_file_dialog(webview.FileDialog.FOLDER, directory="")
            if result and len(result) > 0:
                return result[0]
        except Exception:
            pass
        return None

    def verify_exe(self, folder_path):
        # Validate game executable paths
        exe_path = os.path.join(folder_path, "RaccoonCh1", "Binaries", "Win64", "RaccoonCh1-Win64-Shipping.exe")
        exe_alt = os.path.join(folder_path, "RaccoonCh1-Win64-Shipping.exe")
        return os.path.exists(exe_path) or os.path.exists(exe_alt)

    def install(self, folder_path, lenguaje="en"):
        try:
            # Determine target directories
            win64_path = os.path.join(folder_path, "RaccoonCh1", "Binaries", "Win64")
            if not os.path.exists(win64_path):
                win64_path = folder_path

            exe_name_no_ext = "RaccoonCh1-Win64-Shipping"
            uevr_profile_roaming = os.path.join(self.app_data, "UnrealVRMod", exe_name_no_ext)

            os.makedirs(uevr_profile_roaming, exist_ok=True)
            os.makedirs(win64_path, exist_ok=True)
            
            # Extract UEVR profile zip
            target_zip = os.path.join(self.base_dir, f"{exe_name_no_ext}.zip")
            if os.path.exists(target_zip):
                with zipfile.ZipFile(target_zip, 'r') as zip_ref:
                    zip_ref.extractall(uevr_profile_roaming)

            # Copy launcher executable
            launcher_src = os.path.join(self.base_dir, "IPVR_Launcher.exe")
            launcher_dest = os.path.join(win64_path, "IPVR_Launcher.exe")
            if os.path.exists(launcher_src):
                shutil.copy2(launcher_src, launcher_dest)

            # Generate config file
            config_data = {"lenguaje": lenguaje}
            config_path = os.path.join(win64_path, "launcher_config.json")
            with open(config_path, "w", encoding="utf-8") as json_file:
                json.dump(config_data, json_file, indent=4)

            # Crear Acceso Directo usando pyshortcuts
            try:
                icon_path = os.path.join(self.base_dir, "logo.ico") # Ruta al icono
                
                # Verificamos si existe el icono para evitar errores de PyShortcuts si falta el archivo
                valid_icon = icon_path if os.path.exists(icon_path) else None

                make_shortcut(
                    script=launcher_dest,        # El archivo base a ejecutar
                    executable=launcher_dest,    # Forzamos el ejecutable para evitar errores
                    name='Indigo Park VR',
                    description='Indigo Park VR',
                    icon=valid_icon,             # Pasamos el icono
                    terminal=False,    
                    desktop=True,      
                    startmenu=True     
                )
                print("Acceso directo creado exitosamente con pyshortcuts.")
            except Exception as e:
                print(f"No se pudo crear el acceso directo: {e}")

            return "success"
            
        except Exception as e:
            print(f"Error during installation: {e}")
            return "error"

    def close_app(self):
        # Close main window
        if len(webview.windows) > 0:
            webview.windows[0].destroy()

def main():
    # Initialize and launch the installer UI
    api = InstallApi()
    
    webview.create_window(
        title='Indigo Park VR - Setup',
        url='IPVR_Installer.html',
        js_api=api,
        width=1080,
        height=720,
        frameless=True,
        easy_drag=False,
        background_color='#1a1a1a',
        transparent=False
    )
    
    webview.start(debug=False)

if __name__ == '__main__':
    main()
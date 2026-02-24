#!/usr/bin/env python3
"""
Launcher for Web Application + API Server
Zapuskaet odnovremenno API server i web server
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def main():
    """Zapustit vse komponenty"""
    base_dir = Path(__file__).parent
    
    print("=" * 60)
    print("ZAPUSK WEB PRILOZHENIYa + API SERVER")
    print("=" * 60)
    print()
    
    # 1. Zapuskaem API server v fone
    print("[1/3] Zapusk API servera...")
    api_process = subprocess.Popen(
        [sys.executable, "api_server.py"],
        cwd=base_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Daem vremya na zapusk
    time.sleep(2)
    
    # Proveryaem zapustilsya li
    if api_process.poll() is None:
        print("     API server zapushen na http://localhost:8000")
    else:
        print("     [!] Ne udalos zapustit API server")
        print("     Web prilozhenie budet rabotat v offline rezhime")
    
    print()
    
    # 2. Zapuskaem web server
    print("[2/3] Zapusk Web servera...")
    web_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "3000"],
        cwd=base_dir / "app",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(1)
    
    if web_process.poll() is None:
        print("     Web server zapushen na http://localhost:3000")
    else:
        print("     [!] Ne udalos zapustit web server")
        return
    
    print()
    
    # 3. Otkryvaem brauzer
    print("[3/3] Otkrytie brauzera...")
    webbrowser.open("http://localhost:3000")
    
    print()
    print("=" * 60)
    print("GOTOVO!")
    print("=" * 60)
    print()
    print("Dostupnye adresy:")
    print("  Web:   http://localhost:3000")
    print("  API:   http://localhost:8000")
    print()
    print("Dlya ostanovki nazhmite Ctrl+C")
    print("=" * 60)
    
    try:
        # Zhдем pokabor processy rabotayut
        while True:
            time.sleep(1)
            # Proveryaem zhivy li processy
            if api_process.poll() is not None and web_process.poll() is not None:
                break
    except KeyboardInterrupt:
        print("\n\nOstanovka...")
    finally:
        # Ubivaem processy
        if api_process.poll() is None:
            api_process.terminate()
            print("API server ostanovlen")
        
        if web_process.poll() is None:
            web_process.terminate()
            print("Web server ostanovlen")
        
        print("\nDo svidaniya!")

if __name__ == "__main__":
    main()

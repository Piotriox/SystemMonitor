# main.py

import tkinter as tk
import sys

try:
    import psutil
except ImportError:
    print("ERROR: psutil is not installed. Install it with: pip install psutil")
    sys.exit(1)

try:
    import matplotlib
    import matplotlib.pyplot as plt
except ImportError:
    print("ERROR: matplotlib is not installed. Install it with: pip install matplotlib")
    sys.exit(1)

from system_stats import SystemStats
from ui import SystemMonitorUI
from charts import ChartManager
from constants import UPDATE_INTERVAL


def main():
    root = tk.Tk()
    
    # İkonu ayarla
    root.iconbitmap('SystemMonitorLogo.ico')
    root.title('System Monitor')
    
    stats_manager = SystemStats()
    chart_manager = ChartManager(theme='dark')
    ui = SystemMonitorUI(root, stats_manager, chart_manager)
    
    def update_loop():
        try:
            ui.update_display()
        except Exception as e:
            print(f"Update error: {e}")
        
        root.after(UPDATE_INTERVAL, update_loop)
    
    root.after(UPDATE_INTERVAL, update_loop)
    
    root.mainloop()


if __name__ == "__main__":
    main()

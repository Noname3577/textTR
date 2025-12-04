#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text File Splitter & Merger - Main Entry Point
โปรแกรมแบ่งและรวมไฟล์ข้อความ พร้อมระบบแปลภาษา

This is the main entry point for the application.
Uses the new organized structure.
"""

import sys
import os

# Add the project root to path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def main():
    """Main entry point for the application"""
    try:
        # Import from new structure
        from gui.main_window import MainApplication
        from config.constants import STATUS_MESSAGES
        
        # Create and run the application
        app = MainApplication()
        app.update_status(STATUS_MESSAGES['ready'])
        app.run()
        
    except ImportError as e:
        # Handle missing modules
        error_msg = f"ไม่พบโมดูลที่จำเป็น: {str(e)}\n\n"
        error_msg += "กรุณาตรวจสอบว่าโครงสร้างไฟล์ถูกต้อง"
        
        print(error_msg)
        
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("ข้อผิดพลาด", error_msg)
            root.destroy()
        except:
            pass
        
        sys.exit(1)
        
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to show error dialog if tkinter is available
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", f"Failed to start application:\n{e}")
            root.destroy()
        except:
            pass
        
        sys.exit(1)


if __name__ == "__main__":
    main()
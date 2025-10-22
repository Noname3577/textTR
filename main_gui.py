#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main GUI Application for Text File Splitter & Merger
แอปพลิเคชัน GUI หลักสำหรับแบ่งและรวมไฟล์ข้อความ
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import glob
import shutil
from pathlib import Path

# Import modules
from constants import (
    APP_TITLE,
    APP_VERSION,
    DEFAULT_WINDOW_SIZE,
    MIN_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
    EMOJIS,
    STATUS_MESSAGES
)
from utils import center_window, open_file_manager, format_file_size
from gui_base import StatusMixin, ProgressMixin
from file_operations import FileSplitterTab, FileMergerTab
from translation_manager import TranslationTab
from file_viewer import FileViewerTab


class SettingsTab:
    """
    Tab สำหรับการตั้งค่าและเครื่องมือ
    """
    
    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        
        self.create_widgets()
    
    def create_widgets(self) -> None:
        """สร้าง widgets สำหรับ tab ตั้งค่า"""
        
        # Title
        title_label = ttk.Label(
            self.frame, 
            text=f"{EMOJIS['settings']} การตั้งค่าและเครื่องมือ", 
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(10, 20))
        
        # Default settings section
        self._create_default_settings_section()
        
        # File management tools section
        self._create_file_management_section()
        
        # Statistics section
        self._create_statistics_section()
    
    def _create_default_settings_section(self) -> None:
        """สร้างส่วนค่าเริ่มต้น"""
        defaults_frame = ttk.LabelFrame(
            self.frame, 
            text=f"{EMOJIS['settings']} ค่าเริ่มต้น", 
            padding=15
        )
        defaults_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        # Lines per file default
        lines_frame = ttk.Frame(defaults_frame)
        lines_frame.pack(fill='x', pady=5)
        
        ttk.Label(lines_frame, text="จำนวนบรรทัดต่อไฟล์เริ่มต้น:").grid(
            row=0, column=0, sticky='w', pady=5
        )
        
        self.lines_var = tk.IntVar(value=500)
        ttk.Spinbox(
            lines_frame, 
            from_=1, 
            to=10000, 
            width=10, 
            textvariable=self.lines_var
        ).grid(row=0, column=1, padx=(10, 0), pady=5)
        
        # Create folder default
        folder_frame = ttk.Frame(defaults_frame)
        folder_frame.pack(fill='x', pady=5)
        
        ttk.Label(folder_frame, text="สร้างโฟลเดอร์โดยอัตโนมัติ:").grid(
            row=0, column=0, sticky='w', pady=5
        )
        
        self.create_folder_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(folder_frame, variable=self.create_folder_var).grid(
            row=0, column=1, padx=(10, 0), pady=5, sticky='w'
        )
    
    def _create_file_management_section(self) -> None:
        """สร้างส่วนเครื่องมือจัดการไฟล์"""
        tools_frame = ttk.LabelFrame(
            self.frame, 
            text=f"{EMOJIS['clean']} เครื่องมือจัดการไฟล์", 
            padding=15
        )
        tools_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        # Cleanup section
        cleanup_frame = ttk.Frame(tools_frame)
        cleanup_frame.pack(fill='x', pady=5)
        
        ttk.Button(
            cleanup_frame, 
            text=f"{EMOJIS['clean']} ลบไฟล์ _part_ ทั้งหมด", 
            command=self.cleanup_part_files
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            cleanup_frame, 
            text=f"{EMOJIS['folder']} ลบโฟลเดอร์ _split_ เก่า", 
            command=self.cleanup_split_folders
        ).pack(side='left')
        
        # Folder management section
        folder_frame = ttk.Frame(tools_frame)
        folder_frame.pack(fill='x', pady=5)
        
        ttk.Button(
            folder_frame, 
            text=f"{EMOJIS['folder']} เปิดโฟลเดอร์ปัจจุบัน", 
            command=self.open_current_folder
        ).pack(side='left', padx=(0, 10))
    
    def _create_statistics_section(self) -> None:
        """สร้างส่วนสถิติและข้อมูล"""
        stats_frame = ttk.LabelFrame(
            self.frame, 
            text=f"{EMOJIS['info']} สถิติและข้อมูล", 
            padding=15
        )
        stats_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        # Stats text area
        from tkinter import scrolledtext
        self.stats_text = scrolledtext.ScrolledText(
            stats_frame, 
            height=10, 
            wrap='word'
        )
        self.stats_text.pack(fill='both', expand=True)
        
        # Refresh button
        ttk.Button(
            stats_frame, 
            text=f"{EMOJIS['refresh']} อัปเดตสถิติ", 
            command=self.update_stats
        ).pack(pady=(10, 0))
        
        # Load initial stats
        self.update_stats()
    
    # === File Management Methods ===
    
    def cleanup_part_files(self) -> None:
        """ลบไฟล์ _part_ ทั้งหมด"""
        current_dir = os.getcwd()
        part_files = glob.glob("*_part_*.txt")
        
        if not part_files:
            messagebox.showinfo("ข้อมูล", "ไม่พบไฟล์ _part_ ที่จะลบ")
            return
        
        result = messagebox.askyesno(
            "ยืนยัน", 
            f"พบไฟล์ _part_ จำนวน {len(part_files)} ไฟล์\nต้องการลบหรือไม่?"
        )
        
        if result:
            deleted_count = 0
            for file_path in part_files:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception:
                    pass
            
            messagebox.showinfo(
                "สำเร็จ", 
                f"ลบไฟล์สำเร็จ {deleted_count} จาก {len(part_files)} ไฟล์"
            )
    
    def cleanup_split_folders(self) -> None:
        """ลบโฟลเดอร์ _split_ เก่า"""
        current_dir = os.getcwd()
        split_folders = []
        
        for item in os.listdir(current_dir):
            if os.path.isdir(item) and '_split_' in item:
                split_folders.append(item)
        
        if not split_folders:
            messagebox.showinfo("ข้อมูล", "ไม่พบโฟลเดอร์ _split_ ที่จะลบ")
            return
        
        result = messagebox.askyesno(
            "ยืนยัน", 
            f"พบโฟลเดอร์ _split_ จำนวน {len(split_folders)} โฟลเดอร์\nต้องการลบหรือไม่?"
        )
        
        if result:
            deleted_count = 0
            for folder_path in split_folders:
                try:
                    shutil.rmtree(folder_path)
                    deleted_count += 1
                except Exception:
                    pass
            
            messagebox.showinfo(
                "สำเร็จ", 
                f"ลบโฟลเดอร์สำเร็จ {deleted_count} จาก {len(split_folders)} โฟลเดอร์"
            )
    
    def open_current_folder(self) -> None:
        """เปิดโฟลเดอร์ปัจจุบัน"""
        current_dir = os.getcwd()
        
        if open_file_manager(current_dir):
            messagebox.showinfo("สำเร็จ", f"เปิดโฟลเดอร์: {current_dir}")
        else:
            messagebox.showerror("ข้อผิดพลาด", "ไม่สามารถเปิดโฟลเดอร์ได้")
    
    def update_stats(self) -> None:
        """อัปเดตสถิติ"""
        try:
            current_dir = os.getcwd()
            
            # นับไฟล์ประเภทต่างๆ
            txt_files = glob.glob("*.txt")
            csv_files = glob.glob("*.csv")
            part_files = glob.glob("*_part_*.txt")
            
            # นับโฟลเดอร์
            split_folders = [d for d in os.listdir(current_dir) 
                           if os.path.isdir(d) and '_split_' in d]
            
            # คำนวณขนาดไฟล์รวม
            total_size = 0
            file_count = 0
            
            for file_pattern in ["*.txt", "*.csv", "*.log"]:
                for file_path in glob.glob(file_pattern):
                    try:
                        size = os.path.getsize(file_path)
                        total_size += size
                        file_count += 1
                    except Exception:
                        pass
            
            # สร้างข้อความสถิติ
            stats_text = f"""📊 สถิติโฟลเดอร์ปัจจุบัน

📂 โฟลเดอร์: {current_dir}
📄 ไฟล์ข้อความทั้งหมด: {file_count} ไฟล์
📏 ขนาดรวม: {format_file_size(total_size)}

📋 รายละเอียดไฟล์:
  • ไฟล์ .txt: {len(txt_files)} ไฟล์
  • ไฟล์ .csv: {len(csv_files)} ไฟล์
  • ไฟล์ _part_: {len(part_files)} ไฟล์

📁 โฟลเดอร์ _split_: {len(split_folders)} โฟลเดอร์

💡 คำแนะนำ:
"""
            
            # ให้คำแนะนำ
            if len(part_files) > 10:
                stats_text += "- คุณมีไฟล์ _part_ จำนวนมาก ควรพิจารณาทำความสะอาด\n"
            
            if len(split_folders) > 5:
                stats_text += "- คุณมีโฟลเดอร์ _split_ จำนวนมาก ควรพิจารณาลบโฟลเดอร์เก่า\n"
            
            if total_size > 100 * 1024 * 1024:  # > 100MB
                stats_text += "- ไฟล์มีขนาดใหญ่ ควรพิจารณาแบ่งไฟล์\n"
            
            if not txt_files and not csv_files:
                stats_text += "- ไม่พบไฟล์ข้อความ เริ่มต้นด้วยการเลือกไฟล์ในแท็บแบ่งไฟล์\n"
            
            # แสดงผลสถิติ
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, stats_text)
            
        except Exception as e:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, f"เกิดข้อผิดพลาดในการดึงสถิติ: {str(e)}")


class MainApplication(StatusMixin):
    """
    แอปพลิเคชัน GUI หลัก
    """
    
    def __init__(self):
        StatusMixin.__init__(self)
        
        self.root = tk.Tk()
        self.setup_main_window()
        self.create_widgets()
        self.setup_events()
    
    def setup_main_window(self) -> None:
        """ตั้งค่าหน้าต่างหลัก"""
        self.root.title(APP_TITLE)
        self.root.geometry(DEFAULT_WINDOW_SIZE)
        self.root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.root.resizable(True, True)
        
        # ตั้งค่า icon (ถ้ามี)
        try:
            # ลองหา icon ในโฟลเดอร์เดียวกัน
            icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass
        
        # จัดตำแหน่งหน้าต่างให้อยู่กลาง
        center_window(self.root)
        
        # ตั้งค่าสไตล์
        self.setup_styles()
    
    def setup_styles(self) -> None:
        """ตั้งค่าสไตล์สำหรับ GUI"""
        style = ttk.Style()
        
        # ใช้ theme ที่ดูทันสมัย
        try:
            style.theme_use('clam')
        except Exception:
            pass
        
        # กำหนดสีและฟอนต์
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Section.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TLabel', foreground='#2d8a2f')
        style.configure('Error.TLabel', foreground='#d32f2f')
        style.configure('Info.TLabel', foreground='#1976d2')
        style.configure('Warning.TLabel', foreground='#f57c00')
    
    def create_widgets(self) -> None:
        """สร้าง widgets หลัก"""
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_tabs()
        
        # Create status bar
        self.create_status_bar(self.root)
        
        # Create menu bar
        self.create_menu_bar()
    
    def create_tabs(self) -> None:
        """สร้าง tabs ต่างๆ"""
        
        # Tab 1: แบ่งไฟล์
        self.split_tab = FileSplitterTab(self.notebook)
        self.notebook.add(self.split_tab.frame, text=f"{EMOJIS['split']} แบ่งไฟล์")
        
        # Tab 2: รวมไฟล์
        self.merge_tab = FileMergerTab(self.notebook)
        self.notebook.add(self.merge_tab.frame, text=f"{EMOJIS['merge']} รวมไฟล์")
        
        # Tab 3: ดูไฟล์ข้อความ
        self.viewer_tab = FileViewerTab(self.notebook)
        self.notebook.add(self.viewer_tab.frame, text=f"{EMOJIS['view']} ดูไฟล์")
        
        # Tab 4: แปลข้อความ
        self.translation_tab = TranslationTab(self.notebook)
        self.notebook.add(self.translation_tab.frame, text=f"{EMOJIS['translate']} แปลข้อความ")
        
        # Tab 5: ตั้งค่า
        self.settings_tab = SettingsTab(self.notebook)
        self.notebook.add(self.settings_tab.frame, text=f"{EMOJIS['settings']} ตั้งค่า")
    
    def create_menu_bar(self) -> None:
        """สร้าง menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ไฟล์", menu=file_menu)
        file_menu.add_command(label="เปิดโฟลเดอร์ปัจจุบัน", command=self.open_current_folder)
        file_menu.add_separator()
        file_menu.add_command(label="ออกจากโปรแกรม", command=self.on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="เครื่องมือ", menu=tools_menu)
        tools_menu.add_command(label="ลบไฟล์ _part_ ทั้งหมด", command=self.settings_tab.cleanup_part_files)
        tools_menu.add_command(label="ลบโฟลเดอร์ _split_ เก่า", command=self.settings_tab.cleanup_split_folders)
        tools_menu.add_separator()
        tools_menu.add_command(label="อัปเดตสถิติ", command=self.settings_tab.update_stats)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="มุมมอง", menu=view_menu)
        view_menu.add_command(label="แท็บแบ่งไฟล์", command=lambda: self.notebook.select(0))
        view_menu.add_command(label="แท็บรวมไฟล์", command=lambda: self.notebook.select(1))
        view_menu.add_command(label="แท็บดูไฟล์", command=lambda: self.notebook.select(2))
        view_menu.add_command(label="แท็บแปลข้อความ", command=lambda: self.notebook.select(3))
        view_menu.add_command(label="แท็บตั้งค่า", command=lambda: self.notebook.select(4))
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ช่วยเหลือ", menu=help_menu)
        help_menu.add_command(label="วิธีใช้", command=self.show_help)
        help_menu.add_command(label="เกี่ยวกับโปรแกรม", command=self.show_about)
    
    def setup_events(self) -> None:
        """ตั้งค่า events"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Keyboard shortcuts
        self.root.bind('<Control-q>', lambda e: self.on_closing())
        self.root.bind('<Control-o>', lambda e: self.open_current_folder())
        self.root.bind('<F1>', lambda e: self.show_help())
        self.root.bind('<F5>', lambda e: self.settings_tab.update_stats())
    
    # === Event Handlers ===
    
    def on_closing(self) -> None:
        """จัดการเมื่อปิดโปรแกรม"""
        # หยุดการทำงานที่อาจกำลังดำเนินอยู่
        try:
            # หยุด auto refresh ใน viewer tab
            if hasattr(self.viewer_tab, 'stop_auto_refresh'):
                self.viewer_tab.stop_auto_refresh()
            
            # หยุด translation process
            if hasattr(self.translation_tab, 'cancel_translation'):
                self.translation_tab.cancel_translation = True
        except Exception:
            pass
        
        # ถามยืนยันก่อนปิด
        result = messagebox.askyesno(
            "ยืนยัน", 
            "ต้องการออกจากโปรแกรมหรือไม่?"
        )
        
        if result:
            self.root.destroy()
    
    def open_current_folder(self) -> None:
        """เปิดโฟลเดอร์ปัจจุบัน"""
        self.settings_tab.open_current_folder()
    
    def show_help(self) -> None:
        """แสดงหน้าต่างช่วยเหลือ"""
        help_window = tk.Toplevel(self.root)
        help_window.title("วิธีใช้โปรแกรม")
        help_window.geometry("600x500")
        help_window.resizable(True, True)
        help_window.transient(self.root)
        help_window.grab_set()
        
        center_window(help_window, 600, 500)
        
        # Help content
        from tkinter import scrolledtext
        help_text = scrolledtext.ScrolledText(help_window, wrap='word')
        help_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        help_content = f"""🔧 {APP_TITLE} - คู่มือการใช้งาน

📄 แท็บแบ่งไฟล์:
• เลือกไฟล์ข้อความที่ต้องการแบ่ง
• กำหนดจำนวนบรรทัดต่อไฟล์
• เลือกว่าจะสร้างโฟลเดอร์ใหม่หรือไม่
• กดปุ่ม "แบ่งไฟล์" เพื่อเริ่มการทำงาน

📋 แท็บรวมไฟล์:
• เลือกโฟลเดอร์ที่มีไฟล์ที่ต้องการรวม
• กำหนดรูปแบบชื่อไฟล์ (เช่น *_part_*.txt)
• เลือกชื่อไฟล์ผลลัพธ์ (หรือปล่อยให้อัตโนมัติ)
• กดปุ่ม "รวมไฟล์" เพื่อเริ่มการทำงาน

👁️ แท็บดูไฟล์:
• เลือกไฟล์ข้อความที่ต้องการดู
• เปิด/ปิดการรีเฟรชอัตโนมัติ
• ใช้ปุ่มนำทางเพื่อดูทีละบรรทัด
• กระโดดไปยังบรรทัดที่ต้องการ

🌐 แท็บแปลข้อความ:
• เลือกไฟล์ข้อความที่ต้องการแปล
• เลือกภาษาต้นฉบับและภาษาเป้าหมาย
• ดูข้อความในรูปแบบตาราง
• แปลทีละบรรทัด หรือแปลทั้งไฟล์
• บันทึกการแปลลงไฟล์เดิมหรือไฟล์ใหม่

⚙️ แท็บตั้งค่า:
• ดูสถิติโฟลเดอร์ปัจจุบัน
• จัดการไฟล์และโฟลเดอร์
• ลบไฟล์ _part_ และโฟลเดอร์ _split_ เก่า
• เปิดโฟลเดอร์ปัจจุบันในโปรแกรมจัดการไฟล์

⌨️ คีย์ลัด:
• Ctrl+Q: ออกจากโปรแกรม
• Ctrl+O: เปิดโฟลเดอร์ปัจจุบัน
• F1: แสดงหน้าต่างช่วยเหลือ
• F5: อัปเดตสถิติ

💡 เทคนิคการใช้งาน:
• สำหรับไฟล์ขนาดใหญ่ ควรแบ่งเป็นไฟล์ละ 1000-5000 บรรทัด
• ใช้ฟังก์ชัน "ตรวจสอบไฟล์" เพื่อดูข้อมูลก่อนแบ่ง
• สำหรับการแปล ควรติดตั้ง googletrans หรือ deep-translator
• ใช้การรีเฟรชอัตโนมัติเพื่อดูไฟล์ที่เปลี่ยนแปลงแบบเรียลไทม์
"""
        
        help_text.insert(tk.END, help_content)
        help_text.config(state='disabled')
        
        # Close button
        ttk.Button(
            help_window, 
            text="ปิด", 
            command=help_window.destroy
        ).pack(pady=10)
    
    def show_about(self) -> None:
        """แสดงข้อมูลเกี่ยวกับโปรแกรม"""
        about_text = f"""🔧 Text File Splitter & Merger v{APP_VERSION}

📝 เครื่องมือแบ่งและรวมไฟล์ข้อความ
พร้อมฟีเจอร์ดูไฟล์และแปลข้อความ

💻 พัฒนาด้วย Python และ Tkinter
📅 ปี 2024

🌟 ฟีเจอร์หลัก:
• แบ่งไฟล์ข้อความขนาดใหญ่
• รวมไฟล์ที่แบ่งแล้วกลับเข้าด้วยกัน
• ดูไฟล์ข้อความแบบเรียลไทม์
• แปลข้อความหลายภาษา
• จัดการไฟล์และโฟลเดอร์

💝 โปรแกรมนี้เป็น Open Source
สามารถใช้งานและปรับปรุงได้อย่างอิสระ"""
        
        messagebox.showinfo("เกี่ยวกับโปรแกรม", about_text)
    
    def run(self) -> None:
        """เริ่มต้นโปรแกรม"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nโปรแกรมถูกหยุดโดยผู้ใช้")
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดที่ไม่คาดคิด:\n{str(e)}")


def main():
    """ฟังก์ชันหลักสำหรับเริ่มต้นโปรแกรม"""
    
    # ตรวจสอบ Python version
    if sys.version_info < (3, 6):
        print("โปรแกรมนี้ต้องใช้ Python 3.6 หรือสูงกว่า")
        sys.exit(1)
    
    try:
        # สร้างและรันแอปพลิเคชัน
        app = MainApplication()
        app.update_status(STATUS_MESSAGES['ready'])
        app.run()
        
    except ImportError as e:
        error_msg = f"ไม่พบโมดูลที่จำเป็น: {str(e)}\n\n"
        error_msg += "กรุณาติดตั้งโมดูลที่จำเป็นดังนี้:\n"
        error_msg += "pip install -r requirements.txt"
        
        try:
            import tkinter.messagebox as mb
            mb.showerror("ข้อผิดพลาด", error_msg)
        except:
            print(error_msg)
        
        sys.exit(1)
    
    except Exception as e:
        error_msg = f"เกิดข้อผิดพลาดในการเริ่มต้นโปรแกรม:\n{str(e)}"
        
        try:
            import tkinter.messagebox as mb
            mb.showerror("ข้อผิดพลาด", error_msg)
        except:
            print(error_msg)
        
        sys.exit(1)


if __name__ == "__main__":
    main()
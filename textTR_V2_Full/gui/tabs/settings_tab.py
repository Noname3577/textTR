#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Settings Tab - GUI component for settings and tools
Tab สำหรับการตั้งค่าและเครื่องมือ
"""

import os
import glob
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from config.constants import EMOJIS
from utils.file_utils import format_file_size, open_file_manager


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
            json_files = glob.glob("*.json")
            part_files = glob.glob("*_part_*.txt")
            
            # นับโฟลเดอร์
            split_folders = [d for d in os.listdir(current_dir) 
                           if os.path.isdir(d) and '_split_' in d]
            
            # คำนวณขนาดไฟล์รวม
            total_size = 0
            file_count = 0
            
            for file_pattern in ["*.txt", "*.csv", "*.json", "*.log"]:
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
  • ไฟล์ .json: {len(json_files)} ไฟล์
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
            
            if not txt_files and not csv_files and not json_files:
                stats_text += "- ไม่พบไฟล์ข้อความ เริ่มต้นด้วยการเลือกไฟล์ในแท็บแบ่งไฟล์\n"
            
            # แสดงผลสถิติ
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, stats_text)
            
        except Exception as e:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, f"เกิดข้อผิดพลาดในการดึงสถิติ: {str(e)}")

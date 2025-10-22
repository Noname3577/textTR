#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Operations Module for Text File Splitter & Merger GUI
โมดูลการดำเนินการไฟล์สำหรับแอปพลิเคชัน GUI แบ่งและรวมไฟล์ข้อความ
"""

import os
import glob
import threading
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from gui_base import BaseTabComponent
from constants import (
    DEFAULT_LINES_PER_FILE, 
    DEFAULT_FILE_PATTERN, 
    EMOJIS, 
    STATUS_MESSAGES,
    SUPPORTED_FILE_TYPES
)
from utils import (
    get_file_info, 
    count_lines_in_file, 
    format_file_size,
    validate_file_path,
    validate_directory_path,
    safe_int_conversion
)
from text_splitter import split_text_file, merge_text_files


class FileSplitterTab(BaseTabComponent):
    """
    Tab สำหรับการแบ่งไฟล์ข้อความ
    """
    
    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        
        # ตัวแปรสำหรับเก็บค่าต่างๆ
        self.variables = {
            'input_file_path': tk.StringVar(),
            'lines_per_file': tk.IntVar(value=DEFAULT_LINES_PER_FILE),
            'create_folder': tk.BooleanVar(value=True),
            'output_folder': tk.StringVar()
        }
        
        self.create_widgets()
    
    def create_widgets(self) -> None:
        """สร้าง widgets สำหรับ tab แบ่งไฟล์"""
        
        # Main frame
        self.frame = ttk.Frame(self.parent)
        
        # Title
        title_label = ttk.Label(
            self.frame, 
            text=f"{EMOJIS['split']} แบ่งไฟล์ข้อความ", 
            style='Title.TLabel'
        )
        title_label.pack(pady=(10, 20))
        
        # File selection section
        self._create_file_selection_section()
        
        # Settings section
        self._create_settings_section()
        
        # Action buttons section
        self._create_action_buttons_section()
        
        # Progress bar
        self.widgets['progress'] = self.create_progress_bar(self.frame)
        self.widgets['progress'].pack(fill='x', padx=20, pady=(0, 10))
        
        # Results section
        self._create_results_section()
        
        # Status bar
        self.create_status_bar(self.frame)
    
    def _create_file_selection_section(self) -> None:
        """สร้างส่วนเลือกไฟล์"""
        file_frame = ttk.LabelFrame(self.frame, text=f"{EMOJIS['folder']} เลือกไฟล์", padding=10)
        file_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # Input file label
        ttk.Label(file_frame, text="ไฟล์ต้นฉบับ:").pack(anchor='w')
        
        # Input file entry and browse button
        input_frame = ttk.Frame(file_frame)
        input_frame.pack(fill='x', pady=(5, 10))
        
        self.widgets['input_entry'] = ttk.Entry(
            input_frame, 
            textvariable=self.variables['input_file_path'], 
            width=60
        )
        self.widgets['input_entry'].pack(side='left', fill='x', expand=True)
        
        self.widgets['browse_button'] = ttk.Button(
            input_frame, 
            text=f"{EMOJIS['folder']} เรียกดู", 
            command=self.browse_input_file
        )
        self.widgets['browse_button'].pack(side='right', padx=(5, 0))
        
        # Drag & Drop hint
        hint_label = ttk.Label(
            file_frame, 
            text=f"💡 คุณสามารถลากไฟล์มาวางที่นี่ได้", 
            style='Info.TLabel'
        )
        hint_label.pack(anchor='w')
    
    def _create_settings_section(self) -> None:
        """สร้างส่วนการตั้งค่า"""
        settings_frame = ttk.LabelFrame(self.frame, text=f"{EMOJIS['settings']} การตั้งค่า", padding=10)
        settings_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # Lines per file setting
        lines_frame = ttk.Frame(settings_frame)
        lines_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(lines_frame, text="จำนวนบรรทัดต่อไฟล์:").pack(side='left')
        
        self.widgets['lines_spinbox'] = ttk.Spinbox(
            lines_frame, 
            from_=1, 
            to=100000, 
            width=10, 
            textvariable=self.variables['lines_per_file']
        )
        self.widgets['lines_spinbox'].pack(side='left', padx=(10, 0))
        
        # Quick preset buttons
        preset_frame = ttk.Frame(lines_frame)
        preset_frame.pack(side='right')
        
        for value in [100, 500, 1000]:
            ttk.Button(
                preset_frame, 
                text=str(value), 
                width=5, 
                command=lambda v=value: self.variables['lines_per_file'].set(v)
            ).pack(side='left', padx=2)
        
        # Create folder option
        self.widgets['folder_checkbox'] = ttk.Checkbutton(
            settings_frame, 
            text=f"{EMOJIS['folder']} สร้างโฟลเดอร์ใหม่สำหรับเก็บไฟล์ที่แบ่ง", 
            variable=self.variables['create_folder']
        )
        self.widgets['folder_checkbox'].pack(anchor='w')
    
    def _create_action_buttons_section(self) -> None:
        """สร้างส่วนปุ่มดำเนินการ"""
        action_frame = ttk.Frame(self.frame)
        action_frame.pack(fill='x', padx=20, pady=10)
        
        self.widgets['split_button'] = ttk.Button(
            action_frame, 
            text=f"{EMOJIS['split']} แบ่งไฟล์", 
            command=self.start_split
        )
        self.widgets['split_button'].pack(side='left', padx=(0, 10))
        
        ttk.Button(
            action_frame, 
            text=f"{EMOJIS['clean']} ล้างค่า", 
            command=self.clear_form
        ).pack(side='left')
        
        ttk.Button(
            action_frame, 
            text=f"{EMOJIS['search']} ตรวจสอบไฟล์", 
            command=self.analyze_file
        ).pack(side='right')
    
    def _create_results_section(self) -> None:
        """สร้างส่วนแสดงผลลัพธ์"""
        results_frame = ttk.LabelFrame(self.frame, text=f"{EMOJIS['info']} ผลลัพธ์", padding=10)
        results_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))
        
        self.widgets['results_text'] = scrolledtext.ScrolledText(
            results_frame, 
            height=8, 
            wrap='word'
        )
        self.widgets['results_text'].pack(fill='both', expand=True)
    
    def browse_input_file(self) -> None:
        """เลือกไฟล์สำหรับแบ่ง"""
        filename = self.browse_file('open_text')
        if filename:
            self.variables['input_file_path'].set(filename)
            self.update_status(f"เลือกไฟล์: {os.path.basename(filename)}")
    
    def analyze_file(self) -> None:
        """วิเคราะห์ไฟล์และแนะนำการตั้งค่า"""
        file_path = self.variables['input_file_path'].get()
        
        if not self.validate_file_exists(file_path):
            return
        
        try:
            # ดึงข้อมูลไฟล์
            file_info = get_file_info(file_path)
            line_count = count_lines_in_file(file_path)
            
            # คำนวณจำนวนไฟล์ที่จะได้
            lines_per_file = self.variables['lines_per_file'].get()
            expected_files = (line_count + lines_per_file - 1) // lines_per_file if line_count > 0 else 0
            
            # แสดงผลการวิเคราะห์
            analysis_text = f"""📊 การวิเคราะห์ไฟล์

📄 ชื่อไฟล์: {os.path.basename(file_path)}
📏 ขนาดไฟล์: {file_info.get('size_formatted', 'ไม่ทราบ')}
📝 จำนวนบรรทัด: {line_count:,} บรรทัด
🔢 บรรทัดต่อไฟล์: {lines_per_file:,}
📁 ไฟล์ที่คาดว่าจะได้: {expected_files} ไฟล์

💡 คำแนะนำ:
"""
            
            # ให้คำแนะนำตามขนาดไฟล์
            if line_count < 100:
                analysis_text += "- ไฟล์นี้มีขนาดเล็ก อาจไม่จำเป็นต้องแบ่ง\n"
            elif line_count < 1000:
                analysis_text += "- แนะนำให้แบ่งไฟล์ละ 100-200 บรรทัด\n"
                self.variables['lines_per_file'].set(200)
            elif line_count < 10000:
                analysis_text += "- แนะนำให้แบ่งไฟล์ละ 500-1000 บรรทัด\n"
                self.variables['lines_per_file'].set(500)
            else:
                analysis_text += "- แนะนำให้แบ่งไฟล์ละ 1000-5000 บรรทัด\n"
                self.variables['lines_per_file'].set(2000)
            
            self.widgets['results_text'].delete(1.0, tk.END)
            self.widgets['results_text'].insert(tk.END, analysis_text)
            
            self.update_status(f"วิเคราะห์ไฟล์เสร็จสิ้น: {line_count:,} บรรทัด")
            
        except Exception as e:
            self.show_error(f"ไม่สามารถวิเคราะห์ไฟล์ได้: {str(e)}")
    
    def start_split(self) -> None:
        """เริ่มแบ่งไฟล์ในเทรดแยก"""
        if self.is_working():
            self.show_warning("กำลังดำเนินการอยู่ กรุณารอสักครู่")
            return
        
        # ตรวจสอบข้อมูล
        file_path = self.variables['input_file_path'].get()
        if not self.validate_file_exists(file_path):
            return
        
        lines_per_file = self.variables['lines_per_file'].get()
        if not self.validate_number_range(lines_per_file, 1, 100000, "จำนวนบรรทัดต่อไฟล์"):
            return
        
        # เริ่มการทำงาน
        self.set_working(True)
        self.widgets['split_button'].config(state='disabled')
        self.start_progress()
        
        # รันในเทรดแยก
        thread = threading.Thread(target=self._split_file_thread)
        thread.daemon = True
        thread.start()
    
    def _split_file_thread(self) -> None:
        """แบ่งไฟล์ในเทรดแยก"""
        try:
            file_path = self.variables['input_file_path'].get()
            lines_per_file = self.variables['lines_per_file'].get()
            create_folder = self.variables['create_folder'].get()
            
            # เรียกใช้ฟังก์ชันแบ่งไฟล์
            result = split_text_file(file_path, lines_per_file, create_folder=create_folder)
            output_files, output_dir = result
            
            # อัปเดต GUI ในเทรดหลัก
            self.parent.after(0, self._split_completed, output_files, output_dir, None)
            
        except Exception as e:
            self.parent.after(0, self._split_completed, None, None, str(e))
    
    def _split_completed(self, output_files: List[str], output_dir: str, error: str) -> None:
        """เรียกเมื่อแบ่งไฟล์เสร็จ"""
        self.set_working(False)
        self.widgets['split_button'].config(state='normal')
        self.stop_progress()
        
        if error:
            self.widgets['results_text'].delete(1.0, tk.END)
            self.widgets['results_text'].insert(tk.END, f"{EMOJIS['error']} เกิดข้อผิดพลาด: {error}")
            self.update_status(f"{EMOJIS['error']} แบ่งไฟล์ไม่สำเร็จ")
            self.show_error(f"ไม่สามารถแบ่งไฟล์ได้: {error}")
            return
        
        # แสดงผลลัพธ์
        result_text = f"{EMOJIS['success']} แบ่งไฟล์เสร็จสิ้น!\n\n"
        result_text += f"📊 สร้างไฟล์ทั้งหมด: {len(output_files)} ไฟล์\n"
        
        if output_dir:
            result_text += f"📁 โฟลเดอร์ผลลัพธ์: {os.path.basename(output_dir)}\n"
            result_text += f"📍 เส้นทาง: {output_dir}\n\n"
        
        result_text += "📄 ไฟล์ที่สร้าง:\n"
        for i, file_path in enumerate(output_files[:10], 1):  # แสดงแค่ 10 ไฟล์แรก
            result_text += f"{i:2d}. {os.path.basename(file_path)}\n"
        
        if len(output_files) > 10:
            result_text += f"... และอีก {len(output_files) - 10} ไฟล์"
        
        self.widgets['results_text'].delete(1.0, tk.END)
        self.widgets['results_text'].insert(tk.END, result_text)
        
        self.update_status(f"{EMOJIS['success']} แบ่งไฟล์สำเร็จ: {len(output_files)} ไฟล์")
        
        # แสดง notification
        self.show_success(f"แบ่งไฟล์เสร็จสิ้น!\nสร้างไฟล์ {len(output_files)} ไฟล์")
    
    def clear_form(self) -> None:
        """ล้างฟอร์มแบ่งไฟล์"""
        self.variables['input_file_path'].set("")
        self.widgets['results_text'].delete(1.0, tk.END)
        self.update_status(f"{EMOJIS['clean']} ล้างฟอร์มแบ่งไฟล์")


class FileMergerTab(BaseTabComponent):
    """
    Tab สำหรับการรวมไฟล์ข้อความ
    """
    
    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        
        # ตัวแปรสำหรับเก็บค่าต่างๆ
        self.variables = {
            'source_folder': tk.StringVar(),
            'merge_pattern': tk.StringVar(value=DEFAULT_FILE_PATTERN),
            'output_file_name': tk.StringVar()
        }
        
        self.create_widgets()
    
    def create_widgets(self) -> None:
        """สร้าง widgets สำหรับ tab รวมไฟล์"""
        
        # Main frame
        self.frame = ttk.Frame(self.parent)
        
        # Title
        title_label = ttk.Label(
            self.frame, 
            text=f"{EMOJIS['merge']} รวมไฟล์ข้อความ", 
            style='Title.TLabel'
        )
        title_label.pack(pady=(10, 20))
        
        # Source selection section
        self._create_source_selection_section()
        
        # Output settings section
        self._create_output_settings_section()
        
        # Action buttons section
        self._create_action_buttons_section()
        
        # Progress bar
        self.widgets['progress'] = self.create_progress_bar(self.frame)
        self.widgets['progress'].pack(fill='x', padx=20, pady=(0, 10))
        
        # Results section
        self._create_results_section()
        
        # Status bar
        self.create_status_bar(self.frame)
    
    def _create_source_selection_section(self) -> None:
        """สร้างส่วนเลือกแหล่งไฟล์"""
        source_frame = ttk.LabelFrame(self.frame, text=f"{EMOJIS['folder']} แหล่งไฟล์", padding=10)
        source_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # Source folder
        ttk.Label(source_frame, text="โฟลเดอร์ต้นทาง (ไม่ระบุ = โฟลเดอร์ปัจจุบัน):").pack(anchor='w')
        
        source_folder_frame = ttk.Frame(source_frame)
        source_folder_frame.pack(fill='x', pady=(5, 10))
        
        self.widgets['source_entry'] = ttk.Entry(
            source_folder_frame, 
            textvariable=self.variables['source_folder'], 
            width=60
        )
        self.widgets['source_entry'].pack(side='left', fill='x', expand=True)
        
        ttk.Button(
            source_folder_frame, 
            text=f"{EMOJIS['folder']} เรียกดู", 
            command=self.browse_source_folder
        ).pack(side='right', padx=(5, 0))
        
        # Auto-detect button
        auto_frame = ttk.Frame(source_frame)
        auto_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(
            auto_frame, 
            text=f"{EMOJIS['search']} ค้นหาโฟลเดอร์ที่แบ่งไว้", 
            command=self.find_split_folders
        ).pack(side='left')
        
        # File pattern
        ttk.Label(source_frame, text="รูปแบบชื่อไฟล์:").pack(anchor='w')
        
        pattern_frame = ttk.Frame(source_frame)
        pattern_frame.pack(fill='x', pady=(5, 0))
        
        self.widgets['pattern_entry'] = ttk.Entry(
            pattern_frame, 
            textvariable=self.variables['merge_pattern'], 
            width=40
        )
        self.widgets['pattern_entry'].pack(side='left', fill='x', expand=True)
        
        # Pattern presets
        preset_frame = ttk.Frame(pattern_frame)
        preset_frame.pack(side='right', padx=(10, 0))
        
        patterns = [
            ("*_part_*.txt", "*_part_*.txt"),
            ("*.txt", "*.txt"),
            ("*.csv", "*.csv")
        ]
        
        for label, pattern in patterns:
            ttk.Button(
                preset_frame, 
                text=label, 
                width=len(label), 
                command=lambda p=pattern: self.variables['merge_pattern'].set(p)
            ).pack(side='left', padx=2)
    
    def _create_output_settings_section(self) -> None:
        """สร้างส่วนการตั้งค่าไฟล์ผลลัพธ์"""
        output_frame = ttk.LabelFrame(self.frame, text=f"{EMOJIS['file']} ไฟล์ผลลัพธ์", padding=10)
        output_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ttk.Label(output_frame, text="ชื่อไฟล์ผลลัพธ์ (ไม่ระบุ = อัตโนมัติ):").pack(anchor='w')
        
        output_file_frame = ttk.Frame(output_frame)
        output_file_frame.pack(fill='x', pady=(5, 0))
        
        self.widgets['output_entry'] = ttk.Entry(
            output_file_frame, 
            textvariable=self.variables['output_file_name'], 
            width=60
        )
        self.widgets['output_entry'].pack(side='left', fill='x', expand=True)
        
        ttk.Button(
            output_file_frame, 
            text=f"{EMOJIS['save']} เลือกที่บันทึก", 
            command=self.browse_output_file
        ).pack(side='right', padx=(5, 0))
    
    def _create_action_buttons_section(self) -> None:
        """สร้างส่วนปุ่มดำเนินการ"""
        action_frame = ttk.Frame(self.frame)
        action_frame.pack(fill='x', padx=20, pady=10)
        
        self.widgets['merge_button'] = ttk.Button(
            action_frame, 
            text=f"{EMOJIS['merge']} รวมไฟล์", 
            command=self.start_merge
        )
        self.widgets['merge_button'].pack(side='left', padx=(0, 10))
        
        ttk.Button(
            action_frame, 
            text=f"{EMOJIS['clean']} ล้างค่า", 
            command=self.clear_form
        ).pack(side='left')
        
        ttk.Button(
            action_frame, 
            text=f"{EMOJIS['view']} ดูตัวอย่างไฟล์", 
            command=self.preview_files
        ).pack(side='right')
    
    def _create_results_section(self) -> None:
        """สร้างส่วนแสดงผลลัพธ์"""
        results_frame = ttk.LabelFrame(self.frame, text=f"{EMOJIS['info']} ผลลัพธ์", padding=10)
        results_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))
        
        self.widgets['results_text'] = scrolledtext.ScrolledText(
            results_frame, 
            height=8, 
            wrap='word'
        )
        self.widgets['results_text'].pack(fill='both', expand=True)
    
    def browse_source_folder(self) -> None:
        """เลือกโฟลเดอร์ต้นทางสำหรับรวมไฟล์"""
        folder = self.browse_folder()
        if folder:
            self.variables['source_folder'].set(folder)
            self.update_status(f"เลือกโฟลเดอร์: {os.path.basename(folder)}")
    
    def browse_output_file(self) -> None:
        """เลือกที่สำหรับบันทึกไฟล์ที่รวม"""
        filename = self.browse_file('save_text')
        if filename:
            self.variables['output_file_name'].set(filename)
            self.update_status(f"กำหนดไฟล์ผลลัพธ์: {os.path.basename(filename)}")
    
    def find_split_folders(self) -> None:
        """ค้นหาโฟลเดอร์ที่แบ่งไว้อัตโนมัติ"""
        current_dir = os.getcwd()
        split_folders = []
        
        for item in os.listdir(current_dir):
            if os.path.isdir(item) and '_split_' in item:
                split_folders.append(item)
        
        if not split_folders:
            self.widgets['results_text'].delete(1.0, tk.END)
            self.widgets['results_text'].insert(tk.END, f"{EMOJIS['warning']} ไม่พบโฟลเดอร์ที่แบ่งไว้")
            return
        
        # แสดงรายการโฟลเดอร์
        folder_list = "\n".join(f"📁 {folder}" for folder in split_folders)
        self.widgets['results_text'].delete(1.0, tk.END)
        self.widgets['results_text'].insert(tk.END, f"{EMOJIS['search']} พบโฟลเดอร์ที่แบ่งไว้:\n\n{folder_list}")
        
        # ใช้โฟลเดอร์ล่าสุด
        latest_folder = max(split_folders, key=lambda x: os.path.getmtime(x))
        self.variables['source_folder'].set(latest_folder)
        
        self.update_status(f"{EMOJIS['search']} พบ {len(split_folders)} โฟลเดอร์ ใช้ล่าสุด: {latest_folder}")
    
    def preview_files(self) -> None:
        """แสดงตัวอย่างไฟล์ที่จะรวม"""
        pattern = self.variables['merge_pattern'].get()
        source = self.variables['source_folder'].get()
        
        if source:
            search_path = os.path.join(source, pattern)
        else:
            search_path = pattern
        
        try:
            files = glob.glob(search_path)
            files.sort()
            
            if not files:
                self.widgets['results_text'].delete(1.0, tk.END)
                self.widgets['results_text'].insert(tk.END, f"{EMOJIS['warning']} ไม่พบไฟล์ที่ตรงกับรูปแบบ: {pattern}")
                return
            
            # แสดงรายการไฟล์
            preview_text = f"{EMOJIS['view']} พบไฟล์ที่จะรวม ({len(files)} ไฟล์):\n\n"
            
            for i, file_path in enumerate(files[:20], 1):  # แสดงแค่ 20 ไฟล์แรก
                file_info = get_file_info(file_path)
                preview_text += f"{i:2d}. {os.path.basename(file_path)} ({file_info.get('size_formatted', '?')})\n"
            
            if len(files) > 20:
                preview_text += f"... และอีก {len(files) - 20} ไฟล์\n"
            
            # คำนวณขนาดรวม
            total_size = sum(get_file_info(f).get('size', 0) for f in files)
            preview_text += f"\n📊 ขนาดรวม: {format_file_size(total_size)}"
            
            self.widgets['results_text'].delete(1.0, tk.END)
            self.widgets['results_text'].insert(tk.END, preview_text)
            
            self.update_status(f"{EMOJIS['view']} พบไฟล์ {len(files)} ไฟล์")
            
        except Exception as e:
            self.show_error(f"ไม่สามารถดูตัวอย่างไฟล์ได้: {str(e)}")
    
    def start_merge(self) -> None:
        """เริ่มรวมไฟล์ในเทรดแยก"""
        print("🔍 DEBUG - start_merge() called")
        
        if self.is_working():
            print("🔍 DEBUG - Already working, showing warning")
            self.show_warning("กำลังดำเนินการอยู่ กรุณารอสักครู่")
            return

        # ตรวจสอบข้อมูล
        pattern = self.variables['merge_pattern'].get()
        output_file = self.variables['output_file_name'].get().strip()
        print(f"🔍 DEBUG - Pattern from GUI: '{pattern}'")
        print(f"🔍 DEBUG - Output file from GUI: '{output_file}'")
        
        if not self.validate_required_field(pattern, "รูปแบบชื่อไฟล์"):
            print("🔍 DEBUG - Pattern validation failed")
            return
            
        if not output_file:
            print("🔍 DEBUG - Output file is empty, generating automatic name")
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"merged_text_{timestamp}.txt"
            self.variables['output_file_name'].set(output_file)
            self.update_status(f"สร้างชื่อไฟล์อัตโนมัติ: {output_file}")
            print(f"🔍 DEBUG - Auto-generated output file: '{output_file}'")        # ⚠️ ตรวจสอบ pattern ที่อาจก่อปัญหา
        if pattern == "*.txt":
            print("🔍 DEBUG - Pattern is '*.txt', showing warning dialog")
            warning_result = self.show_warning("⚠️ การใช้รูปแบบ '*.txt' อาจรวมไฟล์ที่ไม่ต้องการ (เช่น requirements.txt)\n\nแนะนำให้ใช้รูปแบบที่เฉพาะเจาะจงกว่า เช่น:\n- text_part_*.txt\n- *_part_*.txt\n\nต้องการดำเนินการต่อหรือไม่?")
            print(f"🔍 DEBUG - Warning dialog result: {warning_result}")
            if not warning_result:
                print("🔍 DEBUG - User chose NO, returning from function")
                return
        
        # ตรวจสอบว่ามีไฟล์ที่จะรวมหรือไม่
        source_folder = self.variables['source_folder'].get()
        if source_folder:
            if not os.path.exists(source_folder):
                self.show_error(f"ไม่พบโฟลเดอร์ต้นทาง: {source_folder}")
                return
            search_path = os.path.join(source_folder, pattern)
        else:
            search_path = pattern
        
        import glob
        matching_files = sorted(glob.glob(search_path))
        
        if not matching_files:
            error_msg = f"ไม่พบไฟล์ที่ตรงกับรูปแบบ: {pattern}"
            if source_folder:
                error_msg += f"\nในโฟลเดอร์: {source_folder}"
                # แสดงไฟล์ที่มีในโฟลเดอร์
                try:
                    available_files = [f for f in os.listdir(source_folder) if f.endswith('.txt')]
                    if available_files:
                        error_msg += f"\n\nไฟล์ .txt ที่มีอยู่ในโฟลเดอร์:\n" + "\n".join(f"- {f}" for f in available_files[:5])
                        if len(available_files) > 5:
                            error_msg += f"\n... และอีก {len(available_files) - 5} ไฟล์"
                except:
                    pass
            else:
                error_msg += "\nในโฟลเดอร์ปัจจุบัน"
            
            self.show_error(error_msg)
            return
        
        if len(matching_files) == 1 and matching_files[0].endswith('requirements.txt'):
            self.show_error("พบแต่ไฟล์ requirements.txt เท่านั้น\n\nกรุณาตรวจสอบ:\n1. รูปแบบชื่อไฟล์ (Pattern)\n2. โฟลเดอร์ต้นทาง (Source Folder)")
            return
        
        # แสดงสรุปไฟล์ที่จะรวม
        file_summary = f"พร้อมรวมไฟล์ {len(matching_files)} ไฟล์:\n"
        for i, f in enumerate(matching_files[:5], 1):
            file_summary += f"{i}. {os.path.basename(f)}\n"
        if len(matching_files) > 5:
            file_summary += f"... และอีก {len(matching_files) - 5} ไฟล์"
        
        # ขอการยืนยัน
        print("🔍 DEBUG - Showing confirmation dialog")
        confirmation_result = self.show_warning(f"{file_summary}\n\nต้องการดำเนินการรวมไฟล์หรือไม่?")
        print(f"🔍 DEBUG - Confirmation dialog result: {confirmation_result}")
        if not confirmation_result:
            print("🔍 DEBUG - User cancelled, returning from function")
            return
        
        # เริ่มการทำงาน
        print("🔍 DEBUG - Starting merge process...")
        self.set_working(True)
        self.widgets['merge_button'].config(state='disabled')
        self.start_progress()

        # รันในเทรดแยก
        print("🔍 DEBUG - Creating merge thread...")
        thread = threading.Thread(target=self._merge_file_thread)
        thread.daemon = True
        thread.start()
    
    def _merge_file_thread(self) -> None:
        """รวมไฟล์ในเทรดแยก"""
        try:
            pattern = self.variables['merge_pattern'].get()
            source_folder = self.variables['source_folder'].get()
            output_file = self.variables['output_file_name'].get()
            
            # 🔍 Debug logging
            print(f"🔍 DEBUG - Merge parameters:")
            print(f"   Pattern: '{pattern}'")
            print(f"   Source folder: '{source_folder}'")
            print(f"   Output file: '{output_file}'")
            
            # ตรวจสอบไฟล์ก่อนรวม
            import glob
            if source_folder:
                search_path = os.path.join(source_folder, pattern)
            else:
                search_path = pattern
            
            matching_files = sorted(glob.glob(search_path))
            print(f"   🔍 Search path: '{search_path}'")
            print(f"   📄 Found {len(matching_files)} files:")
            for f in matching_files[:3]:
                print(f"      - {f}")
            
            # เรียกใช้ฟังก์ชันรวมไฟล์ (ลำดับ parameter ที่ถูกต้อง)
            result_file = merge_text_files(pattern, output_file, source_folder)
            print(f"   ✅ Result from merge_text_files: '{result_file}'")
            
            # อัปเดต GUI ในเทรดหลัก
            self.parent.after(0, self._merge_completed, result_file, None)
            
        except FileNotFoundError as e:
            # ข้อผิดพลาดเฉพาะการหาไฟล์ไม่เจอ
            error_msg = f"ไม่พบไฟล์ที่ตรงกับเงื่อนไข: {str(e)}"
            self.parent.after(0, self._merge_completed, None, error_msg)
        except Exception as e:
            # ข้อผิดพลาดอื่นๆ
            error_msg = f"เกิดข้อผิดพลาดในการรวมไฟล์: {str(e)}"
            self.parent.after(0, self._merge_completed, None, error_msg)
    
    def _merge_completed(self, result_file: str, error: str) -> None:
        """เรียกเมื่อรวมไฟล์เสร็จ"""
        self.set_working(False)
        self.widgets['merge_button'].config(state='normal')
        self.stop_progress()
        
        if error or result_file is None:
            error_msg = error or "ไม่สามารถรวมไฟล์ได้ (result_file is None)"
            self.widgets['results_text'].delete(1.0, tk.END)
            self.widgets['results_text'].insert(tk.END, f"{EMOJIS['error']} เกิดข้อผิดพลาด: {error_msg}")
            self.update_status(f"{EMOJIS['error']} รวมไฟล์ไม่สำเร็จ")
            self.show_error(f"ไม่สามารถรวมไฟล์ได้: {error_msg}")
            return
        
        # แสดงผลลัพธ์
        try:
            if not os.path.exists(result_file):
                raise FileNotFoundError(f"ไม่พบไฟล์ผลลัพธ์: {result_file}")
                
            file_info = get_file_info(result_file)
            line_count = count_lines_in_file(result_file)
            
            result_text = f"{EMOJIS['success']} รวมไฟล์เสร็จสิ้น!\n\n"
            result_text += f"📄 ไฟล์ผลลัพธ์: {os.path.basename(result_file)}\n"
            result_text += f"📍 เส้นทาง: {result_file}\n"
            result_text += f"📏 ขนาดไฟล์: {file_info.get('size_formatted', 'ไม่ทราบ')}\n"
            result_text += f"📝 จำนวนบรรทัด: {line_count:,} บรรทัด"
            
        except Exception as e:
            # Fallback เมื่อไม่สามารถดึงข้อมูลไฟล์ได้
            result_text = f"{EMOJIS['success']} รวมไฟล์เสร็จสิ้น!\n\n"
            if result_file and os.path.exists(result_file):
                result_text += f"📄 ไฟล์ผลลัพธ์: {os.path.basename(result_file)}\n"
                result_text += f"📍 เส้นทาง: {result_file}"
            else:
                result_text += f"⚠️ ไม่สามารถแสดงรายละเอียดไฟล์ได้: {str(e)}"
        
        self.widgets['results_text'].delete(1.0, tk.END)
        self.widgets['results_text'].insert(tk.END, result_text)
        
        # อัปเดต status ด้วยการตรวจสอบความปลอดภัย
        if result_file and os.path.exists(result_file):
            self.update_status(f"{EMOJIS['success']} รวมไฟล์สำเร็จ: {os.path.basename(result_file)}")
        else:
            self.update_status(f"{EMOJIS['success']} รวมไฟล์เสร็จสิ้น")
        
        # แสดง notification
        self.show_success(f"รวมไฟล์เสร็จสิ้น!\nไฟล์ผลลัพธ์: {os.path.basename(result_file)}")
    
    def clear_form(self) -> None:
        """ล้างฟอร์มรวมไฟล์"""
        self.variables['source_folder'].set("")
        self.variables['output_file_name'].set("")
        self.widgets['results_text'].delete(1.0, tk.END)
        self.update_status(f"{EMOJIS['clean']} ล้างฟอร์มรวมไฟล์")
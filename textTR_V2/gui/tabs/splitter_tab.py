#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Splitter Tab - GUI component for splitting text files
Tab สำหรับแบ่งไฟล์ข้อความ
"""

import os
import threading
from typing import List
import tkinter as tk
from tkinter import ttk, scrolledtext

from gui.base import BaseTabComponent
from config.constants import (
    DEFAULT_LINES_PER_FILE, 
    EMOJIS, 
    STATUS_MESSAGES
)
from utils.file_utils import (
    get_file_info, 
    count_lines_in_file, 
    validate_file_path
)
from core.text_splitter import split_text_file


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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Merger Tab - GUI component for merging text files
Tab สำหรับรวมไฟล์ข้อความ
"""

import os
import glob
import threading
from typing import List
import tkinter as tk
from tkinter import ttk, scrolledtext

from gui.base import BaseTabComponent
from config.constants import (
    DEFAULT_FILE_PATTERN, 
    EMOJIS
)
from utils.file_utils import (
    get_file_info, 
    count_lines_in_file,
    format_file_size
)
from core.text_splitter import merge_text_files


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
        if self.is_working():
            self.show_warning("กำลังดำเนินการอยู่ กรุณารอสักครู่")
            return

        # ตรวจสอบข้อมูล
        pattern = self.variables['merge_pattern'].get()
        output_file = self.variables['output_file_name'].get().strip()
        
        if not self.validate_required_field(pattern, "รูปแบบชื่อไฟล์"):
            return
            
        if not output_file:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"merged_text_{timestamp}.txt"
            self.variables['output_file_name'].set(output_file)
            self.update_status(f"สร้างชื่อไฟล์อัตโนมัติ: {output_file}")
        
        # ตรวจสอบ pattern ที่อาจก่อปัญหา
        if pattern == "*.txt":
            warning_result = self.show_warning(
                "⚠️ การใช้รูปแบบ '*.txt' อาจรวมไฟล์ที่ไม่ต้องการ\n\n"
                "แนะนำให้ใช้รูปแบบที่เฉพาะเจาะจงกว่า เช่น:\n"
                "- text_part_*.txt\n"
                "- *_part_*.txt\n\n"
                "ต้องการดำเนินการต่อหรือไม่?"
            )
            if not warning_result:
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
        
        matching_files = sorted(glob.glob(search_path))
        
        if not matching_files:
            self.show_error(f"ไม่พบไฟล์ที่ตรงกับรูปแบบ: {pattern}")
            return
        
        # แสดงสรุปและขอยืนยัน
        file_summary = f"พร้อมรวมไฟล์ {len(matching_files)} ไฟล์:\n"
        for i, f in enumerate(matching_files[:5], 1):
            file_summary += f"{i}. {os.path.basename(f)}\n"
        if len(matching_files) > 5:
            file_summary += f"... และอีก {len(matching_files) - 5} ไฟล์"
        
        confirmation_result = self.show_warning(f"{file_summary}\n\nต้องการดำเนินการรวมไฟล์หรือไม่?")
        if not confirmation_result:
            return
        
        # เริ่มการทำงาน
        self.set_working(True)
        self.widgets['merge_button'].config(state='disabled')
        self.start_progress()

        # รันในเทรดแยก
        thread = threading.Thread(target=self._merge_file_thread)
        thread.daemon = True
        thread.start()
    
    def _merge_file_thread(self) -> None:
        """รวมไฟล์ในเทรดแยก"""
        try:
            pattern = self.variables['merge_pattern'].get()
            source_folder = self.variables['source_folder'].get()
            output_file = self.variables['output_file_name'].get()
            
            # เรียกใช้ฟังก์ชันรวมไฟล์
            result_file = merge_text_files(pattern, output_file, source_folder)
            
            # อัปเดต GUI ในเทรดหลัก
            self.parent.after(0, self._merge_completed, result_file, None)
            
        except FileNotFoundError as e:
            error_msg = f"ไม่พบไฟล์ที่ตรงกับเงื่อนไข: {str(e)}"
            self.parent.after(0, self._merge_completed, None, error_msg)
        except Exception as e:
            error_msg = f"เกิดข้อผิดพลาดในการรวมไฟล์: {str(e)}"
            self.parent.after(0, self._merge_completed, None, error_msg)
    
    def _merge_completed(self, result_file: str, error: str) -> None:
        """เรียกเมื่อรวมไฟล์เสร็จ"""
        self.set_working(False)
        self.widgets['merge_button'].config(state='normal')
        self.stop_progress()
        
        if error or result_file is None:
            error_msg = error or "ไม่สามารถรวมไฟล์ได้"
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
            result_text = f"{EMOJIS['success']} รวมไฟล์เสร็จสิ้น!\n\n"
            if result_file and os.path.exists(result_file):
                result_text += f"📄 ไฟล์ผลลัพธ์: {os.path.basename(result_file)}\n"
                result_text += f"📍 เส้นทาง: {result_file}"
            else:
                result_text += f"⚠️ ไม่สามารถแสดงรายละเอียดไฟล์ได้: {str(e)}"
        
        self.widgets['results_text'].delete(1.0, tk.END)
        self.widgets['results_text'].insert(tk.END, result_text)
        
        if result_file and os.path.exists(result_file):
            self.update_status(f"{EMOJIS['success']} รวมไฟล์สำเร็จ: {os.path.basename(result_file)}")
        else:
            self.update_status(f"{EMOJIS['success']} รวมไฟล์เสร็จสิ้น")
        
        self.show_success(f"รวมไฟล์เสร็จสิ้น!\nไฟล์ผลลัพธ์: {os.path.basename(result_file)}")
    
    def clear_form(self) -> None:
        """ล้างฟอร์มรวมไฟล์"""
        self.variables['source_folder'].set("")
        self.variables['output_file_name'].set("")
        self.widgets['results_text'].delete(1.0, tk.END)
        self.update_status(f"{EMOJIS['clean']} ล้างฟอร์มรวมไฟล์")

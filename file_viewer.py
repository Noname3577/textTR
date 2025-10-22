#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Viewer Module for Text File Splitter & Merger GUI
โมดูลดูไฟล์สำหรับแอปพลิเคชัน GUI แบ่งและรวมไฟล์ข้อความ
"""

import os
import threading
import time
from typing import List, Optional
import tkinter as tk
from tkinter import ttk, scrolledtext

from gui_base import BaseTabComponent
from constants import (
    EMOJIS,
    AUTO_REFRESH_INTERVAL,
    MAX_DISPLAY_LINES,
    MAX_FILE_SIZE_FOR_AUTO_REFRESH
)
from utils import (
    get_file_info,
    count_lines_in_file,
    read_file_lines,
    validate_file_path,
    format_file_size,
    format_timestamp
)


class FileViewerTab(BaseTabComponent):
    """
    Tab สำหรับการดูไฟล์ข้อความแบบเรียลไทม์
    """
    
    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        
        # ตัวแปรสำหรับเก็บค่าต่างๆ
        self.variables = {
            'file_path': tk.StringVar(),
            'auto_refresh': tk.BooleanVar(value=False),
            'current_line': tk.IntVar(value=0),
            'total_lines': tk.IntVar(value=0)
        }
        
        # ข้อมูลไฟล์
        self.file_lines: List[str] = []
        self.last_modified_time = 0
        self.refresh_job: Optional[str] = None
        
        self.create_widgets()
    
    def create_widgets(self) -> None:
        """สร้าง widgets สำหรับ tab ดูไฟล์"""
        
        # Main frame
        self.frame = ttk.Frame(self.parent)
        
        # Title
        title_label = ttk.Label(
            self.frame, 
            text=f"{EMOJIS['view']} ดูไฟล์ข้อความแบบเรียลไทม์", 
            style='Title.TLabel'
        )
        title_label.pack(pady=(10, 20))
        
        # File selection section
        self._create_file_selection_section()
        
        # File info section
        self._create_file_info_section()
        
        # Navigation section
        self._create_navigation_section()
        
        # Content display section
        self._create_content_section()
        
        # Current line display section
        self._create_current_line_section()
        
        # Status bar
        self.create_status_bar(self.frame)
    
    def _create_file_selection_section(self) -> None:
        """สร้างส่วนเลือกไฟล์"""
        file_frame = ttk.LabelFrame(self.frame, text=f"{EMOJIS['folder']} เลือกไฟล์", padding=10)
        file_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # File path label
        ttk.Label(file_frame, text="ไฟล์ข้อความที่ต้องการดู:").pack(anchor='w')
        
        # File input frame
        file_input_frame = ttk.Frame(file_frame)
        file_input_frame.pack(fill='x', pady=(5, 10))
        
        self.widgets['file_entry'] = ttk.Entry(
            file_input_frame, 
            textvariable=self.variables['file_path'], 
            width=60
        )
        self.widgets['file_entry'].pack(side='left', fill='x', expand=True)
        
        ttk.Button(
            file_input_frame, 
            text=f"{EMOJIS['folder']} เรียกดู", 
            command=self.browse_viewer_file
        ).pack(side='right', padx=(5, 0))
        
        # Options frame
        options_frame = ttk.Frame(file_frame)
        options_frame.pack(fill='x', pady=(0, 10))
        
        self.widgets['auto_refresh_check'] = ttk.Checkbutton(
            options_frame, 
            text=f"{EMOJIS['refresh']} รีเฟรชอัตโนมัติทุก 2 วินาที", 
            variable=self.variables['auto_refresh'], 
            command=self.toggle_auto_refresh
        )
        self.widgets['auto_refresh_check'].pack(side='left')
        
        ttk.Button(
            options_frame, 
            text=f"{EMOJIS['refresh']} รีเฟรชทันที", 
            command=self.refresh_viewer
        ).pack(side='right')
    
    def _create_file_info_section(self) -> None:
        """สร้างส่วนแสดงข้อมูลไฟล์"""
        info_frame = ttk.LabelFrame(self.frame, text=f"{EMOJIS['info']} ข้อมูลไฟล์", padding=10)
        info_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        self.widgets['file_info'] = tk.Text(
            info_frame, 
            height=3, 
            wrap='word', 
            state='disabled',
            bg='#f5f5f5'
        )
        self.widgets['file_info'].pack(fill='x')
    
    def _create_navigation_section(self) -> None:
        """สร้างส่วนนำทาง"""
        nav_frame = ttk.LabelFrame(self.frame, text=f"{EMOJIS['navigation']['first']} การนำทาง", padding=10)
        nav_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # Navigation controls
        nav_controls = ttk.Frame(nav_frame)
        nav_controls.pack(fill='x')
        
        ttk.Label(nav_controls, text="นำทาง:").pack(side='left')
        
        ttk.Button(
            nav_controls, 
            text=f"{EMOJIS['navigation']['first']} แรก", 
            command=self.goto_first_line
        ).pack(side='left', padx=(10, 2))
        
        ttk.Button(
            nav_controls, 
            text=f"{EMOJIS['navigation']['prev']} ก่อนหน้า", 
            command=self.goto_prev_line
        ).pack(side='left', padx=2)
        
        # Line info
        self.widgets['line_info'] = ttk.Label(nav_controls, text="0 / 0")
        self.widgets['line_info'].pack(side='left', padx=(10, 10))
        
        ttk.Button(
            nav_controls, 
            text=f"{EMOJIS['navigation']['next']} ถัดไป", 
            command=self.goto_next_line
        ).pack(side='left', padx=2)
        
        ttk.Button(
            nav_controls, 
            text=f"{EMOJIS['navigation']['last']} สุดท้าย", 
            command=self.goto_last_line
        ).pack(side='left', padx=(2, 10))
        
        # Jump to line
        ttk.Label(nav_controls, text="ไปที่บรรทัดที่:").pack(side='left', padx=(20, 5))
        
        self.widgets['jump_entry'] = ttk.Entry(nav_controls, width=8)
        self.widgets['jump_entry'].pack(side='left', padx=(0, 5))
        
        ttk.Button(
            nav_controls, 
            text=f"{EMOJIS['navigation']['jump']} ไป", 
            command=self.jump_to_line
        ).pack(side='left')
        
        # Bind Enter key for jump
        self.widgets['jump_entry'].bind('<Return>', lambda e: self.jump_to_line())
    
    def _create_content_section(self) -> None:
        """สร้างส่วนแสดงเนื้อหา"""
        content_frame = ttk.LabelFrame(
            self.frame, 
            text=f"{EMOJIS['file']} เนื้อหาไฟล์ (แยกทีละบรรทัด)", 
            padding=10
        )
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))
        
        self.widgets['content_text'] = scrolledtext.ScrolledText(
            content_frame, 
            height=15, 
            wrap='word', 
            state='disabled'
        )
        self.widgets['content_text'].pack(fill='both', expand=True)
    
    def _create_current_line_section(self) -> None:
        """สร้างส่วนแสดงบรรทัดปัจจุบัน"""
        current_frame = ttk.LabelFrame(self.frame, text=f"{EMOJIS['edit']} บรรทัดปัจจุบัน", padding=10)
        current_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        self.widgets['current_line_text'] = tk.Text(
            current_frame, 
            height=3, 
            wrap='word',
            bg='#ffffcc'
        )
        self.widgets['current_line_text'].pack(fill='x')
    
    # === File Operations ===
    
    def browse_viewer_file(self) -> None:
        """เลือกไฟล์สำหรับดู"""
        filename = self.browse_file('open_text')
        if filename:
            self.variables['file_path'].set(filename)
            self.load_file_for_viewing()
    
    def load_file_for_viewing(self) -> None:
        """โหลดไฟล์สำหรับดู"""
        file_path = self.variables['file_path'].get()
        
        if not self.validate_file_exists(file_path):
            return
        
        try:
            # โหลดบรรทัดจากไฟล์
            self.file_lines = read_file_lines(file_path, MAX_DISPLAY_LINES)
            
            # อัปเดตข้อมูลไฟล์
            self.update_file_info()
            
            # แสดงเนื้อหาทั้งหมด
            self.display_all_content()
            
            # ไปที่บรรทัดแรก
            self.variables['current_line'].set(0)
            self.variables['total_lines'].set(len(self.file_lines))
            self.display_current_line()
            
            # อัปเดตสถานะ
            self.update_status(f"โหลดไฟล์สำเร็จ: {len(self.file_lines):,} บรรทัด")
            
        except Exception as e:
            self.show_error(f"ไม่สามารถโหลดไฟล์ได้: {str(e)}")
    
    def update_file_info(self) -> None:
        """อัปเดตข้อมูลไฟล์"""
        file_path = self.variables['file_path'].get()
        
        if not validate_file_path(file_path):
            return
        
        try:
            # ดึงข้อมูลไฟล์
            file_info = get_file_info(file_path)
            line_count = count_lines_in_file(file_path)
            
            # สร้างข้อความแสดงข้อมูล
            info_text = f"""📄 ชื่อไฟล์: {os.path.basename(file_path)}
📏 ขนาด: {file_info.get('size_formatted', 'ไม่ทราบ')} ({file_info.get('size', 0):,} ไบต์)
📝 จำนวนบรรทัด: {line_count:,} บรรทัด
🕒 แก้ไขล่าสุด: {file_info.get('modified_formatted', 'ไม่ทราบ')}"""
            
            # แสดงข้อมูล
            self.widgets['file_info'].config(state='normal')
            self.widgets['file_info'].delete(1.0, tk.END)
            self.widgets['file_info'].insert(tk.END, info_text)
            self.widgets['file_info'].config(state='disabled')
            
            # อัปเดตเวลาแก้ไข
            self.last_modified_time = file_info.get('modified', 0)
            
        except Exception as e:
            self.widgets['file_info'].config(state='normal')
            self.widgets['file_info'].delete(1.0, tk.END)
            self.widgets['file_info'].insert(tk.END, f"ไม่สามารถดึงข้อมูลไฟล์ได้: {str(e)}")
            self.widgets['file_info'].config(state='disabled')
    
    def display_all_content(self) -> None:
        """แสดงเนื้อหาทั้งหมดของไฟล์"""
        if not self.file_lines:
            return
        
        self.widgets['content_text'].config(state='normal')
        self.widgets['content_text'].delete(1.0, tk.END)
        
        for i, line in enumerate(self.file_lines, 1):
            self.widgets['content_text'].insert(tk.END, f"{i:4d}: {line}")
        
        self.widgets['content_text'].config(state='disabled')
    
    def display_current_line(self) -> None:
        """แสดงบรรทัดปัจจุบัน"""
        if not self.file_lines:
            return
        
        current_index = self.variables['current_line'].get()
        total_lines = len(self.file_lines)
        
        # อัปเดตข้อมูลบรรทัด
        self.widgets['line_info'].config(text=f"{current_index + 1} / {total_lines}")
        
        if 0 <= current_index < total_lines:
            # แสดงบรรทัดปัจจุบัน
            current_line = self.file_lines[current_index]
            
            self.widgets['current_line_text'].delete(1.0, tk.END)
            self.widgets['current_line_text'].insert(
                tk.END, 
                f"บรรทัดที่ {current_index + 1}: {current_line}"
            )
            
            # เลื่อนไปที่บรรทัดใน content view
            self._scroll_to_line(current_index)
    
    def _scroll_to_line(self, line_index: int) -> None:
        """เลื่อนไปที่บรรทัดที่กำหนดใน content view"""
        if not self.file_lines:
            return
        
        total_lines = len(self.file_lines)
        if 0 <= line_index < total_lines:
            # คำนวณตำแหน่ง (เป็นสัดส่วน)
            fraction = line_index / total_lines if total_lines > 0 else 0
            
            # เลื่อนไปที่ตำแหน่งนั้น
            self.widgets['content_text'].yview_moveto(fraction)
    
    # === Navigation Operations ===
    
    def goto_next_line(self) -> None:
        """ไปบรรทัดถัดไป"""
        current = self.variables['current_line'].get()
        total = len(self.file_lines)
        
        if current < total - 1:
            self.variables['current_line'].set(current + 1)
            self.display_current_line()
    
    def goto_prev_line(self) -> None:
        """ไปบรรทัดก่อนหน้า"""
        current = self.variables['current_line'].get()
        
        if current > 0:
            self.variables['current_line'].set(current - 1)
            self.display_current_line()
    
    def goto_first_line(self) -> None:
        """ไปบรรทัดแรก"""
        if self.file_lines:
            self.variables['current_line'].set(0)
            self.display_current_line()
    
    def goto_last_line(self) -> None:
        """ไปบรรทัดสุดท้าย"""
        if self.file_lines:
            self.variables['current_line'].set(len(self.file_lines) - 1)
            self.display_current_line()
    
    def goto_line(self, line_number: int) -> None:
        """ไปยังบรรทัดที่กำหนด (1-based)"""
        if not self.file_lines:
            return
        
        line_index = line_number - 1  # แปลงเป็น 0-based
        total_lines = len(self.file_lines)
        
        if 0 <= line_index < total_lines:
            self.variables['current_line'].set(line_index)
            self.display_current_line()
        else:
            self.show_error(f"หมายเลขบรรทัดต้องอยู่ระหว่าง 1-{total_lines}")
    
    def jump_to_line(self) -> None:
        """กระโดดไปยังบรรทัดที่กำหนด"""
        try:
            line_number = int(self.widgets['jump_entry'].get())
            self.goto_line(line_number)
            
            # ล้างช่องกรอก
            self.widgets['jump_entry'].delete(0, tk.END)
            
        except ValueError:
            self.show_error("กรุณาใส่หมายเลขบรรทัดที่ถูกต้อง")
    
    # === Auto Refresh Operations ===
    
    def toggle_auto_refresh(self) -> None:
        """เปิด/ปิดการรีเฟรชอัตโนมัติ"""
        if self.variables['auto_refresh'].get():
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()
    
    def start_auto_refresh(self) -> None:
        """เริ่มการรีเฟรชอัตโนมัติ"""
        if self.refresh_job:
            self.frame.after_cancel(self.refresh_job)
        
        self.refresh_viewer()
        self.refresh_job = self.frame.after(AUTO_REFRESH_INTERVAL, self.start_auto_refresh)
        
        self.update_status(f"{EMOJIS['refresh']} เปิดการรีเฟรชอัตโนมัติ")
    
    def stop_auto_refresh(self) -> None:
        """หยุดการรีเฟรชอัตโนมัติ"""
        if self.refresh_job:
            self.frame.after_cancel(self.refresh_job)
            self.refresh_job = None
        
        self.update_status(f"{EMOJIS['info']} ปิดการรีเฟรชอัตโนมัติ")
    
    def refresh_viewer(self) -> None:
        """รีเฟรชการดูไฟล์"""
        file_path = self.variables['file_path'].get()
        
        if not validate_file_path(file_path):
            return
        
        try:
            # ตรวจสอบว่าไฟล์มีการเปลี่ยนแปลงหรือไม่
            file_info = get_file_info(file_path)
            current_modified_time = file_info.get('modified', 0)
            
            if current_modified_time != self.last_modified_time:
                # ไฟล์มีการเปลี่ยนแปลง - โหลดใหม่
                current_line = self.variables['current_line'].get()
                
                # โหลดไฟล์ใหม่
                self.load_file_for_viewing()
                
                # กลับไปที่บรรทัดเดิม (ถ้าเป็นไปได้)
                if current_line < len(self.file_lines):
                    self.variables['current_line'].set(current_line)
                    self.display_current_line()
                
                self.update_status(f"{EMOJIS['refresh']} ไฟล์มีการเปลี่ยนแปลง - รีเฟรชแล้ว")
            else:
                # ไฟล์ไม่เปลี่ยนแปลง
                if self.variables['auto_refresh'].get():
                    self.update_status(f"{EMOJIS['success']} ไฟล์ไม่มีการเปลี่ยนแปลง")
                else:
                    self.update_status(f"{EMOJIS['refresh']} รีเฟรชเสร็จสิ้น")
            
        except Exception as e:
            self.show_error(f"การรีเฟรชล้มเหลว: {str(e)}")
    
    # === Utility Methods ===
    
    def clear_viewer(self) -> None:
        """ล้างการแสดงผล"""
        self.file_lines = []
        self.variables['current_line'].set(0)
        self.variables['total_lines'].set(0)
        
        # ล้าง widgets
        widgets_to_clear = ['content_text', 'current_line_text', 'file_info']
        
        for widget_name in widgets_to_clear:
            widget = self.widgets.get(widget_name)
            if widget:
                if hasattr(widget, 'config'):
                    widget.config(state='normal')
                    widget.delete(1.0, tk.END)
                    if widget_name in ['content_text', 'file_info']:
                        widget.config(state='disabled')
        
        # อัปเดตข้อมูลบรรทัด
        self.widgets['line_info'].config(text="0 / 0")
        
        # หยุดการรีเฟรชอัตโนมัติ
        if self.variables['auto_refresh'].get():
            self.variables['auto_refresh'].set(False)
            self.stop_auto_refresh()
        
        self.update_status(f"{EMOJIS['clean']} ล้างการแสดงผลแล้ว")
    
    def get_file_statistics(self) -> dict:
        """ดึงสถิติของไฟล์ปัจจุบัน"""
        if not self.file_lines:
            return {}
        
        file_path = self.variables['file_path'].get()
        
        stats = {
            'file_path': file_path,
            'total_lines': len(self.file_lines),
            'current_line': self.variables['current_line'].get() + 1,
            'empty_lines': sum(1 for line in self.file_lines if not line.strip()),
            'non_empty_lines': sum(1 for line in self.file_lines if line.strip()),
        }
        
        if validate_file_path(file_path):
            file_info = get_file_info(file_path)
            stats.update({
                'file_size': file_info.get('size', 0),
                'file_size_formatted': file_info.get('size_formatted', 'ไม่ทราบ'),
                'modified_time': file_info.get('modified_formatted', 'ไม่ทราบ')
            })
        
        return stats
    
    def export_current_view(self) -> None:
        """ส่งออกมุมมองปัจจุบัน"""
        if not self.file_lines:
            self.show_error("ไม่มีไฟล์ที่จะส่งออก")
            return
        
        filename = self.browse_file('save_text')
        if not filename:
            return
        
        try:
            # เตรียมข้อมูลสำหรับส่งออก
            export_lines = []
            
            for i, line in enumerate(self.file_lines, 1):
                export_lines.append(f"{i:4d}: {line}")
            
            # เขียนลงไฟล์
            from utils import write_file_lines
            if write_file_lines(filename, export_lines):
                self.show_success(f"ส่งออกไฟล์สำเร็จ: {os.path.basename(filename)}")
            else:
                self.show_error("การส่งออกล้มเหลว")
                
        except Exception as e:
            self.show_error(f"การส่งออกล้มเหลว: {str(e)}")


class FileComparisonDialog(tk.Toplevel):
    """
    Dialog สำหรับเปรียบเทียบไฟล์ (เสริม)
    """
    
    def __init__(self, parent: tk.Tk, file1: str, file2: str):
        super().__init__(parent)
        
        self.file1 = file1
        self.file2 = file2
        
        self.title("เปรียบเทียบไฟล์")
        self.geometry("800x600")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.load_files()
    
    def create_widgets(self) -> None:
        """สร้าง widgets สำหรับ dialog"""
        
        # Title
        title_label = ttk.Label(
            self, 
            text="🔍 เปรียบเทียบไฟล์", 
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=10)
        
        # File info frame
        info_frame = ttk.Frame(self)
        info_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # File 1 info
        ttk.Label(info_frame, text=f"ไฟล์ที่ 1: {os.path.basename(self.file1)}", 
                 style='Section.TLabel').pack(anchor='w')
        
        # File 2 info  
        ttk.Label(info_frame, text=f"ไฟล์ที่ 2: {os.path.basename(self.file2)}", 
                 style='Section.TLabel').pack(anchor='w')
        
        # Comparison result frame
        result_frame = ttk.Frame(self)
        result_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Create text widget for showing differences
        self.result_text = scrolledtext.ScrolledText(
            result_frame, 
            height=20, 
            wrap='word'
        )
        self.result_text.pack(fill='both', expand=True)
        
        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="ปิด", command=self.destroy).pack(side='right')
    
    def load_files(self) -> None:
        """โหลดและเปรียบเทียบไฟล์"""
        try:
            # โหลดไฟล์ทั้งสอง
            lines1 = read_file_lines(self.file1) if validate_file_path(self.file1) else []
            lines2 = read_file_lines(self.file2) if validate_file_path(self.file2) else []
            
            # เปรียบเทียบ
            self.compare_files(lines1, lines2)
            
        except Exception as e:
            self.result_text.insert(tk.END, f"เกิดข้อผิดพลาดในการเปรียบเทียบ: {str(e)}")
    
    def compare_files(self, lines1: List[str], lines2: List[str]) -> None:
        """เปรียบเทียบไฟล์และแสดงผล"""
        
        # สถิติพื้นฐาน
        result = f"📊 สถิติการเปรียบเทียบ:\n"
        result += f"ไฟล์ที่ 1: {len(lines1):,} บรรทัด\n"
        result += f"ไฟล์ที่ 2: {len(lines2):,} บรรทัด\n\n"
        
        # เปรียบเทียบทีละบรรทัด
        max_lines = max(len(lines1), len(lines2))
        differences = []
        
        for i in range(max_lines):
            line1 = lines1[i].rstrip() if i < len(lines1) else None
            line2 = lines2[i].rstrip() if i < len(lines2) else None
            
            if line1 != line2:
                differences.append({
                    'line_number': i + 1,
                    'line1': line1,
                    'line2': line2
                })
        
        # แสดงผลลัพธ์
        if not differences:
            result += "✅ ไฟล์ทั้งสองเหมือนกัน\n"
        else:
            result += f"❌ พบความแตกต่าง {len(differences)} บรรทัด:\n\n"
            
            for diff in differences[:50]:  # แสดงแค่ 50 ความแตกต่างแรก
                line_num = diff['line_number']
                result += f"บรรทัดที่ {line_num}:\n"
                
                if diff['line1'] is None:
                    result += f"  ไฟล์ 1: [ไม่มีบรรทัดนี้]\n"
                else:
                    result += f"  ไฟล์ 1: {diff['line1']}\n"
                
                if diff['line2'] is None:
                    result += f"  ไฟล์ 2: [ไม่มีบรรทัดนี้]\n"
                else:
                    result += f"  ไฟล์ 2: {diff['line2']}\n"
                
                result += "\n"
            
            if len(differences) > 50:
                result += f"... และอีก {len(differences) - 50} ความแตกต่าง\n"
        
        self.result_text.insert(tk.END, result)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base classes and mixins for GUI components
คลาสฐานและมิกซินสำหรับส่วนประกอบของ GUI
"""

import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable

from config.constants import STYLES, EMOJIS, STATUS_MESSAGES
from utils.ui_utils import center_window


class BaseGUIComponent(ABC):
    """
    คลาสฐานสำหรับส่วนประกอบ GUI
    """
    
    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.frame: Optional[ttk.Frame] = None
        self.widgets: Dict[str, tk.Widget] = {}
        self.variables: Dict[str, tk.Variable] = {}
        
    @abstractmethod
    def create_widgets(self) -> None:
        """สร้าง widgets สำหรับส่วนประกอบนี้"""
        pass
    
    def setup_styles(self) -> None:
        """ตั้งค่าสไตล์สำหรับ widgets"""
        if hasattr(self, '_style_configured'):
            return
            
        style = ttk.Style()
        
        # กำหนดสไตล์พื้นฐาน
        style.configure('Title.TLabel', font=STYLES['title_font'])
        style.configure('Section.TLabel', font=STYLES['section_font'])
        style.configure('Success.TLabel', foreground=STYLES['success_color'])
        style.configure('Error.TLabel', foreground=STYLES['error_color'])
        style.configure('Info.TLabel', foreground=STYLES['info_color'])
        style.configure('Warning.TLabel', foreground=STYLES['warning_color'])
        
        self._style_configured = True
    
    def get_widget(self, name: str) -> Optional[tk.Widget]:
        """ดึง widget ตามชื่อ"""
        return self.widgets.get(name)
    
    def get_variable(self, name: str) -> Optional[tk.Variable]:
        """ดึง variable ตามชื่อ"""
        return self.variables.get(name)
    
    def set_enabled(self, enabled: bool) -> None:
        """เปิด/ปิดการใช้งาน widgets"""
        state = 'normal' if enabled else 'disabled'
        for widget in self.widgets.values():
            if hasattr(widget, 'config'):
                try:
                    widget.config(state=state)
                except tk.TclError:
                    pass  # บาง widgets ไม่รองรับ state


class StatusMixin:
    """
    Mixin สำหรับการจัดการสถานะและข้อความแจ้งเตือน
    """
    
    def __init__(self):
        self._status_label: Optional[ttk.Label] = None
        self._is_working = False
    
    def create_status_bar(self, parent: tk.Widget) -> ttk.Label:
        """สร้าง status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill='x', side='bottom', padx=5, pady=2)
        
        self._status_label = ttk.Label(
            status_frame, 
            text=STATUS_MESSAGES['ready']
        )
        self._status_label.pack(side='left')
        
        return self._status_label
    
    def update_status(self, message: str, status_type: str = 'info') -> None:
        """อัปเดตข้อความสถานะ"""
        if self._status_label:
            emoji = EMOJIS.get(status_type, EMOJIS['info'])
            self._status_label.config(text=f"{emoji} {message}")
    
    def set_working(self, working: bool) -> None:
        """ตั้งค่าสถานะการทำงาน"""
        self._is_working = working
        if working:
            self.update_status(STATUS_MESSAGES['working'], 'loading')
        else:
            self.update_status(STATUS_MESSAGES['ready'], 'success')
    
    def is_working(self) -> bool:
        """ตรวจสอบว่ากำลังทำงานอยู่หรือไม่"""
        return self._is_working


class ProgressMixin:
    """
    Mixin สำหรับการแสดงความคืบหน้า
    """
    
    def __init__(self):
        self._progress_bar: Optional[ttk.Progressbar] = None
        self._progress_window: Optional[tk.Toplevel] = None
    
    def create_progress_bar(self, parent: tk.Widget) -> ttk.Progressbar:
        """สร้าง progress bar"""
        self._progress_bar = ttk.Progressbar(
            parent,
            mode='indeterminate',
            length=300
        )
        return self._progress_bar
    
    def start_progress(self) -> None:
        """เริ่ม progress bar"""
        if self._progress_bar:
            self._progress_bar.start()
    
    def stop_progress(self) -> None:
        """หยุด progress bar"""
        if self._progress_bar:
            self._progress_bar.stop()
    
    def set_progress_value(self, value: float) -> None:
        """ตั้งค่า progress bar (สำหรับ determinate mode)"""
        if self._progress_bar:
            self._progress_bar.config(mode='determinate')
            self._progress_bar['value'] = value
    
    def create_progress_dialog(self, parent: tk.Tk, title: str, message: str) -> tk.Toplevel:
        """สร้างกล่องโต้ตอบแสดงความคืบหน้า"""
        self._progress_window = tk.Toplevel(parent)
        self._progress_window.title(title)
        self._progress_window.geometry("400x150")
        self._progress_window.resizable(False, False)
        self._progress_window.transient(parent)
        self._progress_window.grab_set()
        
        # จัดตำแหน่งให้อยู่กลาง
        center_window(self._progress_window, 400, 150)
        
        # Title
        title_label = ttk.Label(
            self._progress_window, 
            text=title, 
            style='Title.TLabel'
        )
        title_label.pack(pady=(10, 5))
        
        # Message
        message_label = ttk.Label(self._progress_window, text=message)
        message_label.pack(pady=(0, 10))
        
        # Progress bar
        progress_bar = ttk.Progressbar(
            self._progress_window,
            mode='indeterminate',
            length=350
        )
        progress_bar.pack(pady=(0, 10))
        progress_bar.start()
        
        # Cancel button (optional)
        button_frame = ttk.Frame(self._progress_window)
        button_frame.pack(pady=(0, 10))
        
        cancel_button = ttk.Button(
            button_frame,
            text="ยกเลิก",
            command=self.close_progress_dialog
        )
        cancel_button.pack()
        
        return self._progress_window
    
    def update_progress_dialog(self, message: str) -> None:
        """อัปเดตข้อความในกล่องโต้ตอบความคืบหน้า"""
        if self._progress_window:
            # หา label แรกที่ไม่ใช่ title
            for child in self._progress_window.winfo_children():
                if isinstance(child, ttk.Label) and child.cget('style') != 'Title.TLabel':
                    child.config(text=message)
                    break
    
    def close_progress_dialog(self) -> None:
        """ปิดกล่องโต้ตอบความคืบหน้า"""
        if self._progress_window:
            self._progress_window.destroy()
            self._progress_window = None


class FileOperationMixin:
    """
    Mixin สำหรับการดำเนินการกับไฟล์
    """
    
    def __init__(self):
        self._file_dialogs: Dict[str, Dict[str, Any]] = {
            'open_text': {
                'title': "เลือกไฟล์ข้อความ",
                'filetypes': [
                    ("Text files", "*.txt"),
                    ("JSON files", "*.json"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ]
            },
            'open_json': {
                'title': "เลือกไฟล์ JSON",
                'filetypes': [
                    ("JSON files", "*.json"),
                    ("All files", "*.*")
                ]
            },
            'save_text': {
                'title': "บันทึกไฟล์ข้อความ",
                'defaultextension': ".txt",
                'filetypes': [
                    ("Text files", "*.txt"),
                    ("JSON files", "*.json"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ]
            },
            'save_json': {
                'title': "บันทึกไฟล์ JSON",
                'defaultextension': ".json",
                'filetypes': [
                    ("JSON files", "*.json"),
                    ("All files", "*.*")
                ]
            },
            'select_folder': {
                'title': "เลือกโฟลเดอร์"
            }
        }
    
    def browse_file(self, dialog_type: str = 'open_text') -> Optional[str]:
        """เปิดกล่องโต้ตอบเลือกไฟล์"""
        from tkinter import filedialog
        
        config = self._file_dialogs.get(dialog_type, self._file_dialogs['open_text'])
        
        if dialog_type.startswith('save'):
            return filedialog.asksaveasfilename(**config)
        else:
            return filedialog.askopenfilename(**config)
    
    def browse_folder(self) -> Optional[str]:
        """เปิดกล่องโต้ตอบเลือกโฟลเดอร์"""
        from tkinter import filedialog
        
        config = self._file_dialogs['select_folder']
        return filedialog.askdirectory(**config)


class ValidationMixin:
    """
    Mixin สำหรับการตรวจสอบข้อมูล
    """
    
    def validate_required_field(self, value: str, field_name: str) -> bool:
        """ตรวจสอบว่าฟิลด์ที่จำเป็นไม่ว่าง"""
        if not value or not value.strip():
            self.show_error(f"กรุณากรอก{field_name}")
            return False
        return True
    
    def validate_file_exists(self, file_path: str) -> bool:
        """ตรวจสอบว่าไฟล์มีอยู่จริง"""
        from utils.file_utils import validate_file_path
        
        if not validate_file_path(file_path):
            self.show_error("ไม่พบไฟล์ที่ระบุ")
            return False
        return True
    
    def validate_number_range(self, value: int, min_val: int, max_val: int, field_name: str) -> bool:
        """ตรวจสอบว่าค่าตัวเลขอยู่ในช่วงที่กำหนด"""
        if value < min_val or value > max_val:
            self.show_error(f"{field_name}ต้องอยู่ระหว่าง {min_val} - {max_val}")
            return False
        return True
    
    def show_error(self, message: str) -> None:
        """แสดงข้อความข้อผิดพลาด (ต้อง implement ในคลาสลูก)"""
        pass


class EventMixin:
    """
    Mixin สำหรับการจัดการ events
    """
    
    def __init__(self):
        self._event_handlers: Dict[str, list] = {}
    
    def bind_event(self, event_name: str, handler: Callable) -> None:
        """ผูก event handler"""
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        self._event_handlers[event_name].append(handler)
    
    def trigger_event(self, event_name: str, *args, **kwargs) -> None:
        """เรียก event handlers"""
        if event_name in self._event_handlers:
            for handler in self._event_handlers[event_name]:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    print(f"Error in event handler: {e}")
    
    def unbind_event(self, event_name: str, handler: Callable) -> None:
        """ยกเลิกการผูก event handler"""
        if event_name in self._event_handlers:
            try:
                self._event_handlers[event_name].remove(handler)
            except ValueError:
                pass


class BaseTabComponent(BaseGUIComponent, StatusMixin, ProgressMixin, 
                      FileOperationMixin, ValidationMixin, EventMixin):
    """
    คลาสฐานสำหรับ tab components ที่รวม mixins ทั้งหมด
    """
    
    def __init__(self, parent: tk.Widget):
        BaseGUIComponent.__init__(self, parent)
        StatusMixin.__init__(self)
        ProgressMixin.__init__(self)
        FileOperationMixin.__init__(self)
        ValidationMixin.__init__(self)
        EventMixin.__init__(self)
        
        self.setup_styles()
    
    def show_error(self, message: str) -> None:
        """แสดงข้อความข้อผิดพลาด"""
        from utils.ui_utils import show_error_dialog
        show_error_dialog(self.parent, "ข้อผิดพลาด", message)
    
    def show_success(self, message: str) -> None:
        """แสดงข้อความความสำเร็จ"""
        from utils.ui_utils import show_success_dialog
        show_success_dialog(self.parent, "สำเร็จ", message)
    
    def show_warning(self, message: str) -> bool:
        """แสดงข้อความเตือน"""
        from utils.ui_utils import show_warning_dialog
        return show_warning_dialog(self.parent, "คำเตือน", message)


class BaseDialog(tk.Toplevel):
    """
    คลาสฐานสำหรับ dialog windows
    """
    
    def __init__(self, parent: tk.Tk, title: str, size: tuple = (400, 300)):
        super().__init__(parent)
        
        self.parent = parent
        self.result = None
        
        # ตั้งค่าหน้าต่าง
        self.title(title)
        self.geometry(f"{size[0]}x{size[1]}")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # จัดตำแหน่งให้อยู่กลาง
        center_window(self, size[0], size[1])
        
        # สร้าง widgets
        self.create_widgets()
        
        # ผูก events
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.bind("<Escape>", lambda e: self.on_cancel())
        self.bind("<Return>", lambda e: self.on_ok())
    
    def create_widgets(self) -> None:
        """สร้าง widgets สำหรับ dialog"""
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Content area (override ในคลาสลูก)
        self.create_content(main_frame)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(button_frame, text="ตกลง", command=self.on_ok).pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="ยกเลิก", command=self.on_cancel).pack(side='right')
    
    def create_content(self, parent: ttk.Frame) -> None:
        """สร้างเนื้อหา dialog (override ในคลาสลูก)"""
        pass
    
    def on_ok(self) -> None:
        """เมื่อกดปุ่มตกลง"""
        if self.validate():
            self.result = self.get_result()
            self.destroy()
    
    def on_cancel(self) -> None:
        """เมื่อกดปุ่มยกเลิก"""
        self.result = None
        self.destroy()
    
    def validate(self) -> bool:
        """ตรวจสอบข้อมูล (override ในคลาสลูก)"""
        return True
    
    def get_result(self) -> Any:
        """ดึงผลลัพธ์ (override ในคลาสลูก)"""
        return None
    
    def show_modal(self) -> Any:
        """แสดง dialog แบบ modal และรอผลลัพธ์"""
        self.wait_window()
        return self.result

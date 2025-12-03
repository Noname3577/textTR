#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI Utility Functions
ฟังก์ชันยูทิลิตี้สำหรับ UI และการแสดงผล
"""

import os
import platform
import subprocess
from typing import List, Tuple, Any
import tkinter as tk
from tkinter import messagebox


# Emojis for UI (standalone definition for this module)
EMOJIS = {
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
}


def center_window(window: tk.Tk, width: int = None, height: int = None) -> None:
    """
    จัดตำแหน่งหน้าต่างให้อยู่กลางหน้าจอ
    
    Args:
        window: หน้าต่างที่จะจัดตำแหน่ง
        width: ความกว้างที่ต้องการ (None = ใช้ขนาดปัจจุบัน)
        height: ความสูงที่ต้องการ (None = ใช้ขนาดปัจจุบัน)
    """
    window.update_idletasks()
    
    if width is None:
        width = window.winfo_width()
    if height is None:
        height = window.winfo_height()
    
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    window.geometry(f"{width}x{height}+{x}+{y}")


def open_file_manager(path: str) -> bool:
    """
    เปิดโปรแกรมจัดการไฟล์ที่เส้นทางที่กำหนด
    
    Args:
        path: เส้นทางที่จะเปิด
        
    Returns:
        True ถ้าเปิดสำเร็จ, False ถ้าล้มเหลว
    """
    try:
        system = platform.system()
        
        if system == "Windows":
            os.startfile(path)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", path])
        else:  # Linux และ Unix อื่นๆ
            subprocess.run(["xdg-open", path])
        
        return True
    except Exception:
        return False


def show_error_dialog(parent: tk.Tk, title: str, message: str) -> None:
    """
    แสดงกล่องโต้ตอบข้อผิดพลาด
    
    Args:
        parent: หน้าต่างหลัก
        title: หัวข้อกล่องโต้ตอบ
        message: ข้อความแสดง
    """
    messagebox.showerror(title, f"{EMOJIS['error']} {message}", parent=parent)


def show_success_dialog(parent: tk.Tk, title: str, message: str) -> None:
    """
    แสดงกล่องโต้ตอบความสำเร็จ
    
    Args:
        parent: หน้าต่างหลัก
        title: หัวข้อกล่องโต้ตอบ
        message: ข้อความแสดง
    """
    messagebox.showinfo(title, f"{EMOJIS['success']} {message}", parent=parent)


def show_warning_dialog(parent: tk.Tk, title: str, message: str) -> bool:
    """
    แสดงกล่องโต้ตอบเตือน
    
    Args:
        parent: หน้าต่างหลัก
        title: หัวข้อกล่องโต้ตอบ
        message: ข้อความแสดง
        
    Returns:
        True ถ้าผู้ใช้เลือก Yes, False ถ้าเลือก No
    """
    result = messagebox.askyesno(title, f"{EMOJIS['warning']} {message}", parent=parent)
    return result


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    ตัดข้อความให้มีความยาวไม่เกินที่กำหนด
    
    Args:
        text: ข้อความต้นฉบับ
        max_length: ความยาวสูงสุด
        
    Returns:
        ข้อความที่ตัดแล้ว
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."


def safe_int_conversion(value: str, default: int = 0) -> int:
    """
    แปลงสตริงเป็นจำนวนเต็มอย่างปลอดภัย
    
    Args:
        value: สตริงที่จะแปลง
        default: ค่าเริ่มต้นถ้าแปลงไม่ได้
        
    Returns:
        จำนวนเต็มที่แปลงได้หรือค่าเริ่มต้น
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def calculate_pagination(total_items: int, items_per_page: int) -> Tuple[int, List[int]]:
    """
    คำนวณข้อมูลการแบ่งหน้า
    
    Args:
        total_items: จำนวนรายการทั้งหมด
        items_per_page: จำนวนรายการต่อหน้า
        
    Returns:
        Tuple (จำนวนหน้าทั้งหมด, รายการหมายเลขหน้า)
    """
    if total_items <= 0 or items_per_page <= 0:
        return 0, []
    
    total_pages = (total_items + items_per_page - 1) // items_per_page
    page_numbers = list(range(1, total_pages + 1))
    
    return total_pages, page_numbers


def get_page_items(items: List[Any], page: int, items_per_page: int) -> List[Any]:
    """
    ดึงรายการในหน้าที่กำหนด
    
    Args:
        items: รายการทั้งหมด
        page: หมายเลขหน้า (เริ่มจาก 1)
        items_per_page: จำนวนรายการต่อหน้า
        
    Returns:
        รายการในหน้าที่กำหนด
    """
    if page <= 0 or items_per_page <= 0:
        return []
    
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    
    return items[start_index:end_index]

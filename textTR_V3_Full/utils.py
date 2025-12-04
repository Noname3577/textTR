#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility Functions for Text File Splitter & Merger GUI
ฟังก์ชันยูทิลิตี้สำหรับแอปพลิเคชัน GUI แบ่งและรวมไฟล์ข้อความ
"""

import os
import sys
import json
import platform
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any, Union
import tkinter as tk
from tkinter import messagebox

from constants import ERROR_MESSAGES, SUCCESS_MESSAGES, STATUS_MESSAGES, EMOJIS


def format_file_size(size_bytes: int) -> str:
    """
    แปลงขนาดไฟล์เป็นรูปแบบที่อ่านง่าย
    
    Args:
        size_bytes: ขนาดไฟล์ในหน่วยไบต์
        
    Returns:
        สตริงขนาดไฟล์ในรูปแบบที่อ่านง่าย เช่น "1.5 MB"
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    size_index = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and size_index < len(size_names) - 1:
        size /= 1024.0
        size_index += 1
    
    if size_index == 0:
        return f"{int(size)} {size_names[size_index]}"
    else:
        return f"{size:.1f} {size_names[size_index]}"


def format_timestamp(timestamp: float) -> str:
    """
    แปลงเวลาเป็นรูปแบบที่อ่านง่าย
    
    Args:
        timestamp: เวลาในรูปแบบ Unix timestamp
        
    Returns:
        สตริงเวลาในรูปแบบที่อ่านง่าย
    """
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OSError):
        return "ไม่ทราบ"


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    ดึงข้อมูลไฟล์
    
    Args:
        file_path: เส้นทางไฟล์
        
    Returns:
        Dictionary ที่มีข้อมูลไฟล์
    """
    if not file_path or not os.path.exists(file_path):
        return {}
    
    try:
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'size_formatted': format_file_size(stat.st_size),
            'modified': stat.st_mtime,
            'modified_formatted': format_timestamp(stat.st_mtime),
            'created': stat.st_ctime,
            'created_formatted': format_timestamp(stat.st_ctime),
            'is_file': os.path.isfile(file_path),
            'is_dir': os.path.isdir(file_path),
            'extension': os.path.splitext(file_path)[1].lower()
        }
    except (OSError, IOError):
        return {}


def count_lines_in_file(file_path: str) -> int:
    """
    นับจำนวนบรรทัดในไฟล์
    
    Args:
        file_path: เส้นทางไฟล์
        
    Returns:
        จำนวนบรรทัดในไฟล์
    """
    if not os.path.exists(file_path):
        return 0
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except (IOError, OSError):
        return 0


def read_file_lines(file_path: str, max_lines: Optional[int] = None) -> List[str]:
    """
    อ่านบรรทัดจากไฟล์
    
    Args:
        file_path: เส้นทางไฟล์
        max_lines: จำนวนบรรทัดสูงสุดที่จะอ่าน (None = อ่านทั้งหมด)
        
    Returns:
        รายการบรรทัดในไฟล์
    """
    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            if max_lines is None:
                return f.readlines()
            else:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    lines.append(line)
                return lines
    except (IOError, OSError):
        return []


def write_file_lines(file_path: str, lines: List[str]) -> bool:
    """
    เขียนบรรทัดลงไฟล์
    
    Args:
        file_path: เส้นทางไฟล์
        lines: รายการบรรทัดที่จะเขียน
        
    Returns:
        True ถ้าเขียนสำเร็จ, False ถ้าล้มเหลว
    """
    try:
        # สร้างโฟลเดอร์ถ้ายังไม่มี
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    except (IOError, OSError):
        return False


def validate_file_path(file_path: str) -> bool:
    """
    ตรวจสอบว่าเส้นทางไฟล์ถูกต้องและอ่านได้
    
    Args:
        file_path: เส้นทางไฟล์
        
    Returns:
        True ถ้าไฟล์ถูกต้อง, False ถ้าไม่ถูกต้อง
    """
    return (file_path and 
            os.path.exists(file_path) and 
            os.path.isfile(file_path) and 
            os.access(file_path, os.R_OK))


def validate_directory_path(dir_path: str) -> bool:
    """
    ตรวจสอบว่าเส้นทางโฟลเดอร์ถูกต้องและเข้าถึงได้
    
    Args:
        dir_path: เส้นทางโฟลเดอร์
        
    Returns:
        True ถ้าโฟลเดอร์ถูกต้อง, False ถ้าไม่ถูกต้อง
    """
    return (dir_path and 
            os.path.exists(dir_path) and 
            os.path.isdir(dir_path) and 
            os.access(dir_path, os.R_OK))


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


def create_backup_file(file_path: str) -> Optional[str]:
    """
    สร้างไฟล์สำรองก่อนแก้ไข
    
    Args:
        file_path: เส้นทางไฟล์ต้นฉบับ
        
    Returns:
        เส้นทางไฟล์สำรองถ้าสร้างสำเร็จ, None ถ้าล้มเหลว
    """
    if not validate_file_path(file_path):
        return None
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.backup_{timestamp}"
        
        # คัดลอกไฟล์
        import shutil
        shutil.copy2(file_path, backup_path)
        
        return backup_path
    except Exception:
        return None


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


def sanitize_filename(filename: str) -> str:
    """
    ทำความสะอาดชื่อไฟล์ให้ปลอดภัย
    
    Args:
        filename: ชื่อไฟล์ต้นฉบับ
        
    Returns:
        ชื่อไฟล์ที่ปลอดภัย
    """
    # ตัวอักษรที่ไม่อนุญาตในชื่อไฟล์
    invalid_chars = '<>:"/\\|?*'
    
    # แทนที่ตัวอักษรที่ไม่อนุญาตด้วย underscore
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # ตัดช่องว่างหน้าและหลัง
    filename = filename.strip()
    
    # ถ้าชื่อไฟล์ว่าง ให้ใช้ชื่อเริ่มต้น
    if not filename:
        filename = "untitled"
    
    return filename


def get_unique_filename(file_path: str) -> str:
    """
    หาชื่อไฟล์ที่ไม่ซ้ำกัน
    
    Args:
        file_path: เส้นทางไฟล์ที่ต้องการ
        
    Returns:
        เส้นทางไฟล์ที่ไม่ซ้ำกัน
    """
    if not os.path.exists(file_path):
        return file_path
    
    base, ext = os.path.splitext(file_path)
    counter = 1
    
    while True:
        new_path = f"{base}_{counter}{ext}"
        if not os.path.exists(new_path):
            return new_path
        counter += 1


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


def is_text_file(file_path: str) -> bool:
    """
    ตรวจสอบว่าเป็นไฟล์ข้อความหรือไม่
    
    Args:
        file_path: เส้นทางไฟล์
        
    Returns:
        True ถ้าเป็นไฟล์ข้อความ, False ถ้าไม่ใช่
    """
    if not validate_file_path(file_path):
        return False
    
    # ตรวจสอบจากนามสกุล
    from constants import TEXT_EXTENSIONS
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext in TEXT_EXTENSIONS:
        return True
    
    # ตรวจสอบจากเนื้อหาไฟล์ (ตัวอย่าง 1024 ไบต์แรก)
    try:
        with open(file_path, 'rb') as f:
            sample = f.read(1024)
            
        # ถ้ามี null byte แสดงว่าเป็น binary file
        if b'\x00' in sample:
            return False
        
        # ลองถอดรหัส UTF-8
        try:
            sample.decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False
            
    except (IOError, OSError):
        return False


# ================== JSON File Operations ==================

def is_json_file(file_path: str) -> bool:
    """
    ตรวจสอบว่าเป็นไฟล์ JSON หรือไม่
    
    Args:
        file_path: เส้นทางไฟล์
        
    Returns:
        True ถ้าเป็นไฟล์ JSON, False ถ้าไม่ใช่
    """
    if not file_path:
        return False
    ext = os.path.splitext(file_path)[1].lower()
    return ext == '.json'


def read_json_file(file_path: str) -> Optional[Union[Dict, List]]:
    """
    อ่านไฟล์ JSON และคืนค่าเป็น Python object
    
    Args:
        file_path: เส้นทางไฟล์ JSON
        
    Returns:
        Dictionary หรือ List ที่อ่านจากไฟล์, None ถ้าล้มเหลว
    """
    if not validate_file_path(file_path):
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, OSError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file: {e}")
        return None


def write_json_file(file_path: str, data: Union[Dict, List], 
                    indent: int = 2, ensure_ascii: bool = False) -> bool:
    """
    เขียนข้อมูลลงไฟล์ JSON
    
    Args:
        file_path: เส้นทางไฟล์ JSON
        data: ข้อมูลที่จะเขียน (Dictionary หรือ List)
        indent: จำนวนช่องว่างสำหรับ indentation
        ensure_ascii: ถ้า False จะเก็บ Unicode characters โดยตรง
        
    Returns:
        True ถ้าเขียนสำเร็จ, False ถ้าล้มเหลว
    """
    try:
        # สร้างโฟลเดอร์ถ้ายังไม่มี
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
        return True
    except (IOError, OSError, TypeError) as e:
        print(f"Error writing JSON file: {e}")
        return False


def json_to_text_lines(data: Union[Dict, List], key_field: str = None, 
                       value_field: str = None) -> List[str]:
    """
    แปลง JSON data เป็นรายการบรรทัดข้อความสำหรับแสดงผลหรือแก้ไข
    
    รูปแบบการแปลง:
    - ถ้าเป็น List of strings: แต่ละ item เป็น 1 บรรทัด
    - ถ้าเป็น List of dicts: แปลงเป็น "key: value" หรือ JSON แต่ละ item
    - ถ้าเป็น Dict: แปลงเป็น "key: value" ต่อบรรทัด
    
    Args:
        data: ข้อมูล JSON (Dict หรือ List)
        key_field: ชื่อ field ที่จะใช้เป็น key (สำหรับ List of dicts)
        value_field: ชื่อ field ที่จะใช้เป็น value (สำหรับ List of dicts)
        
    Returns:
        รายการบรรทัดข้อความ
    """
    lines = []
    
    if isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, str):
                lines.append(item + '\n')
            elif isinstance(item, dict):
                if key_field and value_field and key_field in item and value_field in item:
                    # ใช้ format key: value
                    lines.append(f"{item[key_field]}: {item[value_field]}\n")
                else:
                    # แปลงทั้ง dict เป็น JSON string
                    lines.append(json.dumps(item, ensure_ascii=False) + '\n')
            else:
                lines.append(str(item) + '\n')
    
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}\n")
            else:
                lines.append(f"{key}: {value}\n")
    
    return lines


def text_lines_to_json(lines: List[str], output_format: str = 'list',
                       key_field: str = 'key', value_field: str = 'value',
                       separator: str = ':') -> Union[Dict, List]:
    """
    แปลงบรรทัดข้อความกลับเป็น JSON data
    
    Args:
        lines: รายการบรรทัดข้อความ
        output_format: รูปแบบผลลัพธ์ ('list', 'dict', 'list_of_dicts')
        key_field: ชื่อ field สำหรับ key (ใช้กับ list_of_dicts)
        value_field: ชื่อ field สำหรับ value (ใช้กับ list_of_dicts)
        separator: ตัวคั่นระหว่าง key และ value
        
    Returns:
        JSON data ในรูปแบบที่กำหนด
    """
    if output_format == 'list':
        # แปลงเป็น list of strings (ตัด newline ออก)
        return [line.rstrip('\n\r') for line in lines if line.strip()]
    
    elif output_format == 'dict':
        # แปลงเป็น dictionary
        result = {}
        for line in lines:
            line = line.strip()
            if line and separator in line:
                key, value = line.split(separator, 1)
                key = key.strip()
                value = value.strip()
                # ลองแปลง value เป็น JSON ถ้าเป็นไปได้
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass
                result[key] = value
        return result
    
    elif output_format == 'list_of_dicts':
        # แปลงเป็น list of dicts
        result = []
        for line in lines:
            line = line.strip()
            if line:
                # ลองแปลงจาก JSON string ก่อน
                try:
                    item = json.loads(line)
                    if isinstance(item, dict):
                        result.append(item)
                        continue
                except json.JSONDecodeError:
                    pass
                
                # ถ้าไม่ใช่ JSON ให้ใช้ separator
                if separator in line:
                    key, value = line.split(separator, 1)
                    result.append({
                        key_field: key.strip(),
                        value_field: value.strip()
                    })
                else:
                    result.append({value_field: line})
        return result
    
    return []


def extract_json_strings(data: Union[Dict, List], field_path: str = None) -> List[str]:
    """
    ดึงข้อความทั้งหมดจาก JSON data สำหรับการแปล
    
    Args:
        data: ข้อมูล JSON
        field_path: เส้นทางไปยัง field ที่ต้องการ (เช่น "items.text")
        
    Returns:
        รายการข้อความที่ดึงได้
    """
    strings = []
    
    def extract_from_value(value, depth=0):
        if isinstance(value, str) and value.strip():
            strings.append(value)
        elif isinstance(value, list):
            for item in value:
                extract_from_value(item, depth + 1)
        elif isinstance(value, dict):
            for v in value.values():
                extract_from_value(v, depth + 1)
    
    if field_path:
        # นำทางไปยัง field ที่ต้องการ
        current = data
        for key in field_path.split('.'):
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and key.isdigit():
                current = current[int(key)]
            else:
                return []
        extract_from_value(current)
    else:
        extract_from_value(data)
    
    return strings


def update_json_strings(data: Union[Dict, List], old_strings: List[str], 
                        new_strings: List[str]) -> Union[Dict, List]:
    """
    อัปเดตข้อความใน JSON data (สำหรับใช้หลังการแปล)
    
    Args:
        data: ข้อมูล JSON ต้นฉบับ
        old_strings: รายการข้อความเดิม
        new_strings: รายการข้อความใหม่ที่จะแทนที่
        
    Returns:
        JSON data ที่อัปเดตแล้ว
    """
    if len(old_strings) != len(new_strings):
        return data
    
    # สร้าง mapping
    string_map = dict(zip(old_strings, new_strings))
    
    def update_value(value):
        if isinstance(value, str):
            return string_map.get(value, value)
        elif isinstance(value, list):
            return [update_value(item) for item in value]
        elif isinstance(value, dict):
            return {k: update_value(v) for k, v in value.items()}
        return value
    
    return update_value(data)


def get_json_structure_info(data: Union[Dict, List]) -> Dict[str, Any]:
    """
    วิเคราะห์โครงสร้างของ JSON data
    
    Args:
        data: ข้อมูล JSON
        
    Returns:
        Dictionary ที่มีข้อมูลโครงสร้าง
    """
    info = {
        'type': type(data).__name__,
        'size': 0,
        'depth': 0,
        'string_count': 0,
        'keys': [],
        'sample': None
    }
    
    def analyze(value, depth=0):
        if depth > info['depth']:
            info['depth'] = depth
        
        if isinstance(value, str):
            info['string_count'] += 1
        elif isinstance(value, list):
            info['size'] = max(info['size'], len(value))
            for item in value:
                analyze(item, depth + 1)
        elif isinstance(value, dict):
            if depth == 0:
                info['keys'] = list(value.keys())
            for v in value.values():
                analyze(v, depth + 1)
    
    analyze(data)
    
    # เก็บตัวอย่างข้อมูล
    if isinstance(data, list) and len(data) > 0:
        info['sample'] = data[0]
    elif isinstance(data, dict):
        info['sample'] = {k: v for k, v in list(data.items())[:3]}
    
    return info


def count_lines_in_json(file_path: str) -> int:
    """
    นับจำนวนบรรทัดที่สามารถแปลได้ในไฟล์ JSON
    
    Args:
        file_path: เส้นทางไฟล์ JSON
        
    Returns:
        จำนวนบรรทัด/รายการที่นับได้
    """
    data = read_json_file(file_path)
    if data is None:
        return 0
    
    if isinstance(data, list):
        return len(data)
    elif isinstance(data, dict):
        return len(data)
    return 0
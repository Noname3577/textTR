#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON Utility Functions
ฟังก์ชันยูทิลิตี้สำหรับจัดการไฟล์ JSON
"""

import os
import json
from typing import List, Dict, Optional, Any, Union

from utils.file_utils import validate_file_path


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

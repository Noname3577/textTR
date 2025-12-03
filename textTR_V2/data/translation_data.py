#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translation Data Management
คลาสสำหรับจัดการข้อมูลการแปล
"""

import copy
from typing import List, Dict, Any, Optional

from utils.file_utils import (
    read_file_lines,
    write_file_lines,
    validate_file_path,
    create_backup_file
)
from utils.json_utils import (
    is_json_file,
    read_json_file,
    write_json_file,
    get_json_structure_info
)


class TranslationData:
    """
    คลาสสำหรับจัดการข้อมูลการแปล
    รองรับทั้งไฟล์ข้อความธรรมดาและไฟล์ JSON
    """
    
    def __init__(self):
        self.lines: List[Dict[str, Any]] = []
        self.file_path: Optional[str] = None
        self.is_json: bool = False
        self.json_data: Optional[Any] = None
        self.json_key_field: Optional[str] = None
        self.json_value_field: Optional[str] = None
        self.json_output_format: str = 'list'
    
    def load_from_file(self, file_path: str) -> bool:
        """โหลดไฟล์สำหรับแปล (รองรับทั้ง text และ JSON)"""
        if not validate_file_path(file_path):
            return False
        
        try:
            self.is_json = is_json_file(file_path)
            
            if self.is_json:
                return self._load_json_file(file_path)
            else:
                return self._load_text_file(file_path)
                
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
    def _load_text_file(self, file_path: str) -> bool:
        """โหลดไฟล์ข้อความธรรมดา"""
        try:
            lines = read_file_lines(file_path)
            self.lines = []
            
            for i, line in enumerate(lines):
                self.lines.append({
                    'line_number': i + 1,
                    'original': line.rstrip('\n\r'),
                    'translated': '',
                    'is_translated': False,
                    'status': 'pending',
                    'skip_translation': False
                })
            
            self.file_path = file_path
            return True
            
        except Exception:
            return False
    
    def _load_json_file(self, file_path: str) -> bool:
        """โหลดไฟล์ JSON และแปลงเป็นรูปแบบสำหรับการแปล"""
        try:
            self.json_data = read_json_file(file_path)
            if self.json_data is None:
                return False
            
            # วิเคราะห์โครงสร้าง JSON
            json_info = get_json_structure_info(self.json_data)
            
            # ตรวจสอบรูปแบบและแปลงเป็น lines
            self.lines = []
            
            if isinstance(self.json_data, list):
                self.json_output_format = 'list'
                for i, item in enumerate(self.json_data):
                    if isinstance(item, str):
                        # List of strings
                        self.lines.append({
                            'line_number': i + 1,
                            'original': item,
                            'translated': '',
                            'is_translated': False,
                            'status': 'pending',
                            'skip_translation': False,
                            'json_index': i
                        })
                    elif isinstance(item, dict):
                        # List of dicts - หาค่าที่เป็น string
                        self.json_output_format = 'list_of_dicts'
                        for key, value in item.items():
                            if isinstance(value, str) and value.strip():
                                self.lines.append({
                                    'line_number': len(self.lines) + 1,
                                    'original': value,
                                    'translated': '',
                                    'is_translated': False,
                                    'status': 'pending',
                                    'skip_translation': False,
                                    'json_index': i,
                                    'json_key': key
                                })
            
            elif isinstance(self.json_data, dict):
                self.json_output_format = 'dict'
                for i, (key, value) in enumerate(self.json_data.items()):
                    if isinstance(value, str) and value.strip():
                        self.lines.append({
                            'line_number': i + 1,
                            'original': value,
                            'translated': '',
                            'is_translated': False,
                            'status': 'pending',
                            'skip_translation': False,
                            'json_key': key
                        })
                    elif isinstance(value, list):
                        # Dict with list values
                        for j, item in enumerate(value):
                            if isinstance(item, str) and item.strip():
                                self.lines.append({
                                    'line_number': len(self.lines) + 1,
                                    'original': item,
                                    'translated': '',
                                    'is_translated': False,
                                    'status': 'pending',
                                    'skip_translation': False,
                                    'json_key': key,
                                    'json_list_index': j
                                })
            
            self.file_path = file_path
            return len(self.lines) > 0
            
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            return False
    
    def get_line_count(self) -> int:
        """ดึงจำนวนบรรทัดทั้งหมด"""
        return len(self.lines)
    
    def get_translated_count(self) -> int:
        """ดึงจำนวนบรรทัดที่แปลแล้ว"""
        return sum(1 for line in self.lines if line['is_translated'])
    
    def get_progress_percentage(self) -> float:
        """ดึงเปอร์เซ็นต์ความคืบหน้า"""
        total = self.get_line_count()
        translated = self.get_translated_count()
        return (translated / total * 100) if total > 0 else 0
    
    def translate_line(self, line_index: int, translated_text: str) -> bool:
        """อัปเดตการแปลของบรรทัด"""
        if 0 <= line_index < len(self.lines):
            self.lines[line_index]['translated'] = translated_text
            self.lines[line_index]['is_translated'] = bool(translated_text.strip())
            self.lines[line_index]['status'] = 'completed' if translated_text.strip() else 'pending'
            return True
        return False
    
    def toggle_skip_translation(self, line_index: int) -> bool:
        """เปิด/ปิดการข้ามการแปลของบรรทัด"""
        if 0 <= line_index < len(self.lines):
            current_skip = self.lines[line_index]['skip_translation']
            self.lines[line_index]['skip_translation'] = not current_skip
            # อัปเดตสถานะ
            if self.lines[line_index]['skip_translation']:
                self.lines[line_index]['status'] = 'skipped'
            else:
                # กลับไปเป็นสถานะเดิม
                if self.lines[line_index]['is_translated']:
                    self.lines[line_index]['status'] = 'completed'
                else:
                    self.lines[line_index]['status'] = 'pending'
            return True
        return False
    
    def get_skipped_count(self) -> int:
        """ดึงจำนวนบรรทัดที่ข้ามการแปล"""
        return sum(1 for line in self.lines if line['skip_translation'])
    
    def get_lines_to_translate(self) -> List[int]:
        """ดึงดัชนีบรรทัดที่ต้องแปล (ไม่รวมที่ข้าม)"""
        return [i for i, line in enumerate(self.lines) 
                if not line['skip_translation'] and not line['is_translated'] and line['original'].strip()]
    
    def save_to_file(self, file_path: Optional[str] = None) -> bool:
        """บันทึกการแปลลงไฟล์ (รองรับทั้ง text และ JSON)"""
        target_file = file_path or self.file_path
        if not target_file:
            return False
        
        try:
            # สร้าง backup ถ้าเป็นไฟล์เดิม
            if target_file == self.file_path:
                create_backup_file(target_file)
            
            if self.is_json:
                return self._save_json_file(target_file)
            else:
                return self._save_text_file(target_file)
            
        except Exception as e:
            print(f"Error saving file: {e}")
            return False
    
    def _save_text_file(self, file_path: str) -> bool:
        """บันทึกไฟล์ข้อความธรรมดา"""
        try:
            output_lines = []
            for line_data in self.lines:
                if line_data['is_translated'] and line_data['translated'].strip():
                    output_lines.append(line_data['translated'] + '\n')
                else:
                    output_lines.append(line_data['original'] + '\n')
            
            return write_file_lines(file_path, output_lines)
        except Exception:
            return False
    
    def _save_json_file(self, file_path: str) -> bool:
        """บันทึกไฟล์ JSON พร้อมการแปล"""
        try:
            # สร้าง copy ของ JSON data เดิม
            output_data = copy.deepcopy(self.json_data)
            
            # อัปเดตค่าที่แปลแล้ว
            for line_data in self.lines:
                if line_data['is_translated'] and line_data['translated'].strip():
                    translated = line_data['translated']
                    
                    if self.json_output_format == 'list':
                        # List of strings
                        if 'json_index' in line_data:
                            output_data[line_data['json_index']] = translated
                    
                    elif self.json_output_format == 'list_of_dicts':
                        # List of dicts
                        if 'json_index' in line_data and 'json_key' in line_data:
                            output_data[line_data['json_index']][line_data['json_key']] = translated
                    
                    elif self.json_output_format == 'dict':
                        # Dict
                        if 'json_key' in line_data:
                            if 'json_list_index' in line_data:
                                # Dict with list values
                                output_data[line_data['json_key']][line_data['json_list_index']] = translated
                            else:
                                output_data[line_data['json_key']] = translated
            
            return write_json_file(file_path, output_data)
            
        except Exception as e:
            print(f"Error saving JSON file: {e}")
            return False
    
    def get_file_type_info(self) -> str:
        """ดึงข้อมูลประเภทไฟล์"""
        if self.is_json:
            return f"JSON ({self.json_output_format})"
        return "Text"

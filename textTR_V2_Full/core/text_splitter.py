#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text File Splitter and Merger
สำหรับแบ่งไฟล์ข้อความออกเป็นไฟล์เล็กๆ และรวมไฟล์กลับคืน
"""

import os
import glob
from pathlib import Path
from datetime import datetime


def split_text_file(input_file, lines_per_file=500, output_prefix=None, create_folder=True):
    """
    แบ่งไฟล์ข้อความออกเป็นไฟล์เล็กๆ
    
    Args:
        input_file (str): ชื่อไฟล์ต้นฉบับ
        lines_per_file (int): จำนวนบรรทัดต่อไฟล์ (default: 500)
        output_prefix (str): คำนำหน้าชื่อไฟล์ผลลัพธ์ (default: ชื่อไฟล์เดิม)
        create_folder (bool): สร้างโฟลเดอร์ใหม่สำหรับเก็บไฟล์ที่แบ่ง (default: True)
    
    Returns:
        tuple: (รายชื่อไฟล์ที่สร้างขึ้น, path ของโฟลเดอร์)
    """
    input_path = Path(input_file)
    
    # ตรวจสอบว่าไฟล์มีอยู่จริง
    if not input_path.exists():
        raise FileNotFoundError(f"ไม่พบไฟล์: {input_file}")
    
    # กำหนด prefix สำหรับไฟล์ผลลัพธ์
    if output_prefix is None:
        output_prefix = input_path.stem
    
    # สร้างโฟลเดอร์สำหรับเก็บไฟล์ที่แบ่ง
    if create_folder:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{output_prefix}_split_{timestamp}"
        output_dir = input_path.parent / folder_name
        output_dir.mkdir(exist_ok=True)
        print(f"📁 สร้างโฟลเดอร์: {folder_name}")
    else:
        output_dir = input_path.parent
    
    # เก็บรายชื่อไฟล์ที่สร้างขึ้น
    output_files = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            file_number = 1
            current_lines = 0
            outfile = None
            
            for line in infile:
                # เปิดไฟล์ใหม่เมื่อต้องการ
                if current_lines == 0:
                    if outfile:
                        outfile.close()
                    
                    # สร้างชื่อไฟล์ใหม่
                    output_filename = f"{output_prefix}_part_{file_number:03d}.txt"
                    output_path = output_dir / output_filename
                    output_files.append(str(output_path))
                    
                    outfile = open(output_path, 'w', encoding='utf-8')
                    print(f"📄 กำลังสร้างไฟล์: {output_filename}")
                
                # เขียนบรรทัดลงไฟล์
                outfile.write(line)
                current_lines += 1
                
                # เมื่อครบจำนวนบรรทัดที่กำหนด
                if current_lines >= lines_per_file:
                    current_lines = 0
                    file_number += 1
            
            # ปิดไฟล์สุดท้าย
            if outfile:
                outfile.close()
    
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการแบ่งไฟล์: {e}")
        return []
    
    print(f"✅ แบ่งไฟล์เสร็จสิ้น! สร้างไฟล์ทั้งหมด {len(output_files)} ไฟล์")
    if create_folder:
        print(f"📂 ไฟล์ทั้งหมดถูกเก็บไว้ใน: {output_dir.name}")
    
    return output_files, str(output_dir) if create_folder else None


def merge_text_files(file_pattern, output_file=None, source_folder=None):
    """
    รวมไฟล์ข้อความที่แบ่งแล้วกลับเป็นไฟล์เดียว
    
    Args:
        file_pattern (str): รูปแบบชื่อไฟล์ที่ต้องการรวม (เช่น "filename_part_*.txt")
        output_file (str): ชื่อไฟล์ผลลัพธ์ (default: merged.txt)
        source_folder (str): โฟลเดอร์ที่มีไฟล์ที่ต้องการรวม (optional)
    
    Returns:
        str: ชื่อไฟล์ที่รวมแล้ว
    """
    # หาไฟล์ที่ตรงกับรูปแบบ
    if source_folder:
        search_pattern = os.path.join(source_folder, file_pattern)
    else:
        search_pattern = file_pattern
    
    files = sorted(glob.glob(search_pattern))
    
    if not files:
        search_info = f"รูปแบบ: {search_pattern}" if source_folder else f"รูปแบบ: {file_pattern}"
        raise FileNotFoundError(f"ไม่พบไฟล์ที่ตรงกับ {search_info}")
    
    print(f"🔍 พบไฟล์ที่จะรวม: {len(files)} ไฟล์")
    
    # กำหนดชื่อไฟล์ผลลัพธ์
    if output_file is None:
        base_pattern = file_pattern.replace("_part_*.txt", "").replace("*", "merged")
        output_file = f"{base_pattern}_merged.txt"
    
    # ตรวจสอบว่า output_file เป็นโฟลเดอร์หรือไม่
    if os.path.isdir(output_file):
        base_name = os.path.basename(file_pattern).replace("*", "merged").replace(".txt", "")
        output_file = os.path.join(output_file, f"{base_name}_merged.txt")
    
    # สร้างโฟลเดอร์ถ้าต้องการ
    output_dir = os.path.dirname(output_file) if os.path.dirname(output_file) else '.'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for i, file_path in enumerate(files, 1):
                print(f"📋 กำลังรวมไฟล์ {i}/{len(files)}: {os.path.basename(file_path)}")
                
                with open(file_path, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
    
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการรวมไฟล์: {e}")
        return None
    
    print(f"✅ รวมไฟล์เสร็จสิ้น! ไฟล์ผลลัพธ์: {output_file}")
    return output_file

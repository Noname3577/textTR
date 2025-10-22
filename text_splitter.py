#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text File Splitter and Merger
สำหรับแบ่งไฟล์ข้อความออกเป็นไฟล์เล็กๆ และรวมไฟล์กลับคืน
"""

import os
import sys
from pathlib import Path


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
        from datetime import datetime
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
    import glob
    
    # หาไฟล์ที่ตรงกับรูปแบบ
    if source_folder:
        # ถ้ามี source_folder ให้หาในโฟลเดอร์นั้น
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
        # ลองสร้างชื่อไฟล์จากรูปแบบที่ให้มา
        base_pattern = file_pattern.replace("_part_*.txt", "").replace("*", "merged")
        output_file = f"{base_pattern}_merged.txt"
    
    # ตรวจสอบว่า output_file เป็นโฟลเดอร์หรือไม่
    if os.path.isdir(output_file):
        # ถ้าเป็นโฟลเดอร์ ให้สร้างชื่อไฟล์ใหม่
        base_name = os.path.basename(file_pattern).replace("*", "merged").replace(".txt", "")
        output_file = os.path.join(output_file, f"{base_name}_merged.txt")
    
    # ตรวจสอบว่าสามารถเขียนไฟล์ได้หรือไม่
    output_dir = os.path.dirname(output_file) if os.path.dirname(output_file) else '.'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for i, file_path in enumerate(files, 1):
                print(f"📋 กำลังรวมไฟล์ {i}/{len(files)}: {os.path.basename(file_path)}")
                
                with open(file_path, 'r', encoding='utf-8') as infile:
                    # คัดลอกเนื้อหาทั้งหมด
                    outfile.write(infile.read())
    
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการรวมไฟล์: {e}")
        return None
    
    print(f"✅ รวมไฟล์เสร็จสิ้น! ไฟล์ผลลัพธ์: {output_file}")
    return output_file


def main():
    """
    ฟังก์ชันหลักสำหรับรันโปรแกรม
    """
    print("=" * 50)
    print("โปรแกรมแบ่งและรวมไฟล์ข้อความ")
    print("=" * 50)
    
    while True:
        print("\nเลือกการทำงาน:")
        print("1. แบ่งไฟล์ข้อความ")
        print("2. รวมไฟล์ข้อความ")
        print("3. ออกจากโปรแกรม")
        
        choice = input("\nกรุณาเลือก (1-3): ").strip()
        
        if choice == "1":
            # แบ่งไฟล์
            input_file = input("กรุณาใส่ชื่อไฟล์ที่ต้องการแบ่ง: ").strip()
            
            # ตรวจสอบว่าไฟล์มีอยู่จริง
            if not os.path.exists(input_file):
                print(f"ไม่พบไฟล์: {input_file}")
                continue
            
            # ถามจำนวนบรรทัดต่อไฟล์
            try:
                lines_input = input("จำนวนบรรทัดต่อไฟล์ (กด Enter สำหรับ 500): ").strip()
                lines_per_file = int(lines_input) if lines_input else 500
                
                if lines_per_file <= 0:
                    print("จำนวนบรรทัดต้องมากกว่า 0")
                    continue
                    
            except ValueError:
                print("กรุณาใส่ตัวเลขที่ถูกต้อง")
                continue
            
            # ถามเกี่ยวกับการสร้างโฟลเดอร์
            create_folder_input = input("สร้างโฟลเดอร์ใหม่สำหรับเก็บไฟล์ที่แบ่ง? (Y/n): ").strip().lower()
            create_folder = create_folder_input != 'n' and create_folder_input != 'no'
            
            # ทำการแบ่งไฟล์
            try:
                result = split_text_file(input_file, lines_per_file, create_folder=create_folder)
                output_files, output_dir = result
                
                if output_files:
                    print(f"\n📋 สร้างไฟล์สำเร็จ:")
                    for i, file_path in enumerate(output_files, 1):
                        print(f"  {i}. {os.path.basename(file_path)}")
                    
                    if output_dir:
                        print(f"\n💡 เคล็ดลับ: สำหรับการรวมไฟล์ใช้รูปแบบ:")
                        folder_name = os.path.basename(output_dir)
                        base_name = folder_name.split('_split_')[0]
                        print(f"   รูปแบบไฟล์: {base_name}_part_*.txt")
                        print(f"   โฟลเดอร์ต้นทาง: {folder_name}")
                else:
                    print("ไม่สามารถแบ่งไฟล์ได้")
                    
            except Exception as e:
                print(f"เกิดข้อผิดพลาด: {e}")
        
        elif choice == "2":
            # รวมไฟล์
            print("\n📂 ตัวอย่างรูปแบบไฟล์:")
            print("  filename_part_*.txt (สำหรับไฟล์ที่ขึ้นต้นด้วย filename_part_)")
            print("  *.txt (สำหรับไฟล์ .txt ทั้งหมด)")
            
            # ถามเกี่ยวกับโฟลเดอร์ต้นทาง
            use_folder = input("\nไฟล์อยู่ในโฟลเดอร์ที่แบ่งไว้หรือไม่? (y/N): ").strip().lower()
            source_folder = None
            
            if use_folder in ['y', 'yes', 'ใช่']:
                source_folder = input("กรุณาใส่ชื่อโฟลเดอร์: ").strip()
                if not source_folder or not os.path.exists(source_folder):
                    print("ไม่พบโฟลเดอร์ที่ระบุ จะค้นหาในโฟลเดอร์ปัจจุบัน")
                    source_folder = None
            
            file_pattern = input("กรุณาใส่รูปแบบชื่อไฟล์ที่ต้องการรวม: ").strip()
            
            if not file_pattern:
                print("กรุณาใส่รูปแบบชื่อไฟล์")
                continue
            
            # ชื่อไฟล์ผลลัพธ์
            output_file = input("ชื่อไฟล์ผลลัพธ์ (กด Enter สำหรับชื่ออัตโนมัติ): ").strip()
            output_file = output_file if output_file else None
            
            # ทำการรวมไฟล์
            try:
                result_file = merge_text_files(file_pattern, output_file, source_folder)
                if result_file:
                    print(f"\n✅ รวมไฟล์สำเร็จ: {result_file}")
                else:
                    print("ไม่สามารถรวมไฟล์ได้")
                    
            except Exception as e:
                print(f"เกิดข้อผิดพลาด: {e}")
        
        elif choice == "3":
            print("ขอบคุณที่ใช้โปรแกรม!")
            break
        
        else:
            print("กรุณาเลือก 1-3 เท่านั้น")


if __name__ == "__main__":
    main()
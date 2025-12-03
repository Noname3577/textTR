#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translation Tab - GUI component for translating text files
Tab สำหรับแปลข้อความ

ไฟล์นี้ import TranslationTab จาก translation_manager เพื่อ
ใช้งานร่วมกับโครงสร้างใหม่ - เมื่อต้องการแยกโค้ดเต็มที่
ให้ copy โค้ด TranslationTab มาที่นี่

Note: TranslationTab มีขนาดใหญ่มาก (~1800 บรรทัด) จึงยังคงใช้จากไฟล์เดิม
"""

import os
import sys

# เพิ่ม parent directory ใน path สำหรับ import
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import TranslationTab, TranslationEngine, TranslationData จาก translation_manager เดิม
# เพื่อความเข้ากันได้ในช่วงเปลี่ยนผ่าน
try:
    # ลอง import จาก core และ data modules ใหม่ก่อน
    from core.translation_engine import TranslationEngine
    from data.translation_data import TranslationData
    print("✅ Loaded TranslationEngine and TranslationData from new modules")
except ImportError:
    # Fallback: import จากไฟล์เดิม
    pass

# TranslationTab ยังใช้จากไฟล์เดิมเนื่องจากขนาดใหญ่
# ในอนาคตจะย้ายมาที่นี่
from translation_manager import TranslationTab

__all__ = ['TranslationTab', 'TranslationEngine', 'TranslationData']

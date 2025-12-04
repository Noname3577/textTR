#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translation Manager Module for Text File Splitter & Merger GUI
โมดูลจัดการการแปลสำหรับแอปพลิเคชัน GUI แบ่งและรวมไฟล์ข้อความ

ไฟล์นี้เป็น wrapper สำหรับ backward compatibility
โค้ดจริงถูกแยกไปที่:
- core/translation_engine.py - TranslationEngine class
- data/translation_data.py - TranslationData class  
- gui/tabs/translation_tab.py - TranslationTab class
- gui/tabs/translation_tab_widgets.py - Widget creation methods
- gui/tabs/translation_tab_operations.py - Translation operations
- gui/tabs/translation_tab_dialogs.py - Dialog windows
"""

# Re-export all classes for backward compatibility
from core.translation_engine import TranslationEngine
from data.translation_data import TranslationData
from gui.tabs.translation_tab import TranslationTab

__all__ = ['TranslationEngine', 'TranslationData', 'TranslationTab']

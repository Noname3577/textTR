#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constants and configuration values for Text File Splitter & Merger GUI
ค่าคงที่และการกำหนดค่าสำหรับแอปพลิเคชัน GUI แบ่งและรวมไฟล์ข้อความ
"""

# Application Information
APP_NAME = "TestApp"
APP_VERSION = "3.0"
APP_TITLE = f"🔧 {APP_NAME} v{APP_VERSION}"

# Window Configuration
DEFAULT_WINDOW_SIZE = "900x700"
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600

# File Operations
DEFAULT_LINES_PER_FILE = 500
MIN_LINES_PER_FILE = 1
MAX_LINES_PER_FILE = 100000
DEFAULT_FILE_PATTERN = "*_part_*.txt"
SUPPORTED_FILE_TYPES = [
    ("Text files", "*.txt"),
    ("JSON files", "*.json"),
    ("CSV files", "*.csv"),
    ("Log files", "*.log"),
    ("All files", "*.*")
]

# Translation Configuration
DEFAULT_SOURCE_LANG = "auto"
DEFAULT_TARGET_LANG = "th"
SUPPORTED_LANGUAGES = [
    ("อัตโนมัติ", "auto"),
    ("ไทย", "th"),
    ("English", "en"),
    ("日本語", "ja"),
    ("한국어", "ko"),
    ("中文", "zh"),
    ("Français", "fr"),
    ("Deutsch", "de"),
    ("Español", "es"),
    ("Italiano", "it"),
    ("Русский", "ru")
]

# Pagination Settings
DEFAULT_LINES_PER_PAGE = 10
MIN_LINES_PER_PAGE = 5
MAX_LINES_PER_PAGE = 50
PAGE_SIZE_OPTIONS = [5, 10, 15, 20, 25, 50]

# UI Styling
STYLES = {
    'title_font': ('Arial', 14, 'bold'),
    'section_font': ('Arial', 12, 'bold'),
    'default_font': ('Arial', 10),
    'monospace_font': ('Consolas', 10),
    'success_color': '#2d8a2f',
    'error_color': '#d32f2f',
    'info_color': '#1976d2',
    'warning_color': '#f57c00'
}

# File Patterns
SPLIT_FOLDER_PATTERN = "*_split_*"
PART_FILE_PATTERN = "*_part_*"
BACKUP_SUFFIX = ".backup"

# Auto-refresh Settings
AUTO_REFRESH_INTERVAL = 2000  # milliseconds
MAX_FILE_SIZE_FOR_AUTO_REFRESH = 10 * 1024 * 1024  # 10MB

# Translation Progress
TRANSLATION_BATCH_SIZE = 10
TRANSLATION_DELAY = 100  # milliseconds between translations

# Emojis for UI
EMOJIS = {
    'file': '📄',
    'folder': '📁',
    'merge': '📋',
    'split': '🔧',
    'view': '👁️',
    'translate': '🌐',
    'settings': '⚙️',
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'loading': '⏳',
    'save': '💾',
    'refresh': '🔄',
    'search': '🔍',
    'clean': '🧹',
    'edit': '✏️',
    'navigation': {
        'first': '⏮️',
        'prev': '◀️',
        'next': '▶️',
        'last': '⏭️',
        'jump': '🎯'
    },
    'skip': '🚫',
    'unskip': '✅',
    'toggle': '🔄'
}

# Status Messages
STATUS_MESSAGES = {
    'ready': f"{EMOJIS['success']} พร้อมใช้งาน",
    'working': f"{EMOJIS['loading']} กำลังทำงาน...",
    'splitting': f"{EMOJIS['split']} กำลังแบ่งไฟล์...",
    'merging': f"{EMOJIS['merge']} กำลังรวมไฟล์...",
    'translating': f"{EMOJIS['translate']} กำลังแปลข้อความ...",
    'saving': f"{EMOJIS['save']} กำลังบันทึก...",
    'loading': f"{EMOJIS['loading']} กำลังโหลด...",
    'complete': f"{EMOJIS['success']} เสร็จสิ้น!",
    'error': f"{EMOJIS['error']} เกิดข้อผิดพลาด"
}

# Error Messages
ERROR_MESSAGES = {
    'file_not_found': "ไม่พบไฟล์ที่ระบุ",
    'file_not_selected': "กรุณาเลือกไฟล์",
    'invalid_lines_per_file': f"จำนวนบรรทัดต่อไฟล์ต้องอยู่ระหว่าง {MIN_LINES_PER_FILE} - {MAX_LINES_PER_FILE}",
    'no_files_to_merge': "ไม่พบไฟล์ที่ตรงกับรูปแบบที่กำหนด",
    'translation_failed': "การแปลล้มเหลว",
    'save_failed': "การบันทึกล้มเหลว",
    'load_failed': "การโหลดไฟล์ล้มเหลว"
}

# Success Messages
SUCCESS_MESSAGES = {
    'file_split': "แบ่งไฟล์สำเร็จ",
    'files_merged': "รวมไฟล์สำเร็จ",
    'translation_complete': "แปลข้อความสำเร็จ",
    'file_saved': "บันทึกไฟล์สำเร็จ",
    'settings_saved': "บันทึกการตั้งค่าสำเร็จ"
}

# File Extensions
TEXT_EXTENSIONS = ['.txt', '.csv', '.log', '.md', '.json', '.xml']
BACKUP_EXTENSIONS = ['.bak', '.backup', '.old']

# Limits and Thresholds
MAX_DISPLAY_LINES = 1000
MAX_FILE_SIZE_MB = 100
MAX_TRANSLATION_LENGTH = 5000
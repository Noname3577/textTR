#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translation Manager Module for Text File Splitter & Merger GUI
โมดูลจัดการการแปลสำหรับแอปพลิเคชัน GUI แบ่งและรวมไฟล์ข้อความ
"""

import threading
import time
from typing import List, Dict, Any, Optional, Callable
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from gui_base import BaseTabComponent
from constants import (
    DEFAULT_SOURCE_LANG,
    DEFAULT_TARGET_LANG,
    SUPPORTED_LANGUAGES,
    DEFAULT_LINES_PER_PAGE,
    PAGE_SIZE_OPTIONS,
    EMOJIS,
    TRANSLATION_DELAY,
    TRANSLATION_BATCH_SIZE
)
from utils import (
    read_file_lines,
    write_file_lines,
    validate_file_path,
    get_page_items,
    calculate_pagination,
    create_backup_file
)


class TranslationEngine:
    """
    เครื่องมือแปลข้อความที่รองรับหลายวิธี รวมทั้ง AI Gemini
    """
    
    def __init__(self, gemini_api_key=None, gemini_model="gemini-2.5-flash", protection_patterns=None):
        self.gemini_api_key = gemini_api_key
        self.gemini_model = gemini_model
        self.protection_patterns = protection_patterns or ['curly_braces', 'square_brackets']
        self.gemini_translator = None
        
        # ลำดับการลอง engines (Gemini จะเป็นตัวเลือกแรกถ้าตั้งค่า API key)
        self.engines = []
        
        # เพิ่ม Gemini ถ้ามี API key
        if self.gemini_api_key:
            self.engines.append(self._try_gemini)
        
        # เพิ่ม engines อื่นๆ
        self.engines.extend([
            self._try_googletrans,
            self._try_deep_translator,
            self._try_google_api,
            self._simple_translate
        ])
        
        # เตรียม Gemini translator
        if self.gemini_api_key:
            self._initialize_gemini()
    
    def translate(self, text: str, source_lang: str = 'auto', target_lang: str = 'th', 
                  prompt_type: str = 'general', custom_prompt: str = None, 
                  translate_only_after_separator: bool = False, custom_separator: str = ':') -> str:
        """
        แปลข้อความ (ลองหลายวิธี)
        
        Args:
            text: ข้อความที่จะแปล
            source_lang: ภาษาต้นฉบับ
            target_lang: ภาษาเป้าหมาย
            prompt_type: ประเภท prompt สำหรับ Gemini ('general', 'novel', 'game', etc.)
            custom_prompt: custom prompt สำหรับ Gemini
            translate_only_after_separator: แปลเฉพาะข้อความหลังเครื่องหมายแบ่ง
            custom_separator: เครื่องหมายแบ่ง (เช่น ':', '=', '|', '->')
            
        Returns:
            ข้อความที่แปลแล้ว
        """
        if not text or not text.strip():
            return text
        
        # ลองแต่ละ engine จนกว่าจะสำเร็จ
        for engine in self.engines:
            try:
                # ส่ง prompt parameters สำหรับ Gemini
                if engine == self._try_gemini:
                    result = engine(text, source_lang, target_lang, prompt_type, custom_prompt, translate_only_after_separator, custom_separator)
                else:
                    # สำหรับ engines อื่นๆ ใช้วิธีง่ายๆ
                    if translate_only_after_separator and custom_separator in text:
                        # แยกส่วนหลังเครื่องหมายแบ่ง
                        separator_index = text.find(custom_separator)
                        prefix = text[:separator_index + len(custom_separator)]
                        suffix = text[separator_index + len(custom_separator):].strip()
                        
                        if suffix:
                            translated_suffix = engine(suffix, source_lang, target_lang)
                            if translated_suffix and translated_suffix != suffix:
                                # เพิ่มช่องว่างหลังเครื่องหมายแบ่งถ้ายังไม่มี
                                if not prefix.endswith(' '):
                                    result = f"{prefix} {translated_suffix}".strip()
                                else:
                                    result = f"{prefix}{translated_suffix}".strip()
                            else:
                                result = text
                        else:
                            result = text
                    else:
                        result = engine(text, source_lang, target_lang)
                
                if result and result != text:
                    return result
            except Exception:
                continue
        
        # ถ้าแปลไม่ได้ให้ส่งกลับข้อความเดิม
        return text
    
    def _initialize_gemini(self) -> None:
        """เตรียม Gemini translator"""
        try:
            from ai_translator import create_gemini_translator
            self.gemini_translator = create_gemini_translator(
                self.gemini_api_key, self.gemini_model, self.protection_patterns
            )
        except ImportError:
            print("ไม่สามารถ import ai_translator ได้")
        except Exception as e:
            print(f"การเตรียม Gemini translator ล้มเหลว: {e}")
    
    def _try_gemini(self, text: str, source_lang: str, target_lang: str, 
                   prompt_type: str = 'general', custom_prompt: str = None, 
                   translate_only_after_separator: bool = False, custom_separator: str = ':') -> str:
        """ลองใช้ Google Gemini AI"""
        if not self.gemini_translator:
            raise Exception("Gemini translator ไม่พร้อมใช้งาน")
        
        try:
            result = self.gemini_translator.translate_text(
                text, source_lang, target_lang, prompt_type, custom_prompt, 
                protect_special_text=True, translate_only_after_separator=translate_only_after_separator, 
                custom_separator=custom_separator
            )
            return result
        except Exception as e:
            raise Exception(f"Gemini translation failed: {e}")
    
    def is_gemini_available(self) -> bool:
        """ตรวจสอบว่า Gemini พร้อมใช้งานหรือไม่"""
        return self.gemini_translator is not None and self.gemini_translator.is_ready()
    
    def test_gemini_connection(self) -> tuple:
        """ทดสอบการเชื่อมต่อ Gemini"""
        if not self.gemini_translator:
            return False, "Gemini translator ไม่ได้เตรียมไว้"
        
        return self.gemini_translator.test_connection()
    
    def get_gemini_prompts(self) -> dict:
        """ดึงรายการ prompt ที่มีใน Gemini"""
        if not self.gemini_translator:
            return {}
        
        return self.gemini_translator.get_available_prompts()
    
    def _try_googletrans(self, text: str, source_lang: str, target_lang: str) -> str:
        """ลองใช้ googletrans library"""
        try:
            from googletrans import Translator
            translator = Translator()
            
            if source_lang == 'auto':
                result = translator.translate(text, dest=target_lang)
            else:
                result = translator.translate(text, src=source_lang, dest=target_lang)
            
            return result.text
        except ImportError:
            raise Exception("googletrans not installed")
        except Exception as e:
            raise Exception(f"googletrans failed: {e}")
    
    def _try_deep_translator(self, text: str, source_lang: str, target_lang: str) -> str:
        """ลองใช้ deep-translator library"""
        try:
            from deep_translator import GoogleTranslator
            
            if source_lang == 'auto':
                translator = GoogleTranslator(target=target_lang)
            else:
                translator = GoogleTranslator(source=source_lang, target=target_lang)
            
            return translator.translate(text)
        except ImportError:
            raise Exception("deep-translator not installed")
        except Exception as e:
            raise Exception(f"deep-translator failed: {e}")
    
    def _try_google_api(self, text: str, source_lang: str, target_lang: str) -> str:
        """ลองใช้ Google Translate API แบบไม่ต้อง key"""
        try:
            import requests
            import json
            
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': source_lang,
                'tl': target_lang,
                'dt': 't',
                'q': text
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result and len(result) > 0 and len(result[0]) > 0:
                    return result[0][0][0]
            
            raise Exception("API request failed")
        except ImportError:
            raise Exception("requests not installed")
        except Exception as e:
            raise Exception(f"Google API failed: {e}")
    
    def _simple_translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """การแปลแบบง่ายๆ สำหรับคำพื้นฐาน"""
        # Dictionary สำหรับคำพื้นฐาน
        basic_dict = {
            ('en', 'th'): {
                'hello': 'สวัสดี', 'world': 'โลก', 'the': '', 'a': '', 'an': '',
                'and': 'และ', 'or': 'หรือ', 'yes': 'ใช่', 'no': 'ไม่',
                'good': 'ดี', 'bad': 'แย่', 'big': 'ใหญ่', 'small': 'เล็ก',
                'new': 'ใหม่', 'old': 'เก่า', 'hot': 'ร้อน', 'cold': 'เย็น',
                'water': 'น้ำ', 'fire': 'ไฟ', 'earth': 'โลก', 'air': 'อากาศ'
            },
            ('th', 'en'): {
                'สวัสดี': 'hello', 'โลก': 'world', 'และ': 'and', 'หรือ': 'or',
                'ใช่': 'yes', 'ไม่': 'no', 'ดี': 'good', 'แย่': 'bad',
                'ใหญ่': 'big', 'เล็ก': 'small', 'ใหม่': 'new', 'เก่า': 'old',
                'ร้อน': 'hot', 'เย็น': 'cold', 'น้ำ': 'water', 'ไฟ': 'fire',
                'อากาศ': 'air'
            }
        }
        
        # หาคำในพจนานุกรม
        dict_key = (source_lang, target_lang)
        if dict_key in basic_dict:
            words = text.lower().split()
            translated_words = []
            
            for word in words:
                if word in basic_dict[dict_key]:
                    translated = basic_dict[dict_key][word]
                    if translated:  # ถ้าไม่ใช่ string ว่าง
                        translated_words.append(translated)
                else:
                    translated_words.append(word)
            
            if translated_words:
                return ' '.join(translated_words)
        
        # ถ้าแปลไม่ได้ให้แสดงข้อความแจ้งเตือน
        return f"[ต้องติดตั้ง translation library เพื่อแปลจาก {source_lang} เป็น {target_lang}]: {text}"


class TranslationData:
    """
    คลาสสำหรับจัดการข้อมูลการแปล
    """
    
    def __init__(self):
        self.lines: List[Dict[str, Any]] = []
        self.file_path: Optional[str] = None
    
    def load_from_file(self, file_path: str) -> bool:
        """โหลดไฟล์สำหรับแปล"""
        if not validate_file_path(file_path):
            return False
        
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
                    'skip_translation': False  # เพิ่มฟิลด์สำหรับกำหนดไม่ให้แปล
                })
            
            self.file_path = file_path
            return True
            
        except Exception:
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
        """บันทึกการแปลลงไฟล์"""
        target_file = file_path or self.file_path
        if not target_file:
            return False
        
        try:
            # สร้าง backup ถ้าเป็นไฟล์เดิม
            if target_file == self.file_path:
                create_backup_file(target_file)
            
            # เตรียมบรรทัดสำหรับบันทึก
            output_lines = []
            for line_data in self.lines:
                if line_data['is_translated'] and line_data['translated'].strip():
                    output_lines.append(line_data['translated'] + '\n')
                else:
                    output_lines.append(line_data['original'] + '\n')
            
            return write_file_lines(target_file, output_lines)
            
        except Exception:
            return False


class TranslationTab(BaseTabComponent):
    """
    Tab สำหรับการแปลข้อความในไฟล์
    """
    
    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        
        # ตัวแปรสำหรับเก็บค่าต่างๆ
        self.variables = {
            'file_path': tk.StringVar(),
            'source_lang': tk.StringVar(value=DEFAULT_SOURCE_LANG),
            'target_lang': tk.StringVar(value=DEFAULT_TARGET_LANG),
            'lines_per_page': tk.IntVar(value=DEFAULT_LINES_PER_PAGE),
            'current_page': tk.IntVar(value=1),
            'total_pages': tk.IntVar(value=0),
            'selected_line': tk.IntVar(value=-1),
            # Gemini settings
            'gemini_api_key': tk.StringVar(),
            'gemini_model': tk.StringVar(value="gemini-2.5-flash"),
            'use_gemini': tk.BooleanVar(value=False),
            'gemini_prompt_type': tk.StringVar(value='general'),
            'custom_prompt': tk.StringVar(),
            # Text Protection settings
            'enable_text_protection': tk.BooleanVar(value=True),
            'protection_patterns': {},  # Will be populated with BooleanVar for each pattern
            # Separator Translation settings
            'translate_only_after_separator': tk.BooleanVar(value=False),
            'custom_separator': tk.StringVar(value=':')
        }
        
        # ข้อมูลการแปล
        self.translation_data = TranslationData()
        self.translation_engine = None  # จะถูกสร้างใหม่เมื่อมีการตั้งค่า Gemini
        
        # สถานะ
        self.cancel_translation = False
        
        self.create_widgets()
    
    def create_widgets(self) -> None:
        """สร้าง widgets สำหรับ tab แปลข้อความ"""
        
        # Main frame for notebook tab
        self.frame = ttk.Frame(self.parent)
        
        # Main scrollable frame
        main_canvas = tk.Canvas(self.frame)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        # Configure scrollable frame updates
        def configure_scroll_region(event=None):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
        def configure_canvas_width(event=None):
            # Make scrollable frame width match canvas width
            canvas_width = event.width if event else main_canvas.winfo_width()
            main_canvas.itemconfig(scroll_window, width=canvas_width)
        
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        main_canvas.bind("<Configure>", configure_canvas_width)
        
        # Create window in canvas  
        scroll_window = main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        main_canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Change frame reference to scrollable frame for content
        self.content_frame = scrollable_frame
        
        # Title
        title_label = ttk.Label(
            self.content_frame, 
            text=f"{EMOJIS['translate']} แปลข้อความ (Grid View)", 
            style='Title.TLabel'
        )
        title_label.pack(pady=(5, 10))
        
        # File selection section
        self._create_file_section()
        
        # Language settings section
        self._create_language_section()
        
        # Gemini AI section
        self._create_gemini_section()
        
        # Pagination section
        self._create_pagination_section()
        
        # Grid display section
        self._create_grid_section()
        
        # Edit section
        self._create_edit_section()
        
        # Status bar
        self.create_status_bar(self.content_frame)
    
    def _create_file_section(self) -> None:
        """สร้างส่วนเลือกไฟล์"""
        file_frame = ttk.LabelFrame(self.content_frame, text=f"{EMOJIS['folder']} ไฟล์", padding=5)
        file_frame.pack(fill='x', padx=10, pady=(0, 5))
        
        file_input_frame = ttk.Frame(file_frame)
        file_input_frame.pack(fill='x')
        
        self.widgets['file_entry'] = ttk.Entry(
            file_input_frame, 
            textvariable=self.variables['file_path']
        )
        self.widgets['file_entry'].pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        ttk.Button(
            file_input_frame, 
            text=f"{EMOJIS['folder']}", 
            command=self.browse_file_for_translation
        ).pack(side='right')
    
    def _create_language_section(self) -> None:
        """สร้างส่วนการตั้งค่าภาษา"""
        lang_frame = ttk.LabelFrame(self.content_frame, text=f"{EMOJIS['translate']} ภาษา", padding=5)
        lang_frame.pack(fill='x', padx=10, pady=(0, 5))
        
        lang_controls = ttk.Frame(lang_frame)
        lang_controls.pack(fill='x')
        
        # Source language
        ttk.Label(lang_controls, text="จาก:").pack(side='left')
        source_combo = ttk.Combobox(
            lang_controls, 
            textvariable=self.variables['source_lang'], 
            width=8, 
            state='readonly'
        )
        source_combo['values'] = [lang[1] for lang in SUPPORTED_LANGUAGES]
        source_combo.pack(side='left', padx=(2, 10))
        
        # Target language
        ttk.Label(lang_controls, text="เป็น:").pack(side='left')
        target_combo = ttk.Combobox(
            lang_controls, 
            textvariable=self.variables['target_lang'], 
            width=8, 
            state='readonly'
        )
        target_combo['values'] = [lang[1] for lang in SUPPORTED_LANGUAGES[1:]]  # ไม่รวม 'auto'
        target_combo.pack(side='left', padx=(2, 10))
        
        # Swap button
        ttk.Button(
            lang_controls, 
            text=f"{EMOJIS['refresh']}", 
            command=self.swap_languages
        ).pack(side='right')
    
    def _create_gemini_section(self) -> None:
        """สร้างส่วนตั้งค่า Gemini AI"""
        gemini_frame = ttk.LabelFrame(self.content_frame, text=f"🤖 Gemini AI Settings", padding=5)
        gemini_frame.pack(fill='x', padx=10, pady=(0, 5))
        
        # Enable Gemini checkbox
        enable_frame = ttk.Frame(gemini_frame)
        enable_frame.pack(fill='x', pady=(0, 3))
        
        ttk.Checkbutton(
            enable_frame,
            text="ใช้ Gemini AI สำหรับการแปล",
            variable=self.variables['use_gemini'],
            command=self.toggle_gemini_settings
        ).pack(side='left')
        
        # Status label
        self.widgets['gemini_status'] = ttk.Label(enable_frame, text="ยังไม่ได้ตั้งค่า", foreground='red')
        self.widgets['gemini_status'].pack(side='right')
        
        # API Key section
        api_frame = ttk.Frame(gemini_frame)
        api_frame.pack(fill='x', pady=(3, 0))
        
        ttk.Label(api_frame, text="API Key:").pack(side='left')
        self.widgets['gemini_api_entry'] = ttk.Entry(
            api_frame, 
            textvariable=self.variables['gemini_api_key'],
            show='*',  # Hide API key
            width=30
        )
        self.widgets['gemini_api_entry'].pack(side='left', padx=(5, 5), fill='x', expand=True)
        
        ttk.Button(api_frame, text="ทดสอบ", command=self.test_gemini_connection).pack(side='right', padx=(0, 5))
        ttk.Button(api_frame, text="บันทึก", command=self.save_gemini_settings).pack(side='right')
        
        # Model and Prompt section
        settings_frame = ttk.Frame(gemini_frame)
        settings_frame.pack(fill='x', pady=(3, 0))
        
        # Model selection
        ttk.Label(settings_frame, text="Model:").pack(side='left')
        model_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.variables['gemini_model'],
            width=15,
            state='readonly',
            values=['gemini-2.5-flash', 'gemini-1.5-pro', 'gemini-1.5-flash']
        )
        model_combo.pack(side='left', padx=(5, 10))
        
        # Prompt type selection
        ttk.Label(settings_frame, text="ประเภทการแปล:").pack(side='left')
        self.widgets['prompt_combo'] = ttk.Combobox(
            settings_frame,
            textvariable=self.variables['gemini_prompt_type'],
            width=12,
            state='readonly'
        )
        self.widgets['prompt_combo'].pack(side='left', padx=(5, 10))
        
        # Custom prompt button
        ttk.Button(
            settings_frame, 
            text="Custom Prompt", 
            command=self.show_custom_prompt_dialog
        ).pack(side='right')
        
        # Text Protection section
        self._create_text_protection_section(gemini_frame)
        
        # Separator Translation section
        self._create_separator_translation_section(gemini_frame)
        
        # Initialize prompt types
        self._update_prompt_types()
        
        # Initialize translation engine
        self._initialize_translation_engine()
    
    def _create_pagination_section(self) -> None:
        """สร้างส่วนการแบ่งหน้า"""
        page_frame = ttk.LabelFrame(self.content_frame, text=f"{EMOJIS['file']} หน้า", padding=5)
        page_frame.pack(fill='x', padx=10, pady=(0, 5))
        
        # Page size controls
        size_frame = ttk.Frame(page_frame)
        size_frame.pack(fill='x', pady=(0, 3))
        
        ttk.Label(size_frame, text="แสดง:").pack(side='left')
        
        lines_spinbox = ttk.Spinbox(
            size_frame, 
            from_=5, 
            to=50, 
            width=5, 
            textvariable=self.variables['lines_per_page'],
            command=self.update_grid_display
        )
        lines_spinbox.pack(side='left', padx=(2, 5))
        
        # Quick page size buttons
        for size in [5, 10, 15]:
            ttk.Button(
                size_frame, 
                text=str(size), 
                width=2, 
                command=lambda s=size: self.set_page_size(s)
            ).pack(side='left', padx=1)
        
        # Page navigation
        nav_controls = ttk.Frame(page_frame)
        nav_controls.pack(fill='x')
        
        # Navigation buttons
        ttk.Button(nav_controls, text="⏪", width=3, command=self.goto_first_page).pack(side='left', padx=1)
        ttk.Button(nav_controls, text="◀", width=2, command=self.goto_prev_page).pack(side='left', padx=1)
        
        # Page info
        self.widgets['page_info'] = ttk.Label(nav_controls, text="0/0", width=8)
        self.widgets['page_info'].pack(side='left', padx=5)
        
        ttk.Button(nav_controls, text="▶", width=2, command=self.goto_next_page).pack(side='left', padx=1)
        ttk.Button(nav_controls, text="⏩", width=3, command=self.goto_last_page).pack(side='left', padx=1)
        
        # Jump to page
        self.widgets['page_jump_entry'] = ttk.Entry(nav_controls, width=4)
        self.widgets['page_jump_entry'].pack(side='left', padx=(10, 2))
        ttk.Button(nav_controls, text="ไป", width=3, command=self.jump_to_page).pack(side='left')
        
        self.widgets['page_jump_entry'].bind('<Return>', lambda e: self.jump_to_page())
    
    def _create_grid_section(self) -> None:
        """สร้างส่วนแสดงตาราง"""
        grid_frame = ttk.LabelFrame(self.content_frame, text=f"{EMOJIS['info']} ตาราง", padding=5)
        grid_frame.pack(fill='both', expand=True, padx=10, pady=(0, 5))
        
        # คำแนะนำการใช้งาน
        help_frame = ttk.Frame(grid_frame)
        help_frame.pack(fill='x', padx=5, pady=(0, 5))
        
        help_label = ttk.Label(
            help_frame, 
            text="💡 คลิกที่คอลัมน์ 'ข้าม' เพื่อปิด/เปิดการแปลบรรทัดนั้น | คลิกที่บรรทัดอื่นเพื่อเลือกและแก้ไข | ใช้ฟีเจอร์แปลเฉพาะหลัง : สำหรับไฟล์เกม",
            font=('Arial', 9),
            foreground='gray'
        )
        help_label.pack()
        
        # Create container frame for proper packing
        tree_container = ttk.Frame(grid_frame)
        tree_container.pack(fill='both', expand=True)
        
        # Create Treeview
        columns = ('line_no', 'skip', 'original', 'translated', 'status')
        self.widgets['tree'] = ttk.Treeview(tree_container, columns=columns, show='headings', height=8)
        
        # Define headings
        self.widgets['tree'].heading('line_no', text='#')
        self.widgets['tree'].heading('skip', text='ข้าม')
        self.widgets['tree'].heading('original', text='ต้นฉบับ')
        self.widgets['tree'].heading('translated', text='แปล')
        self.widgets['tree'].heading('status', text='สถานะ')
        
        # Define column widths
        self.widgets['tree'].column('line_no', width=40, minwidth=30)
        self.widgets['tree'].column('skip', width=50, minwidth=40)
        self.widgets['tree'].column('original', width=280, minwidth=200)
        self.widgets['tree'].column('translated', width=280, minwidth=200)
        self.widgets['tree'].column('status', width=80, minwidth=60)
        
        # Add scrollbars  
        tree_scrollbar_y = ttk.Scrollbar(tree_container, orient='vertical', command=self.widgets['tree'].yview)
        tree_scrollbar_x = ttk.Scrollbar(tree_container, orient='horizontal', command=self.widgets['tree'].xview)
        self.widgets['tree'].configure(yscrollcommand=tree_scrollbar_y.set, xscrollcommand=tree_scrollbar_x.set)
        
        # Pack scrollbars first, then treeview
        tree_scrollbar_y.pack(side='right', fill='y')
        tree_scrollbar_x.pack(side='bottom', fill='x')
        self.widgets['tree'].pack(side='left', fill='both', expand=True)
        
        # Bind events
        self.widgets['tree'].bind('<Button-1>', self.on_tree_click)
        self.widgets['tree'].bind('<Double-1>', self.on_tree_double_click)
        
        # เพิ่มคำแนะนำการใช้งาน
        self.widgets['tree'].bind('<Motion>', self.on_tree_motion)
    
    def _create_edit_section(self) -> None:
        """สร้างส่วนแก้ไข"""
        edit_frame = ttk.LabelFrame(self.content_frame, text=f"{EMOJIS['edit']} แก้ไข", padding=5)
        edit_frame.pack(fill='x', padx=10, pady=(0, 5))
        
        # Current line info
        self.widgets['current_line_info'] = ttk.Label(edit_frame, text="ยังไม่เลือก", style='Section.TLabel')
        self.widgets['current_line_info'].pack(anchor='w', pady=(0, 3))
        
        # Original text
        ttk.Label(edit_frame, text="ต้นฉบับ:").pack(anchor='w')
        self.widgets['original_text'] = tk.Text(edit_frame, height=2, wrap='word', state='disabled', bg='#f5f5f5')
        self.widgets['original_text'].pack(fill='x', pady=(0, 5))
        
        # Translated text
        ttk.Label(edit_frame, text="แปล:").pack(anchor='w')
        self.widgets['translated_text'] = tk.Text(edit_frame, height=2, wrap='word')
        self.widgets['translated_text'].pack(fill='x', pady=(0, 5))
        
        # Skip toggle
        skip_frame = ttk.Frame(edit_frame)
        skip_frame.pack(fill='x', pady=(0, 5))
        
        self.widgets['skip_checkbox'] = ttk.Checkbutton(
            skip_frame,
            text="ข้ามบรรทัดนี้ (ไม่แปลเมื่อแปลทั้งไฟล์)",
            command=self.toggle_skip_selected_line
        )
        self.widgets['skip_checkbox'].pack(side='left')
        
        # ปุ่มช่วยเหลือ
        ttk.Button(
            skip_frame,
            text="❓",
            width=3,
            command=self.show_skip_help
        ).pack(side='right')
        
        # Action buttons
        self._create_action_buttons(edit_frame)
    
    def _create_action_buttons(self, parent: ttk.Frame) -> None:
        """สร้างปุ่มดำเนินการ"""
        
        # Row 1: Individual actions
        row1 = ttk.Frame(parent)
        row1.pack(fill='x', pady=(0, 2))
        
        ttk.Button(row1, text=f"{EMOJIS['translate']} แปลบรรทัดนี้", command=self.translate_selected_line).pack(side='left', padx=(0, 5))
        ttk.Button(row1, text=f"{EMOJIS['save']} บันทึกบรรทัดนี้", command=self.save_selected_line).pack(side='left', padx=(0, 5))
        ttk.Button(row1, text="↩️ รีเซ็ต", command=self.reset_selected_line).pack(side='left', padx=(0, 5))
        ttk.Button(row1, text=f"{EMOJIS['refresh']} รีเฟรชตาราง", command=self.refresh_grid).pack(side='right')
        
        # Row 2: Batch actions
        row2 = ttk.Frame(parent)
        row2.pack(fill='x', pady=(2, 0))
        
        ttk.Button(row2, text=f"{EMOJIS['translate']} แปลหน้านี้ทั้งหมด", command=self.translate_current_page).pack(side='left', padx=(0, 5))
        ttk.Button(row2, text=f"{EMOJIS['translate']} แปลไฟล์ทั้งหมด", command=self.translate_all_file).pack(side='left', padx=(0, 5))
        ttk.Button(row2, text=f"{EMOJIS['info']} ดูสถานะการแปล", command=self.show_translation_status).pack(side='right')
        
        # Row 3: Skip management
        row3 = ttk.Frame(parent)
        row3.pack(fill='x', pady=(2, 0))
        
        ttk.Button(row3, text="🚫 ข้ามหน้านี้ทั้งหมด", command=self.skip_current_page).pack(side='left', padx=(0, 5))
        ttk.Button(row3, text="✅ เปิดหน้านี้ทั้งหมด", command=self.unskip_current_page).pack(side='left', padx=(0, 5))
        ttk.Button(row3, text="🔄 สลับสถานะหน้านี้", command=self.toggle_current_page).pack(side='left', padx=(0, 5))
        
        # Row 4: Save actions
        row4 = ttk.Frame(parent)
        row4.pack(fill='x', pady=(2, 0))
        
        ttk.Button(row4, text=f"{EMOJIS['save']} บันทึกทั้งไฟล์", command=self.save_all_translations).pack(side='left', padx=(0, 5))
        ttk.Button(row4, text=f"{EMOJIS['file']} บันทึกเป็นไฟล์ใหม่", command=self.save_as_new_file).pack(side='left')
    
    # === File Operations ===
    
    def browse_file_for_translation(self) -> None:
        """เลือกไฟล์สำหรับแปล"""
        filename = self.browse_file('open_text')
        if filename:
            self.variables['file_path'].set(filename)
            self.load_file_for_translation()
    
    def load_file_for_translation(self) -> None:
        """โหลดไฟล์สำหรับแปล"""
        file_path = self.variables['file_path'].get()
        
        if not self.validate_file_exists(file_path):
            return
        
        if self.translation_data.load_from_file(file_path):
            self.variables['current_page'].set(1)
            self.update_grid_display()
            self.update_status(f"โหลดไฟล์สำเร็จ: {self.translation_data.get_line_count():,} บรรทัด")
        else:
            self.show_error("ไม่สามารถโหลดไฟล์ได้")
    
    # === Language Operations ===
    
    def swap_languages(self) -> None:
        """สลับภาษาต้นฉบับและเป้าหมาย"""
        source = self.variables['source_lang'].get()
        target = self.variables['target_lang'].get()
        
        if source != 'auto':
            self.variables['source_lang'].set(target)
            self.variables['target_lang'].set(source)
    
    def _create_text_protection_section(self, parent_frame: ttk.Frame) -> None:
        """สร้างส่วนตั้งค่า Text Protection"""
        protection_frame = ttk.LabelFrame(parent_frame, text="🛡️ ป้องกันข้อความพิเศษ", padding=5)
        protection_frame.pack(fill='x', pady=(5, 0))
        
        # Enable text protection checkbox
        enable_frame = ttk.Frame(protection_frame)
        enable_frame.pack(fill='x', pady=(0, 3))
        
        ttk.Checkbutton(
            enable_frame,
            text="เปิดใช้การป้องกันข้อความพิเศษ (เช่น {คำสั่งเกม}, [แท็ก])",
            variable=self.variables['enable_text_protection'],
            command=self.toggle_text_protection
        ).pack(side='left')
        
        # Pattern selection frame
        pattern_frame = ttk.Frame(protection_frame)
        pattern_frame.pack(fill='both', expand=True, pady=(3, 0))
        
        # Get available patterns and create checkboxes
        try:
            from ai_translator import TextProtector
            temp_protector = TextProtector()
            available_patterns = temp_protector.get_available_patterns()
            
            # Create grid layout for patterns
            row = 0
            col = 0
            max_cols = 3
            
            for pattern_name, description in available_patterns.items():
                # Create BooleanVar for this pattern
                pattern_var = tk.BooleanVar(value=pattern_name in ['curly_braces', 'square_brackets'])
                self.variables['protection_patterns'][pattern_name] = pattern_var
                
                # Create checkbox
                cb = ttk.Checkbutton(
                    pattern_frame,
                    text=description,
                    variable=pattern_var,
                    command=self.update_protection_settings
                )
                cb.grid(row=row, column=col, sticky='w', padx=(0, 10), pady=1)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
                    
        except ImportError:
            # Fallback if ai_translator not available
            ttk.Label(pattern_frame, text="TextProtector ไม่พร้อมใช้งาน").pack()
        
        # Custom patterns section
        custom_frame = ttk.Frame(protection_frame)
        custom_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Button(
            custom_frame,
            text="เพิ่ม Pattern เอง",
            command=self.show_custom_pattern_dialog
        ).pack(side='left')
        
        ttk.Button(
            custom_frame,
            text="ทดสอบการป้องกัน",
            command=self.test_text_protection
        ).pack(side='left', padx=(5, 0))
    
    # === Gemini Operations ===
    
    def toggle_gemini_settings(self) -> None:
        """เปิด/ปิดการใช้งาน Gemini"""
        use_gemini = self.variables['use_gemini'].get()
        
        # Enable/disable Gemini related widgets
        state = 'normal' if use_gemini else 'disabled'
        
        if 'gemini_api_entry' in self.widgets:
            self.widgets['gemini_api_entry'].config(state=state)
        if 'prompt_combo' in self.widgets:
            self.widgets['prompt_combo'].config(state=state)
        
        # Update translation engine
        self._initialize_translation_engine()
    
    def save_gemini_settings(self) -> None:
        """บันทึกการตั้งค่า Gemini"""
        api_key = self.variables['gemini_api_key'].get().strip()
        
        if not api_key:
            self.show_error("กรุณาใส่ Gemini API Key")
            return
        
        # Validate API key format
        try:
            from ai_translator import validate_api_key
            if not validate_api_key(api_key):
                self.show_error("รูปแบบ API Key ไม่ถูกต้อง")
                return
        except ImportError:
            pass  # Skip validation if module not available
        
        # Update translation engine
        self._initialize_translation_engine()
        
        # Test connection
        self.test_gemini_connection()
    
    def test_gemini_connection(self) -> None:
        """ทดสอบการเชื่อมต่อ Gemini"""
        if not self.translation_engine:
            self.show_error("กรุณาบันทึกการตั้งค่า Gemini ก่อน")
            return
        
        try:
            success, message = self.translation_engine.test_gemini_connection()
            
            if success:
                self.widgets['gemini_status'].config(text="เชื่อมต่อสำเร็จ", foreground='green')
                self.show_success(message)
            else:
                self.widgets['gemini_status'].config(text="เชื่อมต่อล้มเหลว", foreground='red')
                self.show_error(message)
                
        except Exception as e:
            self.widgets['gemini_status'].config(text="เกิดข้อผิดพลาด", foreground='red')
            self.show_error(f"การทดสอบล้มเหลว: {e}")
    
    def show_custom_prompt_dialog(self) -> None:
        """แสดง dialog สำหรับแก้ไข custom prompt"""
        # Create dialog window
        dialog = tk.Toplevel(self.parent.winfo_toplevel())
        dialog.title("Custom Prompt สำหรับ Gemini")
        dialog.geometry("600x400")
        dialog.transient(self.parent.winfo_toplevel())
        dialog.grab_set()
        
        # Center dialog
        dialog.geometry("+%d+%d" % (
            dialog.winfo_toplevel().winfo_x() + 50,
            dialog.winfo_toplevel().winfo_y() + 50
        ))
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Instructions
        ttk.Label(
            main_frame,
            text="กำหนด Custom Prompt สำหรับการแปลด้วย Gemini AI:",
            font=('TkDefaultFont', 10, 'bold')
        ).pack(anchor='w', pady=(0, 5))
        
        ttk.Label(
            main_frame,
            text="เคล็ดลับ: อธิบายบทบาท สไตล์การแปล และข้อกำหนดพิเศษที่ต้องการ",
            foreground='gray'
        ).pack(anchor='w', pady=(0, 10))
        
        # Text area
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        text_area = scrolledtext.ScrolledText(text_frame, wrap='word', height=15)
        text_area.pack(fill='both', expand=True)
        
        # Load current custom prompt
        current_prompt = self.variables['custom_prompt'].get()
        if current_prompt:
            text_area.insert('1.0', current_prompt)
        
        # Example prompts
        examples_frame = ttk.LabelFrame(main_frame, text="ตัวอย่าง Prompts", padding=5)
        examples_frame.pack(fill='x', pady=(0, 10))
        
        examples = [
            ("นิยาย", "คุณเป็นนักแปลนิยายมืออาชีพ แปลให้มีอารมณ์และบรรยากาศที่สวยงาม"),
            ("เกม", "คุณเป็นนักแปลเกมมืออาชีพ รักษาบรรยากาศการผจญภัยและคำศัพท์เกม"),
            ("สนทนา", "คุณเป็นนักแปลบทสนทนา แปลให้ธรรมชาติและเข้าใจง่าย")
        ]
        
        for name, prompt in examples:
            btn = ttk.Button(
                examples_frame,
                text=f"ใช้ {name}",
                command=lambda p=prompt: [text_area.delete('1.0', tk.END), text_area.insert('1.0', p)]
            )
            btn.pack(side='left', padx=(0, 5))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        def save_prompt():
            custom_prompt = text_area.get('1.0', tk.END).strip()
            self.variables['custom_prompt'].set(custom_prompt)
            dialog.destroy()
            self.show_success("บันทึก Custom Prompt แล้ว")
        
        def clear_prompt():
            self.variables['custom_prompt'].set('')
            dialog.destroy()
            self.show_success("ลบ Custom Prompt แล้ว")
        
        ttk.Button(button_frame, text="บันทึก", command=save_prompt).pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="ยกเลิก", command=dialog.destroy).pack(side='right')
        ttk.Button(button_frame, text="ล้าง", command=clear_prompt).pack(side='left')
        
        # Focus on text area
        text_area.focus_set()
    
    def _create_separator_translation_section(self, parent_frame: ttk.Frame) -> None:
        """สร้างส่วนตั้งค่าการแปลเฉพาะหลังเครื่องหมายแบ่ง"""
        separator_frame = ttk.LabelFrame(parent_frame, text="📍 การแปลเฉพาะส่วนที่ต้องการ", padding=5)
        separator_frame.pack(fill='x', pady=(5, 0))
        
        # Enable separator translation checkbox
        enable_frame = ttk.Frame(separator_frame)
        enable_frame.pack(fill='x', pady=(0, 3))
        
        ttk.Checkbutton(
            enable_frame,
            text="แปลเฉพาะข้อความหลังเครื่องหมายแบ่งเท่านั้น",
            variable=self.variables['translate_only_after_separator'],
            command=self.update_separator_translation_settings
        ).pack(side='left')
        
        # Help button
        ttk.Button(
            enable_frame,
            text="❓",
            width=3,
            command=self.show_separator_translation_help
        ).pack(side='right')
        
        # Separator selection frame
        separator_select_frame = ttk.Frame(separator_frame)
        separator_select_frame.pack(fill='x', pady=(3, 0))
        
        ttk.Label(separator_select_frame, text="เครื่องหมายแบ่ง:").pack(side='left')
        
        # Separator combobox
        separator_combo = ttk.Combobox(
            separator_select_frame,
            textvariable=self.variables['custom_separator'],
            width=8,
            values=[':' , '=', '|', '->', '=>', '~', '#', '@']
        )
        separator_combo.pack(side='left', padx=(5, 5))
        separator_combo.bind('<<ComboboxSelected>>', self.on_separator_changed)
        
        # Custom separator entry
        ttk.Label(separator_select_frame, text="หรือกำหนดเอง:").pack(side='left', padx=(10, 0))
        custom_entry = ttk.Entry(separator_select_frame, textvariable=self.variables['custom_separator'], width=10)
        custom_entry.pack(side='left', padx=(5, 0))
        
        # Example frame (dynamic)
        self.widgets['example_frame'] = ttk.Frame(separator_frame)
        self.widgets['example_frame'].pack(fill='x', pady=(3, 0))
        
        # Example label (will be updated dynamically)
        self.widgets['example_label'] = ttk.Label(
            self.widgets['example_frame'],
            text="ตัวอย่าง: 'Cook_1: Fried Rice' จะแปลเฉพาะ 'Fried Rice' → 'Cook_1: ข้าวผัด'",
            font=('Arial', 9),
            foreground='#666666'
        )
        self.widgets['example_label'].pack(anchor='w')
        
        # Test area
        test_frame = ttk.LabelFrame(separator_frame, text="ทดสอบฟีเจอร์", padding=3)
        test_frame.pack(fill='x', pady=(3, 0))
        
        # Test input
        test_input_frame = ttk.Frame(test_frame)
        test_input_frame.pack(fill='x', pady=(0, 2))
        
        ttk.Label(test_input_frame, text="ทดสอบ:").pack(side='left')
        self.widgets['separator_test_entry'] = ttk.Entry(test_input_frame, width=30)
        self.widgets['separator_test_entry'].pack(side='left', padx=(5, 5), fill='x', expand=True)
        self.widgets['separator_test_entry'].insert(0, "Player_01: Hello World")
        
        ttk.Button(
            test_input_frame,
            text="ทดสอบ",
            command=self.test_separator_translation
        ).pack(side='right')
        
        # Test result
        self.widgets['separator_test_result'] = ttk.Label(
            test_frame,
            text="ผลลัพธ์จะแสดงที่นี่",
            font=('Arial', 9),
            foreground='#0066cc',
            wraplength=400
        )
        self.widgets['separator_test_result'].pack(anchor='w')
        
        # Update example initially
        self.update_separator_example()
    
    def _update_prompt_types(self) -> None:
        """อัปเดตรายการประเภท prompt"""
        try:
            if self.translation_engine and self.translation_engine.is_gemini_available():
                prompts = self.translation_engine.get_gemini_prompts()
                self.widgets['prompt_combo']['values'] = list(prompts.keys())
            else:
                # Default prompt types
                default_prompts = ['general', 'novel', 'game', 'dialogue', 'technical', 'formal']
                self.widgets['prompt_combo']['values'] = default_prompts
        except Exception:
            # Fallback
            default_prompts = ['general', 'novel', 'game', 'dialogue', 'technical', 'formal']
            self.widgets['prompt_combo']['values'] = default_prompts
    
    def _initialize_translation_engine(self) -> None:
        """เตรียม Translation Engine"""
        use_gemini = self.variables['use_gemini'].get()
        
        if use_gemini:
            api_key = self.variables['gemini_api_key'].get().strip()
            model = self.variables['gemini_model'].get()
            
            if api_key:
                # ดึงรายการ protection patterns ที่เลือก
                enabled_patterns = []
                for pattern_name, pattern_var in self.variables['protection_patterns'].items():
                    if pattern_var.get():
                        enabled_patterns.append(pattern_name)
                
                self.translation_engine = TranslationEngine(api_key, model, enabled_patterns)
                
                # Update status
                if self.translation_engine.is_gemini_available():
                    self.widgets['gemini_status'].config(text="พร้อมใช้งาน", foreground='green')
                else:
                    self.widgets['gemini_status'].config(text="ไม่พร้อมใช้งาน", foreground='red')
            else:
                self.translation_engine = TranslationEngine()  # Without Gemini
                self.widgets['gemini_status'].config(text="ไม่ได้ใส่ API Key", foreground='orange')
        else:
            self.translation_engine = TranslationEngine()  # Without Gemini
            if 'gemini_status' in self.widgets:
                self.widgets['gemini_status'].config(text="ปิดการใช้งาน", foreground='gray')
        
        # Update prompt types
        if 'prompt_combo' in self.widgets:
            self._update_prompt_types()
    
    # === Text Protection Operations ===
    
    def toggle_text_protection(self) -> None:
        """เปิด/ปิดการใช้งาน Text Protection"""
        self.update_protection_settings()
    
    def update_protection_settings(self) -> None:
        """อัปเดตการตั้งค่า Text Protection"""
        if self.translation_engine and self.translation_engine.is_gemini_available():
            # ดึงรายการ patterns ที่เลือก
            enabled_patterns = []
            for pattern_name, pattern_var in self.variables['protection_patterns'].items():
                if pattern_var.get():
                    enabled_patterns.append(pattern_name)
            
            # ตั้งค่า patterns ใน Gemini translator
            self.translation_engine.gemini_translator.set_protection_patterns(enabled_patterns)
    
    def show_custom_pattern_dialog(self) -> None:
        """แสดง dialog สำหรับเพิ่ม custom protection pattern"""
        # Create dialog window
        dialog = tk.Toplevel(self.parent.winfo_toplevel())
        dialog.title("เพิ่ม Protection Pattern")
        dialog.geometry("500x300")
        dialog.transient(self.parent.winfo_toplevel())
        dialog.grab_set()
        
        # Center dialog
        dialog.geometry("+%d+%d" % (
            dialog.winfo_toplevel().winfo_x() + 50,
            dialog.winfo_toplevel().winfo_y() + 50
        ))
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Instructions
        ttk.Label(
            main_frame,
            text="เพิ่ม Custom Protection Pattern:",
            font=('TkDefaultFont', 10, 'bold')
        ).pack(anchor='w', pady=(0, 5))
        
        # Name input
        ttk.Label(main_frame, text="ชื่อ Pattern:").pack(anchor='w')
        name_entry = ttk.Entry(main_frame, width=40)
        name_entry.pack(fill='x', pady=(0, 5))
        
        # Pattern input
        ttk.Label(main_frame, text="Regex Pattern:").pack(anchor='w')
        pattern_entry = ttk.Entry(main_frame, width=40)
        pattern_entry.pack(fill='x', pady=(0, 5))
        
        # Examples
        examples_frame = ttk.LabelFrame(main_frame, text="ตัวอย่าง Patterns", padding=5)
        examples_frame.pack(fill='both', expand=True, pady=(5, 10))
        
        examples_text = """ตัวอย่าง Regex Patterns:
• \\{[^}]*\\}          - ข้อความในปีกกา {text}
• \\[[^\\]]*\\]         - ข้อความในวงเล็บเหลี่ยม [text]
• \\$\\w+              - ตัวแปร $variable
• \\b\\d+\\s*HP\\b      - ค่า HP (เช่น 100 HP)
• \\b[A-Z]+\\b          - คำที่เป็นตัวพิมพ์ใหญ่ทั้งหมด
• \\b\\w+_\\w+\\b       - คำที่มี underscore"""
        
        examples_label = tk.Text(examples_frame, height=8, wrap='word', bg='#f5f5f5')
        examples_label.pack(fill='both', expand=True)
        examples_label.insert('1.0', examples_text)
        examples_label.config(state='disabled')
        
        # Test frame
        test_frame = ttk.Frame(main_frame)
        test_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(test_frame, text="ทดสอบ:").pack(side='left')
        test_entry = ttk.Entry(test_frame, width=30)
        test_entry.pack(side='left', padx=(5, 5), fill='x', expand=True)
        
        def test_pattern():
            pattern = pattern_entry.get().strip()
            test_text = test_entry.get().strip()
            
            if not pattern or not test_text:
                self.show_error("กรุณาใส่ pattern และข้อความทดสอบ")
                return
            
            try:
                import re
                matches = re.findall(pattern, test_text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    self.show_success(f"พบการจับคู่: {matches}")
                else:
                    self.show_success("ไม่พบการจับคู่")
            except re.error as e:
                self.show_error(f"Regex ไม่ถูกต้อง: {e}")
        
        ttk.Button(test_frame, text="ทดสอบ", command=test_pattern).pack(side='right')
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        def save_pattern():
            name = name_entry.get().strip()
            pattern = pattern_entry.get().strip()
            
            if not name or not pattern:
                self.show_error("กรุณาใส่ชื่อและ pattern")
                return
            
            # Test pattern validity
            try:
                import re
                re.compile(pattern)
            except re.error as e:
                self.show_error(f"Regex ไม่ถูกต้อง: {e}")
                return
            
            # Add to translator
            if self.translation_engine and self.translation_engine.is_gemini_available():
                self.translation_engine.gemini_translator.add_custom_protection_pattern(name, pattern)
                
                # Add checkbox to UI
                pattern_var = tk.BooleanVar(value=True)
                self.variables['protection_patterns'][name] = pattern_var
                
                dialog.destroy()
                self.show_success(f"เพิ่ม pattern '{name}' แล้ว")
            else:
                self.show_error("Gemini translator ไม่พร้อมใช้งาน")
        
        ttk.Button(button_frame, text="เพิ่ม", command=save_pattern).pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="ยกเลิก", command=dialog.destroy).pack(side='right')
        
        # Focus on name entry
        name_entry.focus_set()
    
    def test_text_protection(self) -> None:
        """ทดสอบการป้องกันข้อความ"""
        # Create dialog window
        dialog = tk.Toplevel(self.parent.winfo_toplevel())
        dialog.title("ทดสอบการป้องกันข้อความ")
        dialog.geometry("600x400")
        dialog.transient(self.parent.winfo_toplevel())
        dialog.grab_set()
        
        # Center dialog
        dialog.geometry("+%d+%d" % (
            dialog.winfo_toplevel().winfo_x() + 50,
            dialog.winfo_toplevel().winfo_y() + 50
        ))
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Instructions
        ttk.Label(
            main_frame,
            text="ทดสอบการป้องกันข้อความ:",
            font=('TkDefaultFont', 10, 'bold')
        ).pack(anchor='w', pady=(0, 5))
        
        # Input text
        ttk.Label(main_frame, text="ข้อความทดสอบ:").pack(anchor='w')
        input_text = scrolledtext.ScrolledText(main_frame, height=4, wrap='word')
        input_text.pack(fill='x', pady=(0, 5))
        
        # Default test text
        default_text = "Hello {player_name}! You have [100 HP] and $gold coins. Visit <shop> or use %skill%."
        input_text.insert('1.0', default_text)
        
        # Results area
        ttk.Label(main_frame, text="ผลลัพธ์:").pack(anchor='w', pady=(10, 0))
        
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Protected text
        ttk.Label(results_frame, text="ข้อความที่ป้องกัน:").pack(anchor='w')
        protected_text = scrolledtext.ScrolledText(results_frame, height=3, wrap='word', bg='#e8f5e8')
        protected_text.pack(fill='x', pady=(0, 5))
        
        # Protected items
        ttk.Label(results_frame, text="รายการที่ถูกป้องกัน:").pack(anchor='w')
        protected_items = scrolledtext.ScrolledText(results_frame, height=4, wrap='word', bg='#f0f0f0')
        protected_items.pack(fill='both', expand=True)
        
        def run_test():
            test_text = input_text.get('1.0', tk.END).strip()
            
            if not test_text:
                self.show_error("กรุณาใส่ข้อความทดสอบ")
                return
            
            if not (self.translation_engine and self.translation_engine.is_gemini_available()):
                self.show_error("Gemini translator ไม่พร้อมใช้งาน")
                return
            
            try:
                # Get text protector
                text_protector = self.translation_engine.gemini_translator.get_text_protector()
                
                # Update protection settings
                self.update_protection_settings()
                
                # Protect text
                protected, placeholders = text_protector.protect_text(test_text)
                
                # Show results
                protected_text.delete('1.0', tk.END)
                protected_text.insert('1.0', protected)
                
                items_text = ""
                if placeholders:
                    for placeholder, original in placeholders.items():
                        items_text += f"{placeholder} → {original}\n"
                else:
                    items_text = "ไม่มีข้อความที่ถูกป้องกัน"
                
                protected_items.delete('1.0', tk.END)
                protected_items.insert('1.0', items_text)
                
            except Exception as e:
                self.show_error(f"การทดสอบล้มเหลว: {e}")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="ทดสอบ", command=run_test).pack(side='left')
        ttk.Button(button_frame, text="ปิด", command=dialog.destroy).pack(side='right')
        
        # Run initial test
        run_test()
    
    def update_separator_translation_settings(self) -> None:
        """อัปเดตการตั้งค่าการแปลเฉพาะหลังเครื่องหมายแบ่ง"""
        pass  # ไม่ต้องทำอะไรพิเศษ ค่าจะถูกใช้ตอนแปล
    
    def on_separator_changed(self, event=None) -> None:
        """เมื่อมีการเปลี่ยนเครื่องหมายแบ่ง"""
        self.update_separator_example()
        self.update_separator_test_example()
    
    def update_separator_example(self) -> None:
        """อัปเดตตัวอย่างการใช้งานตามเครื่องหมายแบ่งที่เลือก"""
        separator = self.variables['custom_separator'].get()
        
        examples = {
            ':': "ตัวอย่าง: 'Cook_1: Fried Rice' จะแปลเฉพาะ 'Fried Rice' → 'Cook_1: ข้าวผัด'",
            '=': "ตัวอย่าง: 'Name=John Smith' จะแปลเฉพาะ 'John Smith' → 'Name=จอห์น สมิธ'",
            '|': "ตัวอย่าง: 'Label|Hello World' จะแปลเฉพาะ 'Hello World' → 'Label|สวัสดีชาวโลก'",
            '->': "ตัวอย่าง: 'Key->Welcome Message' จะแปลเฉพาะ 'Welcome Message' → 'Key->ข้อความต้อนรับ'",
            '=>': "ตัวอย่าง: 'ID=>Description Text' จะแปลเฉพาะ 'Description Text' → 'ID=>ข้อความอธิบาย'",
            '~': "ตัวอย่าง: 'Type~Action Text' จะแปลเฉพาะ 'Action Text' → 'Type~ข้อความการดำเนินการ'",
            '#': "ตัวอย่าง: 'Section#Content Here' จะแปลเฉพาะ 'Content Here' → 'Section#เนื้อหาที่นี่'",
            '@': "ตัวอย่าง: 'Tag@Display Text' จะแปลเฉพาะ 'Display Text' → 'Tag@ข้อความแสดง'"
        }
        
        example_text = examples.get(separator, f"ตัวอย่าง: 'ID{separator}Content' จะแปลเฉพาะ 'Content' → 'ID{separator}เนื้อหา'")
        
        if 'example_label' in self.widgets:
            self.widgets['example_label'].config(text=example_text)
    
    def update_separator_test_example(self) -> None:
        """อัปเดตตัวอย่างในช่องทดสอบตามเครื่องหมายแบ่งที่เลือก"""
        separator = self.variables['custom_separator'].get()
        
        test_examples = {
            ':': "Player_01: Hello World",
            '=': "PlayerName=Welcome Message",
            '|': "ItemID|Magic Sword",
            '->': "QuestName->Find the treasure",
            '=>': "SkillName=>Fire Attack",
            '~': "NPCType~Friendly Merchant",
            '#': "ConfigKey#Default Value",
            '@': "CommandID@Execute Action"
        }
        
        test_text = test_examples.get(separator, f"Example{separator}Test Content")
        
        if 'separator_test_entry' in self.widgets:
            current_text = self.widgets['separator_test_entry'].get()
            # อัปเดตเฉพาะเมื่อยังเป็นตัวอย่างเก่าอยู่
            if any(current_text.startswith(f"Player_01{s}") or current_text.startswith(f"PlayerName{s}") or 
                   current_text.startswith(f"ItemID{s}") for s in [':', '=', '|', '->', '=>', '~', '#', '@']):
                self.widgets['separator_test_entry'].delete(0, tk.END)
                self.widgets['separator_test_entry'].insert(0, test_text)
    
    def show_separator_translation_help(self) -> None:
        """แสดงหน้าต่างช่วยเหลือสำหรับฟีเจอร์การแปลเฉพาะหลังเครื่องหมายแบ่ง"""
        help_window = tk.Toplevel(self.parent.winfo_toplevel())
        help_window.title("วิธีใช้ฟีเจอร์การแปลเฉพาะส่วนที่ต้องการ")
        help_window.geometry("550x500")
        help_window.transient(self.parent.winfo_toplevel())
        help_window.grab_set()
        
        # Center dialog
        help_window.geometry("+%d+%d" % (
            help_window.winfo_toplevel().winfo_x() + 50,
            help_window.winfo_toplevel().winfo_y() + 50
        ))
        
        # Main frame
        main_frame = ttk.Frame(help_window, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="📍 ฟีเจอร์การแปลเฉพาะส่วนที่ต้องการ",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        
        # Close button
        ttk.Button(
            main_frame,
            text="ปิด",
            command=help_window.destroy
        ).pack(pady=5)
    
    def test_separator_translation(self) -> None:
        """ทดสอบฟีเจอร์การแปลเฉพาะหลังเครื่องหมายแบ่ง"""
        test_text = self.widgets['separator_test_entry'].get().strip()
        separator = self.variables['custom_separator'].get()
        
        if not test_text:
            self.widgets['separator_test_result'].config(
                text="กรุณาใส่ข้อความทดสอบ", 
                foreground='red'
            )
            return
        
        if not separator:
            self.widgets['separator_test_result'].config(
                text="กรุณาเลือกหรือกำหนดเครื่องหมายแบ่ง", 
                foreground='red'
            )
            return
        
        if separator not in test_text:
            self.widgets['separator_test_result'].config(
                text=f"ข้อความต้องมีเครื่องหมาย '{separator}' เพื่อทดสอบฟีเจอร์นี้", 
                foreground='red'
            )
            return
        
        try:
            # ทดสอบการแยกข้อความ
            separator_index = test_text.find(separator)
            prefix = test_text[:separator_index + len(separator)]
            suffix = test_text[separator_index + len(separator):].strip()
            
            if not suffix:
                self.widgets['separator_test_result'].config(
                    text=f"ไม่มีข้อความหลังเครื่องหมาย '{separator}'", 
                    foreground='orange'
                )
                return
            
            # แสดงผลการแยก
            result_text = f"ส่วนที่ไม่แปล: '{prefix}'\nส่วนที่จะแปล: '{suffix}'"
            
            # ถ้ามี translation engine ให้ลองแปลจริง
            if self.translation_engine:
                source_lang = self.variables['source_lang'].get()
                target_lang = self.variables['target_lang'].get()
                
                try:
                    translated = self.translation_engine.translate(
                        test_text, source_lang, target_lang, 
                        translate_only_after_separator=True, custom_separator=separator
                    )
                    result_text += f"\n\nผลการแปลจริง: '{translated}'"
                except Exception as e:
                    result_text += f"\n\nไม่สามารถแปลได้: {str(e)}"
            else:
                result_text += "\n\n(ไม่มี translation engine สำหรับทดสอบการแปลจริง)"
            
            self.widgets['separator_test_result'].config(
                text=result_text, 
                foreground='#0066cc'
            )
            
        except Exception as e:
            self.widgets['separator_test_result'].config(
                text=f"เกิดข้อผิดพลาด: {str(e)}", 
                foreground='red'
            )
    
    # === Pagination Operations ===
    
    def set_page_size(self, size: int) -> None:
        """ตั้งค่าจำนวนบรรทัดต่อหน้า"""
        self.variables['lines_per_page'].set(size)
        self.update_grid_display()
    
    def goto_first_page(self) -> None:
        """ไปหน้าแรก"""
        self.variables['current_page'].set(1)
        self.update_grid_display()
    
    def goto_last_page(self) -> None:
        """ไปหน้าสุดท้าย"""
        total_pages = self.variables['total_pages'].get()
        if total_pages > 0:
            self.variables['current_page'].set(total_pages)
            self.update_grid_display()
    
    def goto_prev_page(self) -> None:
        """ไปหน้าก่อน"""
        current = self.variables['current_page'].get()
        if current > 1:
            self.variables['current_page'].set(current - 1)
            self.update_grid_display()
    
    def goto_next_page(self) -> None:
        """ไปหน้าถัดไป"""
        current = self.variables['current_page'].get()
        total = self.variables['total_pages'].get()
        if current < total:
            self.variables['current_page'].set(current + 1)
            self.update_grid_display()
    
    def jump_to_page(self) -> None:
        """กระโดดไปหน้าที่กำหนด"""
        try:
            page = int(self.widgets['page_jump_entry'].get())
            total_pages = self.variables['total_pages'].get()
            
            if 1 <= page <= total_pages:
                self.variables['current_page'].set(page)
                self.update_grid_display()
            else:
                self.show_error(f"หมายเลขหน้าต้องอยู่ระหว่าง 1-{total_pages}")
        except ValueError:
            self.show_error("กรุณาใส่หมายเลขหน้าที่ถูกต้อง")
    
    def update_grid_display(self) -> None:
        """อัปเดตการแสดงผลตาราง"""
        if not self.translation_data.lines:
            return
        
        # คำนวณหน้าทั้งหมด
        lines_per_page = self.variables['lines_per_page'].get()
        total_pages, _ = calculate_pagination(len(self.translation_data.lines), lines_per_page)
        self.variables['total_pages'].set(total_pages)
        
        # ตรวจสอบหน้าปัจจุบัน
        current_page = self.variables['current_page'].get()
        if current_page > total_pages and total_pages > 0:
            current_page = total_pages
            self.variables['current_page'].set(current_page)
        
        # อัปเดตข้อมูลหน้า
        self.widgets['page_info'].config(text=f"{current_page}/{total_pages}")
        
        # ล้างตาราง
        for item in self.widgets['tree'].get_children():
            self.widgets['tree'].delete(item)
        
        # ดึงข้อมูลหน้าปัจจุบัน
        page_lines = get_page_items(self.translation_data.lines, current_page, lines_per_page)
        
        # เพิ่มข้อมูลลงตาราง
        for line_data in page_lines:
            # กำหนดสถานะและไอคอน
            if line_data['skip_translation']:
                status_icon = "🚫"
                skip_icon = "✓"
            elif line_data['is_translated']:
                status_icon = "✅"
                skip_icon = ""
            else:
                status_icon = "⏳"
                skip_icon = ""
            
            original_preview = line_data['original'][:45] + "..." if len(line_data['original']) > 45 else line_data['original']
            translated_preview = line_data['translated'][:45] + "..." if len(line_data['translated']) > 45 else line_data['translated']
            
            self.widgets['tree'].insert('', 'end', values=(
                line_data['line_number'],
                skip_icon,
                original_preview,
                translated_preview,
                status_icon
            ))
    
    # === Tree Events ===
    
    def on_tree_click(self, event) -> None:
        """จัดการเมื่อคลิกที่ตาราง"""
        try:
            # ใช้วิธีใหม่ที่ปลอดภัยกว่า
            # หาว่าคลิกที่บรรทัดไหน
            item_id = self.widgets['tree'].identify_row(event.y)
            if not item_id:
                return
            
            # เลือกรายการ
            self.widgets['tree'].selection_set(item_id)
            item = self.widgets['tree'].item(item_id)
            
            if not item['values']:
                return
            
            line_number = int(item['values'][0])
            line_index = line_number - 1
            
            if not (0 <= line_index < len(self.translation_data.lines)):
                return
            
            # ตรวจสอบว่าคลิกที่คอลัมน์ skip หรือไม่
            # ใช้วิธีคำนวณตำแหน่งแทน identify_column
            skip_column_detected = self._is_skip_column_click(event.x)
            
            if skip_column_detected:
                # คลิกที่คอลัมน์ skip
                self.toggle_skip_line(line_index)
            else:
                # คลิกที่คอลัมน์อื่น - เลือกบรรทัด
                self.variables['selected_line'].set(line_index)
                self.update_edit_area()
                        
        except Exception as e:
            # จัดการข้อผิดพลาด
            print(f"Tree click error: {e}")
            self._fallback_tree_click(event)
    
    def _is_skip_column_click(self, x_pos: int) -> bool:
        """ตรวจสอบว่าคลิกที่คอลัมน์ skip หรือไม่"""
        try:
            # คำนวณตำแหน่งคอลัมน์ skip (คอลัมน์ที่ 2)
            # คอลัมน์ที่ 1: # (width ~40)
            # คอลัมน์ที่ 2: ข้าม (width ~50) 
            col1_width = 40  # ความกว้างคอลัมน์ #
            col2_start = col1_width
            col2_end = col1_width + 50  # ความกว้างคอลัมน์ ข้าม
            
            return col2_start <= x_pos <= col2_end
        except Exception:
            return False
    
    def _fallback_tree_click(self, event) -> None:
        """วิธีสำรองสำหรับการคลิกตาราง"""
        try:
            selection = self.widgets['tree'].selection()
            if selection:
                item = self.widgets['tree'].item(selection[0])
                if item['values']:
                    line_number = int(item['values'][0])
                    line_index = line_number - 1
                    
                    if 0 <= line_index < len(self.translation_data.lines):
                        self.variables['selected_line'].set(line_index)
                        self.update_edit_area()
        except Exception:
            pass  # เงียบๆ หากเกิดข้อผิดพลาดซ้ำ
    
    def on_tree_motion(self, event) -> None:
        """แสดงคำแนะนำเมื่อเลื่อนเมาส์"""
        try:
            # ตรวจสอบว่าเมาส์อยู่ที่คอลัมน์ skip หรือไม่
            column = self.widgets['tree'].identify_column(event.x)
            if column == '#2':  # คอลัมน์ skip
                # เปลี่ยน cursor เป็น hand
                self.widgets['tree'].config(cursor="hand2")
                # อัปเดต status bar
                self.update_status("💡 คลิกที่คอลัมน์ 'ข้าม' เพื่อเปิด/ปิดการแปลบรรทัดนั้น")
            else:
                # cursor ปกติ
                self.widgets['tree'].config(cursor="")
        except Exception:
            # หากเกิดข้อผิดพลาด ให้ใช้ cursor ปกติ
            self.widgets['tree'].config(cursor="")
    
    def on_tree_double_click(self, event) -> None:
        """จัดการเมื่อดับเบิลคลิกที่ตาราง"""
        self.on_tree_click(event)
        self.widgets['translated_text'].focus_set()
    
    def update_edit_area(self) -> None:
        """อัปเดตพื้นที่แก้ไข"""
        selected_index = self.variables['selected_line'].get()
        
        if 0 <= selected_index < len(self.translation_data.lines):
            line_data = self.translation_data.lines[selected_index]
            
            # อัปเดตข้อมูลบรรทัด
            skip_text = " (ข้าม)" if line_data['skip_translation'] else ""
            self.widgets['current_line_info'].config(text=f"บรรทัดที่ {line_data['line_number']}{skip_text}")
            
            # อัปเดตข้อความต้นฉบับ
            self.widgets['original_text'].config(state='normal')
            self.widgets['original_text'].delete(1.0, tk.END)
            self.widgets['original_text'].insert(1.0, line_data['original'])
            self.widgets['original_text'].config(state='disabled')
            
            # อัปเดตข้อความแปล
            self.widgets['translated_text'].delete(1.0, tk.END)
            self.widgets['translated_text'].insert(1.0, line_data['translated'])
            
            # อัปเดต skip checkbox
            if 'skip_checkbox' in self.widgets:
                # ใช้ after เพื่อป้องกัน recursive call
                self.widgets['skip_checkbox'].after(1, lambda: self._update_skip_checkbox(line_data['skip_translation']))
        else:
            self.widgets['current_line_info'].config(text="ยังไม่เลือก")
            self.widgets['original_text'].config(state='normal')
            self.widgets['original_text'].delete(1.0, tk.END)
            self.widgets['original_text'].config(state='disabled')
            self.widgets['translated_text'].delete(1.0, tk.END)
            
            # รีเซ็ต skip checkbox
            if 'skip_checkbox' in self.widgets:
                self.widgets['skip_checkbox'].after(1, lambda: self._update_skip_checkbox(False))
    
    def _update_skip_checkbox(self, skip_value: bool) -> None:
        """อัปเดต skip checkbox อย่างปลอดภัย"""
        if 'skip_checkbox' in self.widgets:
            # ปิดการตอบสนองชั่วคราวเพื่อไม่ให้เกิด recursion
            current_command = self.widgets['skip_checkbox']['command']
            self.widgets['skip_checkbox'].config(command='')
            
            # อัปเดตค่า
            if skip_value:
                self.widgets['skip_checkbox'].state(['selected'])
            else:
                self.widgets['skip_checkbox'].state(['!selected'])
            
            # เปิดการตอบสนองคืน
            self.widgets['skip_checkbox'].config(command=current_command)
    
    # === Translation Operations ===
    
    def translate_selected_line(self) -> None:
        """แปลบรรทัดที่เลือก"""
        selected_index = self.variables['selected_line'].get()
        
        if selected_index == -1:
            self.show_error("กรุณาเลือกบรรทัดที่จะแปล")
            return
        
        if not (0 <= selected_index < len(self.translation_data.lines)):
            return
        
        line_data = self.translation_data.lines[selected_index]
        original_text = line_data['original']
        
        if not original_text.strip():
            self.show_error("บรรทัดนี้ไม่มีข้อความให้แปล")
            return
        
        try:
            source_lang = self.variables['source_lang'].get()
            target_lang = self.variables['target_lang'].get()
            
            self.update_status(f"กำลังแปลบรรทัดที่ {selected_index + 1}...")
            
            # เตรียม parameters สำหรับ Gemini
            prompt_type = self.variables['gemini_prompt_type'].get()
            custom_prompt = self.variables['custom_prompt'].get() if self.variables['custom_prompt'].get().strip() else None
            protect_text = self.variables['enable_text_protection'].get()
            translate_only_after_separator = self.variables['translate_only_after_separator'].get()
            custom_separator = self.variables['custom_separator'].get()
            
            # แปลข้อความ
            if self.translation_engine.is_gemini_available():
                # อัปเดตการตั้งค่าป้องกันข้อความ
                self.update_protection_settings()
                translated_text = self.translation_engine.gemini_translator.translate_text(
                    original_text, source_lang, target_lang, prompt_type, custom_prompt, 
                    protect_text, translate_only_after_separator, custom_separator
                )
            else:
                translated_text = self.translation_engine.translate(
                    original_text, source_lang, target_lang, prompt_type, custom_prompt,
                    translate_only_after_separator, custom_separator
                )
            
            # อัปเดตข้อมูล
            self.translation_data.translate_line(selected_index, translated_text)
            
            # อัปเดต UI
            self.widgets['translated_text'].delete(1.0, tk.END)
            self.widgets['translated_text'].insert(1.0, translated_text)
            
            # รีเฟรชตาราง
            self.refresh_grid()
            
            self.update_status(f"แปลบรรทัดที่ {selected_index + 1} เสร็จสิ้น")
            
        except Exception as e:
            self.show_error(f"การแปลล้มเหลว: {str(e)}")
    
    def save_selected_line(self) -> None:
        """บันทึกการแปลของบรรทัดที่เลือก"""
        selected_index = self.variables['selected_line'].get()
        
        if selected_index == -1:
            self.show_error("กรุณาเลือกบรรทัดที่จะบันทึก")
            return
        
        # ดึงข้อความแปลจากช่องแก้ไข
        translated_text = self.widgets['translated_text'].get(1.0, tk.END).strip()
        
        # อัปเดตข้อมูล
        self.translation_data.translate_line(selected_index, translated_text)
        
        # รีเฟรชตาราง
        self.refresh_grid()
        
        self.show_success(f"บันทึกการแปลบรรทัดที่ {selected_index + 1} แล้ว")
    
    def reset_selected_line(self) -> None:
        """รีเซ็ตการแปลของบรรทัดที่เลือก"""
        selected_index = self.variables['selected_line'].get()
        
        if selected_index == -1:
            return
        
        # รีเซ็ตการแปล
        self.translation_data.translate_line(selected_index, "")
        
        # อัปเดตพื้ที่แก้ไข
        self.widgets['translated_text'].delete(1.0, tk.END)
        
        # รีเฟรชตาราง
        self.refresh_grid()
    
    def toggle_skip_line(self, line_index: int) -> None:
        """เปิด/ปิดการข้ามการแปลของบรรทัด"""
        if not (0 <= line_index < len(self.translation_data.lines)):
            return
        
        line_data = self.translation_data.lines[line_index]
        
        # สลับสถานะการข้าม
        self.translation_data.toggle_skip_translation(line_index)
        
        # แสดงข้อความแจ้งเตือน
        if line_data['skip_translation']:  # หลังจากสลับแล้ว
            self.show_success(f"เปิดการแปลบรรทัดที่ {line_index + 1}")
        else:
            self.show_success(f"ปิดการแปลบรรทัดที่ {line_index + 1} (จะข้ามเมื่อแปลทั้งไฟล์)")
        
        # รีเฟรชตาราง
        self.refresh_grid()
        
        # อัปเดตพื้ที่แก้ไขถ้าบรรทัดนี้ถูกเลือกอยู่
        if self.variables['selected_line'].get() == line_index:
            self.update_edit_area()
    
    def toggle_skip_selected_line(self) -> None:
        """เปิด/ปิดการข้ามของบรรทัดที่เลือก (จาก checkbox)"""
        selected_index = self.variables['selected_line'].get()
        
        if selected_index == -1:
            self.show_error("กรุณาเลือกบรรทัดก่อน")
            return
        
        self.toggle_skip_line(selected_index)
    
    def translate_current_page(self) -> None:
        """แปลบรรทัดทั้งหมดในหน้าปัจจุบัน"""
        if not self.translation_data.lines:
            self.show_error("ไม่มีข้อมูลให้แปล")
            return
        
        # คำนวณช่วงบรรทัดในหน้าปัจจุบัน
        current_page = self.variables['current_page'].get()
        lines_per_page = self.variables['lines_per_page'].get()
        start_index = (current_page - 1) * lines_per_page
        end_index = min(start_index + lines_per_page, len(self.translation_data.lines))
        
        # หาบรรทัดที่ต้องแปล (ไม่รวมที่ข้าม)
        lines_to_translate = []
        skipped_lines = 0
        for i in range(start_index, end_index):
            line_data = self.translation_data.lines[i]
            if line_data['skip_translation']:
                skipped_lines += 1
                continue
            if not line_data['is_translated'] and line_data['original'].strip():
                lines_to_translate.append(i)
        
        if not lines_to_translate:
            message = "ไม่มีบรรทัดใหม่ที่ต้องแปลในหน้านี้"
            if skipped_lines > 0:
                message += f"\n(มีบรรทัดที่ข้าม {skipped_lines} บรรทัด)"
            self.show_success(message)
            return
        
        message = f"ต้องการแปล {len(lines_to_translate)} บรรทัดในหน้านี้หรือไม่?"
        if skipped_lines > 0:
            message += f"\n(จะข้าม {skipped_lines} บรรทัดที่ถูกปิด)"
        
        result = self.show_warning(message)
        if not result:
            return
        
        self._translate_lines_batch(lines_to_translate)
    
    def translate_all_file(self) -> None:
        """แปลบรรทัดทั้งหมดในไฟล์"""
        if not self.translation_data.lines:
            self.show_error("ไม่มีข้อมูลให้แปล")
            return
        
        # ใช้เมธอดใหม่ที่ข้ามบรรทัดที่ปิด
        lines_to_translate = self.translation_data.get_lines_to_translate()
        
        if not lines_to_translate:
            self.show_success("ไม่มีบรรทัดใหม่ที่ต้องแปล")
            return
        
        total_lines = len(self.translation_data.lines)
        skipped_count = self.translation_data.get_skipped_count()
        translated_count = self.translation_data.get_translated_count()
        
        message = f"พบบรรทัดที่ต้องแปล: {len(lines_to_translate)} บรรทัด\n"
        message += f"จากทั้งหมด: {total_lines} บรรทัด\n"
        if skipped_count > 0:
            message += f"บรรทัดที่ข้าม: {skipped_count} บรรทัด\n"
        if translated_count > 0:
            message += f"แปลแล้ว: {translated_count} บรรทัด\n"
        message += f"\nการแปลอาจใช้เวลานาน ต้องการดำเนินการต่อหรือไม่?"
        
        result = self.show_warning(message)
        
        if not result:
            return
        
        self._translate_lines_batch(lines_to_translate)
    
    def _translate_lines_batch(self, line_indices: List[int]) -> None:
        """แปลบรรทัดเป็นชุด"""
        if not line_indices:
            return
        
        # ป้องกันการใช้งานปุ่มอื่นขณะแปล
        self.set_working(True)
        self.cancel_translation = False
        
        # สร้าง progress dialog
        progress_dialog = self.create_progress_dialog(
            self.parent.winfo_toplevel(),
            "กำลังแปลไฟล์",
            f"เตรียมแปลทั้งหมด {len(line_indices)} บรรทัด..."
        )
        
        # เริ่มแปลในเทรดแยก
        thread = threading.Thread(target=self._translate_batch_thread, args=(line_indices,))
        thread.daemon = True
        thread.start()
    
    def _translate_batch_thread(self, line_indices: List[int]) -> None:
        """แปลบรรทัดในเทรดแยก"""
        success_count = 0
        error_count = 0
        total_count = len(line_indices)
        
        source_lang = self.variables['source_lang'].get()
        target_lang = self.variables['target_lang'].get()
        
        try:
            for i, line_index in enumerate(line_indices):
                if self.cancel_translation:
                    break
                
                try:
                    # อัปเดตความคืบหน้า
                    progress = (i / total_count) * 100
                    self.parent.after(0, self.update_progress_dialog, 
                                    f"แปลบรรทัดที่ {line_index + 1} ({i + 1}/{total_count})")
                    
                    # เตรียม parameters สำหรับ Gemini
                    prompt_type = self.variables['gemini_prompt_type'].get()
                    custom_prompt = self.variables['custom_prompt'].get() if self.variables['custom_prompt'].get().strip() else None
                    protect_text = self.variables['enable_text_protection'].get()
                    translate_only_after_separator = self.variables['translate_only_after_separator'].get()
                    custom_separator = self.variables['custom_separator'].get()
                    
                    # แปลข้อความ
                    line_data = self.translation_data.lines[line_index]
                    
                    if self.translation_engine.is_gemini_available():
                        # อัปเดตการตั้งค่าป้องกันข้อความ
                        self.update_protection_settings()
                        translated_text = self.translation_engine.gemini_translator.translate_text(
                            line_data['original'], source_lang, target_lang, prompt_type, custom_prompt, 
                            protect_text, translate_only_after_separator, custom_separator
                        )
                    else:
                        translated_text = self.translation_engine.translate(
                            line_data['original'], source_lang, target_lang, prompt_type, custom_prompt,
                            translate_only_after_separator, custom_separator
                        )
                    
                    # อัปเดตข้อมูล
                    self.translation_data.translate_line(line_index, translated_text)
                    success_count += 1
                    
                    # หน่วงเวลาเล็กน้อยเพื่อไม่ให้ถูกบล็อก
                    time.sleep(TRANSLATION_DELAY / 1000)
                    
                except Exception:
                    error_count += 1
                    continue
            
            # แจ้งผลลัพธ์
            self.parent.after(0, self._translation_batch_completed, success_count, error_count, total_count)
            
        except Exception as e:
            self.parent.after(0, self._translation_batch_completed, success_count, error_count, total_count, str(e))
    
    def _translation_batch_completed(self, success: int, error: int, total: int, exception: str = None) -> None:
        """เรียกเมื่อแปลชุดเสร็จสิ้น"""
        self.set_working(False)
        self.close_progress_dialog()
        
        # รีเฟรชตาราง
        self.refresh_grid()
        
        if exception:
            self.show_error(f"เกิดข้อผิดพลาด: {exception}")
            return
        
        message = f"แปลเสร็จสิ้น!\n\n"
        message += f"สำเร็จ: {success} บรรทัด\n"
        if error > 0:
            message += f"ล้มเหลว: {error} บรรทัด\n"
        message += f"รวม: {success + error} จาก {total} บรรทัด"
        
        self.show_success(message)
    
    # === File Save Operations ===
    
    def save_all_translations(self) -> None:
        """บันทึกการแปลทั้งหมดลงไฟล์เดิม"""
        if not self.translation_data.lines:
            self.show_error("ไม่มีข้อมูลให้บันทึก")
            return
        
        if self.translation_data.save_to_file():
            self.show_success("บันทึกการแปลลงไฟล์เดิมสำเร็จ")
        else:
            self.show_error("การบันทึกล้มเหลว")
    
    def save_as_new_file(self) -> None:
        """บันทึกการแปลเป็นไฟล์ใหม่"""
        if not self.translation_data.lines:
            self.show_error("ไม่มีข้อมูลให้บันทึก")
            return
        
        filename = self.browse_file('save_text')
        if not filename:
            return
        
        if self.translation_data.save_to_file(filename):
            self.show_success(f"บันทึกไฟล์ใหม่สำเร็จ: {os.path.basename(filename)}")
        else:
            self.show_error("การบันทึกล้มเหลว")
    
    # === Utility Methods ===
    
    def show_translation_status(self) -> None:
        """แสดงสถานะการแปล"""
        if not self.translation_data.lines:
            self.show_error("ไม่มีข้อมูลการแปล")
            return
        
        total_lines = self.translation_data.get_line_count()
        translated_lines = self.translation_data.get_translated_count()
        skipped_lines = self.translation_data.get_skipped_count()
        remaining_lines = len(self.translation_data.get_lines_to_translate())
        progress = self.translation_data.get_progress_percentage()
        
        # ตรวจสอบการใช้งานฟีเจอร์แปลเฉพาะหลังเครื่องหมายแบ่ง
        separator_mode = self.variables['translate_only_after_separator'].get()
        separator = self.variables['custom_separator'].get()
        separator_lines = 0
        if separator_mode:
            for line_data in self.translation_data.lines:
                if separator in line_data['original']:
                    separator_lines += 1
        
        status_text = f"""📊 สถานะการแปล

📄 จำนวนบรรทัดทั้งหมด: {total_lines:,}
✅ แปลแล้ว: {translated_lines:,} บรรทัด
🚫 ข้ามการแปล: {skipped_lines:,} บรรทัด
⏳ คงเหลือที่จะแปล: {remaining_lines:,} บรรทัด
📈 ความคืบหน้า: {progress:.1f}%"""

        if separator_mode:
            status_text += f"""

📍 โมดแปลเฉพาะหลังเครื่องหมายแบ่ง: เปิดใช้งาน
🔍 เครื่องหมายแบ่ง: '{separator}'
🔍 บรรทัดที่มีเครื่องหมายแบ่ง: {separator_lines:,} บรรทัด
💡 จะแปลเฉพาะส่วนหลัง '{separator}' เท่านั้น"""
        
        status_text += f"""

💡 คำแนะนำ:
• คลิกที่คอลัมน์ "ข้าม" เพื่อปิด/เปิดการแปล
• บรรทัดที่ข้ามจะไม่ถูกแปลเมื่อแปลทั้งไฟล์
• ใช้ checkbox ในส่วนแก้ไขเพื่อจัดการบรรทัดที่เลือก"""

        if separator_mode:
            status_text += f"""
• โมดแปลเฉพาะหลัง '{separator}' เหมาะสำหรับไฟล์เกมหรือ config files"""
        
        self.show_success(status_text)
    
    def refresh_grid(self) -> None:
        """รีเฟรชตาราง"""
        self.update_grid_display()
    
    def skip_current_page(self) -> None:
        """ข้ามการแปลทั้งหน้าปัจจุบัน"""
        if not self.translation_data.lines:
            self.show_error("ไม่มีข้อมูลให้ดำเนินการ")
            return
        
        # คำนวณช่วงบรรทัดในหน้าปัจจุบัน
        current_page = self.variables['current_page'].get()
        lines_per_page = self.variables['lines_per_page'].get()
        start_index = (current_page - 1) * lines_per_page
        end_index = min(start_index + lines_per_page, len(self.translation_data.lines))
        
        changed_count = 0
        for i in range(start_index, end_index):
            if not self.translation_data.lines[i]['skip_translation']:
                self.translation_data.toggle_skip_translation(i)
                changed_count += 1
        
        if changed_count > 0:
            self.show_success(f"ปิดการแปล {changed_count} บรรทัดในหน้านี้")
            self.refresh_grid()
        else:
            self.show_success("บรรทัดในหน้านี้ถูกปิดการแปลหมดแล้ว")
    
    def unskip_current_page(self) -> None:
        """เปิดการแปลทั้งหน้าปัจจุบัน"""
        if not self.translation_data.lines:
            self.show_error("ไม่มีข้อมูลให้ดำเนินการ")
            return
        
        # คำนวณช่วงบรรทัดในหน้าปัจจุบัน
        current_page = self.variables['current_page'].get()
        lines_per_page = self.variables['lines_per_page'].get()
        start_index = (current_page - 1) * lines_per_page
        end_index = min(start_index + lines_per_page, len(self.translation_data.lines))
        
        changed_count = 0
        for i in range(start_index, end_index):
            if self.translation_data.lines[i]['skip_translation']:
                self.translation_data.toggle_skip_translation(i)
                changed_count += 1
        
        if changed_count > 0:
            self.show_success(f"เปิดการแปล {changed_count} บรรทัดในหน้านี้")
            self.refresh_grid()
        else:
            self.show_success("บรรทัดในหน้านี้เปิดการแปลหมดแล้ว")
    
    def toggle_current_page(self) -> None:
        """สลับสถานะการแปลทั้งหน้าปัจจุบัน"""
        if not self.translation_data.lines:
            self.show_error("ไม่มีข้อมูลให้ดำเนินการ")
            return
        
        # คำนวณช่วงบรรทัดในหน้าปัจจุบัน
        current_page = self.variables['current_page'].get()
        lines_per_page = self.variables['lines_per_page'].get()
        start_index = (current_page - 1) * lines_per_page
        end_index = min(start_index + lines_per_page, len(self.translation_data.lines))
        
        changed_count = 0
        for i in range(start_index, end_index):
            self.translation_data.toggle_skip_translation(i)
            changed_count += 1
        
        if changed_count > 0:
            self.show_success(f"สลับสถานะ {changed_count} บรรทัดในหน้านี้")
            self.refresh_grid()
        else:
            self.show_success("ไม่มีบรรทัดให้สลับสถานะ")
    
    def show_skip_help(self) -> None:
        """แสดงหน้าต่างช่วยเหลือสำหรับฟีเจอร์การข้าม"""
        help_window = tk.Toplevel(self.parent.winfo_toplevel())
        help_window.title("วิธีใช้ฟีเจอร์การข้ามการแปล")
        help_window.geometry("500x600")
        help_window.transient(self.parent.winfo_toplevel())
        help_window.grab_set()
        
        # Center dialog
        help_window.geometry("+%d+%d" % (
            help_window.winfo_toplevel().winfo_x() + 50,
            help_window.winfo_toplevel().winfo_y() + 50
        ))
        
        # Main frame
        main_frame = ttk.Frame(help_window, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="🚫 ฟีเจอร์การข้ามการแปล",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 10))  
        
        # Close button
        ttk.Button(
            main_frame,
            text="ปิด",
            command=help_window.destroy
        ).pack(pady=5)


# เพิ่มฟังก์ชัน import ที่จำเป็น
import os
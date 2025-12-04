#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translation Tab - GUI component for translating text files
Tab สำหรับแปลข้อความ

โครงสร้างไฟล์:
- translation_tab.py (ไฟล์นี้) - Main class รวม mixins
- translation_tab_widgets.py - Widget creation methods  
- translation_tab_operations.py - Translation operations
- translation_tab_dialogs.py - Dialog windows
"""

import tkinter as tk
from tkinter import ttk

from gui.base import BaseTabComponent
from config.constants import (
    DEFAULT_SOURCE_LANG,
    DEFAULT_TARGET_LANG,
    DEFAULT_LINES_PER_PAGE,
    EMOJIS
)
from data.translation_data import TranslationData
from core.translation_engine import TranslationEngine

# Import Mixins
from gui.tabs.translation_tab_widgets import TranslationTabWidgetsMixin
from gui.tabs.translation_tab_operations import TranslationTabOperationsMixin
from gui.tabs.translation_tab_dialogs import TranslationTabDialogsMixin


class TranslationTab(
    TranslationTabWidgetsMixin,
    TranslationTabOperationsMixin, 
    TranslationTabDialogsMixin,
    BaseTabComponent
):
    """
    Tab สำหรับการแปลข้อความในไฟล์
    รวม mixins สำหรับ:
    - Widgets (UI creation)
    - Operations (translation, file, pagination)
    - Dialogs (popup windows)
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
            # Engine selection
            'selected_engine': tk.StringVar(value='auto'),
            # Gemini settings
            'gemini_api_key': tk.StringVar(),
            'gemini_model': tk.StringVar(value="gemini-2.5-flash"),
            'use_gemini': tk.BooleanVar(value=False),
            'gemini_prompt_type': tk.StringVar(value='general'),
            'custom_prompt': tk.StringVar(),
            # Text Protection settings
            'enable_text_protection': tk.BooleanVar(value=True),
            'protection_patterns': {},
            # Separator Translation settings
            'translate_only_after_separator': tk.BooleanVar(value=False),
            'custom_separator': tk.StringVar(value=':')
        }
        
        # ข้อมูลการแปล
        self.translation_data = TranslationData()
        self.translation_engine = None
        
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
        
        def configure_scroll_region(event=None):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
        def configure_canvas_width(event=None):
            canvas_width = event.width if event else main_canvas.winfo_width()
            main_canvas.itemconfig(scroll_window, width=canvas_width)
        
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        main_canvas.bind("<Configure>", configure_canvas_width)
        
        scroll_window = main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        main_canvas.bind("<MouseWheel>", _on_mousewheel)
        
        self.content_frame = scrollable_frame
        
        # Title
        title_label = ttk.Label(
            self.content_frame, 
            text=f"{EMOJIS['translate']} แปลข้อความ (Grid View)", 
            style='Title.TLabel'
        )
        title_label.pack(pady=(5, 10))
        
        # Create sections using mixin methods
        self._create_file_section()
        self._create_language_section()
        self._create_gemini_section()
        self._create_pagination_section()
        self._create_grid_section()
        self._create_edit_section()
        
        # Status bar
        self.create_status_bar(self.content_frame)


__all__ = ['TranslationTab', 'TranslationEngine', 'TranslationData']


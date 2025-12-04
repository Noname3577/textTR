#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translation Tab Widgets - GUI widget creation methods
Methods สำหรับสร้าง widgets ของ TranslationTab
"""

import tkinter as tk
from tkinter import ttk, scrolledtext


class TranslationTabWidgetsMixin:
    """
    Mixin class สำหรับ methods ที่สร้าง widgets
    """
    
    def _create_file_section(self) -> None:
        """สร้างส่วนเลือกไฟล์"""
        from config.constants import EMOJIS
        
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
        from config.constants import EMOJIS, SUPPORTED_LANGUAGES
        
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
        target_combo['values'] = [lang[1] for lang in SUPPORTED_LANGUAGES[1:]]
        target_combo.pack(side='left', padx=(2, 10))
        
        # Swap button
        ttk.Button(
            lang_controls, 
            text=f"{EMOJIS['refresh']}", 
            command=self.swap_languages
        ).pack(side='right')
        
        # Engine selection row
        engine_frame = ttk.Frame(lang_frame)
        engine_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Label(engine_frame, text="🔧 ตัวแปล:").pack(side='left')
        engine_combo = ttk.Combobox(
            engine_frame, 
            textvariable=self.variables['selected_engine'], 
            width=20, 
            state='readonly'
        )
        engine_combo['values'] = [
            'auto (อัตโนมัติ)',
            'Gemini AI',
            'Googletrans',
            'Deep Translator',
            'Google API'
        ]
        engine_combo.current(0)
        engine_combo.pack(side='left', padx=(5, 10))
        
        # Engine status label
        self.widgets['engine_status'] = ttk.Label(engine_frame, text="", foreground='gray')
        self.widgets['engine_status'].pack(side='left')
    
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
            show='*',
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
            width=18,
            state='readonly',
            values=['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-2.5-flash-lite', 
                   'gemini-2.0-flash', 'gemini-1.5-pro', 'gemini-1.5-flash']
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
            
            row = 0
            col = 0
            max_cols = 3
            
            for pattern_name, description in available_patterns.items():
                pattern_var = tk.BooleanVar(value=pattern_name in ['curly_braces', 'square_brackets'])
                self.variables['protection_patterns'][pattern_name] = pattern_var
                
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
        
        separator_combo = ttk.Combobox(
            separator_select_frame,
            textvariable=self.variables['custom_separator'],
            width=8,
            values=[':' , '=', '|', '->', '=>', '~', '#', '@']
        )
        separator_combo.pack(side='left', padx=(5, 5))
        separator_combo.bind('<<ComboboxSelected>>', self.on_separator_changed)
        
        ttk.Label(separator_select_frame, text="หรือกำหนดเอง:").pack(side='left', padx=(10, 0))
        custom_entry = ttk.Entry(separator_select_frame, textvariable=self.variables['custom_separator'], width=10)
        custom_entry.pack(side='left', padx=(5, 0))
        
        # Example frame
        self.widgets['example_frame'] = ttk.Frame(separator_frame)
        self.widgets['example_frame'].pack(fill='x', pady=(3, 0))
        
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
        
        self.widgets['separator_test_result'] = ttk.Label(
            test_frame,
            text="ผลลัพธ์จะแสดงที่นี่",
            font=('Arial', 9),
            foreground='#0066cc',
            wraplength=400
        )
        self.widgets['separator_test_result'].pack(anchor='w')
        
        self.update_separator_example()
    
    def _create_pagination_section(self) -> None:
        """สร้างส่วนการแบ่งหน้า"""
        from config.constants import EMOJIS
        
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
        
        ttk.Button(nav_controls, text="⏪", width=3, command=self.goto_first_page).pack(side='left', padx=1)
        ttk.Button(nav_controls, text="◀", width=2, command=self.goto_prev_page).pack(side='left', padx=1)
        
        self.widgets['page_info'] = ttk.Label(nav_controls, text="0/0", width=8)
        self.widgets['page_info'].pack(side='left', padx=5)
        
        ttk.Button(nav_controls, text="▶", width=2, command=self.goto_next_page).pack(side='left', padx=1)
        ttk.Button(nav_controls, text="⏩", width=3, command=self.goto_last_page).pack(side='left', padx=1)
        
        self.widgets['page_jump_entry'] = ttk.Entry(nav_controls, width=4)
        self.widgets['page_jump_entry'].pack(side='left', padx=(10, 2))
        ttk.Button(nav_controls, text="ไป", width=3, command=self.jump_to_page).pack(side='left')
        
        self.widgets['page_jump_entry'].bind('<Return>', lambda e: self.jump_to_page())
    
    def _create_grid_section(self) -> None:
        """สร้างส่วนแสดงตาราง"""
        from config.constants import EMOJIS
        
        grid_frame = ttk.LabelFrame(self.content_frame, text=f"{EMOJIS['info']} ตาราง", padding=5)
        grid_frame.pack(fill='both', expand=True, padx=10, pady=(0, 5))
        
        # Help frame
        help_frame = ttk.Frame(grid_frame)
        help_frame.pack(fill='x', padx=5, pady=(0, 5))
        
        help_label = ttk.Label(
            help_frame, 
            text="💡 คลิกที่คอลัมน์ 'ข้าม' เพื่อปิด/เปิดการแปลบรรทัดนั้น | คลิกที่บรรทัดอื่นเพื่อเลือกและแก้ไข",
            font=('Arial', 9),
            foreground='gray'
        )
        help_label.pack()
        
        # Create container frame
        tree_container = ttk.Frame(grid_frame)
        tree_container.pack(fill='both', expand=True)
        
        # Create Treeview
        columns = ('line_no', 'skip', 'original', 'translated', 'engine', 'status')
        self.widgets['tree'] = ttk.Treeview(tree_container, columns=columns, show='headings', height=8)
        
        self.widgets['tree'].heading('line_no', text='#')
        self.widgets['tree'].heading('skip', text='ข้าม')
        self.widgets['tree'].heading('original', text='ต้นฉบับ')
        self.widgets['tree'].heading('translated', text='แปล')
        self.widgets['tree'].heading('engine', text='ตัวแปล')
        self.widgets['tree'].heading('status', text='สถานะ')
        
        self.widgets['tree'].column('line_no', width=40, minwidth=30)
        self.widgets['tree'].column('skip', width=50, minwidth=40)
        self.widgets['tree'].column('original', width=250, minwidth=150)
        self.widgets['tree'].column('translated', width=250, minwidth=150)
        self.widgets['tree'].column('engine', width=100, minwidth=80)
        self.widgets['tree'].column('status', width=70, minwidth=50)
        
        # Add scrollbars
        tree_scrollbar_y = ttk.Scrollbar(tree_container, orient='vertical', command=self.widgets['tree'].yview)
        tree_scrollbar_x = ttk.Scrollbar(tree_container, orient='horizontal', command=self.widgets['tree'].xview)
        self.widgets['tree'].configure(yscrollcommand=tree_scrollbar_y.set, xscrollcommand=tree_scrollbar_x.set)
        
        tree_scrollbar_y.pack(side='right', fill='y')
        tree_scrollbar_x.pack(side='bottom', fill='x')
        self.widgets['tree'].pack(side='left', fill='both', expand=True)
        
        # Bind events
        self.widgets['tree'].bind('<Button-1>', self.on_tree_click)
        self.widgets['tree'].bind('<Double-1>', self.on_tree_double_click)
        self.widgets['tree'].bind('<Motion>', self.on_tree_motion)
    
    def _create_edit_section(self) -> None:
        """สร้างส่วนแก้ไข"""
        from config.constants import EMOJIS
        
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
        from config.constants import EMOJIS
        
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
        ttk.Button(row3, text="🔍 ตรวจสอบและข้าม Code", command=self.detect_and_skip_code_lines).pack(side='left', padx=(0, 5))
        
        # Row 4: Save actions
        row4 = ttk.Frame(parent)
        row4.pack(fill='x', pady=(2, 0))
        
        ttk.Button(row4, text=f"{EMOJIS['save']} บันทึกทั้งไฟล์", command=self.save_all_translations).pack(side='left', padx=(0, 5))
        ttk.Button(row4, text=f"{EMOJIS['file']} บันทึกเป็นไฟล์ใหม่", command=self.save_as_new_file).pack(side='left')

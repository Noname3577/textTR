#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translation Tab Dialogs - Dialog windows and helper functions
หน้าต่าง dialogs และ helper functions ของ TranslationTab
"""

import re
import tkinter as tk
from tkinter import ttk, scrolledtext


class TranslationTabDialogsMixin:
    """
    Mixin class สำหรับ dialog windows และ helper methods
    """
    
    def show_custom_prompt_dialog(self) -> None:
        """แสดง dialog สำหรับแก้ไข custom prompt"""
        dialog = tk.Toplevel(self.parent.winfo_toplevel())
        dialog.title("Custom Prompt สำหรับ Gemini")
        dialog.geometry("600x400")
        dialog.transient(self.parent.winfo_toplevel())
        dialog.grab_set()
        
        dialog.geometry("+%d+%d" % (
            dialog.winfo_toplevel().winfo_x() + 50,
            dialog.winfo_toplevel().winfo_y() + 50
        ))
        
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill='both', expand=True)
        
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
        
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        text_area = scrolledtext.ScrolledText(text_frame, wrap='word', height=15)
        text_area.pack(fill='both', expand=True)
        
        current_prompt = self.variables['custom_prompt'].get()
        if current_prompt:
            text_area.insert('1.0', current_prompt)
        
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
        
        text_area.focus_set()
    
    def show_custom_pattern_dialog(self) -> None:
        """แสดง dialog สำหรับเพิ่ม custom protection pattern"""
        dialog = tk.Toplevel(self.parent.winfo_toplevel())
        dialog.title("เพิ่ม Protection Pattern")
        dialog.geometry("500x300")
        dialog.transient(self.parent.winfo_toplevel())
        dialog.grab_set()
        
        dialog.geometry("+%d+%d" % (
            dialog.winfo_toplevel().winfo_x() + 50,
            dialog.winfo_toplevel().winfo_y() + 50
        ))
        
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(
            main_frame,
            text="เพิ่ม Custom Protection Pattern:",
            font=('TkDefaultFont', 10, 'bold')
        ).pack(anchor='w', pady=(0, 5))
        
        ttk.Label(main_frame, text="ชื่อ Pattern:").pack(anchor='w')
        name_entry = ttk.Entry(main_frame, width=40)
        name_entry.pack(fill='x', pady=(0, 5))
        
        ttk.Label(main_frame, text="Regex Pattern:").pack(anchor='w')
        pattern_entry = ttk.Entry(main_frame, width=40)
        pattern_entry.pack(fill='x', pady=(0, 5))
        
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
                matches = re.findall(pattern, test_text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    self.show_success(f"พบการจับคู่: {matches}")
                else:
                    self.show_success("ไม่พบการจับคู่")
            except re.error as e:
                self.show_error(f"Regex ไม่ถูกต้อง: {e}")
        
        ttk.Button(test_frame, text="ทดสอบ", command=test_pattern).pack(side='right')
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        def save_pattern():
            name = name_entry.get().strip()
            pattern = pattern_entry.get().strip()
            
            if not name or not pattern:
                self.show_error("กรุณาใส่ชื่อและ pattern")
                return
            
            try:
                re.compile(pattern)
            except re.error as e:
                self.show_error(f"Regex ไม่ถูกต้อง: {e}")
                return
            
            if self.translation_engine and self.translation_engine.is_gemini_available():
                self.translation_engine.gemini_translator.add_custom_protection_pattern(name, pattern)
                
                pattern_var = tk.BooleanVar(value=True)
                self.variables['protection_patterns'][name] = pattern_var
                
                dialog.destroy()
                self.show_success(f"เพิ่ม pattern '{name}' แล้ว")
            else:
                self.show_error("Gemini translator ไม่พร้อมใช้งาน")
        
        ttk.Button(button_frame, text="เพิ่ม", command=save_pattern).pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="ยกเลิก", command=dialog.destroy).pack(side='right')
        
        name_entry.focus_set()
    
    def test_text_protection(self) -> None:
        """ทดสอบการป้องกันข้อความ"""
        dialog = tk.Toplevel(self.parent.winfo_toplevel())
        dialog.title("ทดสอบการป้องกันข้อความ")
        dialog.geometry("600x400")
        dialog.transient(self.parent.winfo_toplevel())
        dialog.grab_set()
        
        dialog.geometry("+%d+%d" % (
            dialog.winfo_toplevel().winfo_x() + 50,
            dialog.winfo_toplevel().winfo_y() + 50
        ))
        
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(
            main_frame,
            text="ทดสอบการป้องกันข้อความ:",
            font=('TkDefaultFont', 10, 'bold')
        ).pack(anchor='w', pady=(0, 5))
        
        ttk.Label(main_frame, text="ข้อความทดสอบ:").pack(anchor='w')
        input_text = scrolledtext.ScrolledText(main_frame, height=4, wrap='word')
        input_text.pack(fill='x', pady=(0, 5))
        
        default_text = "Hello {player_name}! You have [100 HP] and $gold coins. Visit <shop> or use %skill%."
        input_text.insert('1.0', default_text)
        
        ttk.Label(main_frame, text="ผลลัพธ์:").pack(anchor='w', pady=(10, 0))
        
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        ttk.Label(results_frame, text="ข้อความที่ป้องกัน:").pack(anchor='w')
        protected_text = scrolledtext.ScrolledText(results_frame, height=3, wrap='word', bg='#e8f5e8')
        protected_text.pack(fill='x', pady=(0, 5))
        
        ttk.Label(results_frame, text="รายการที่ถูกป้องกัน:").pack(anchor='w')
        protected_items = scrolledtext.ScrolledText(results_frame, height=4, wrap='word', bg='#f0f0f0')
        protected_items.pack(fill='both', expand=True)
        
        def run_test():
            test_text = input_text.get('1.0', tk.END).strip()
            
            if not test_text:
                self.show_error("กรุณาใส่ข้อความทดสอบ")
                return
            
            try:
                from ai_translator import TextProtector
                
                enabled_patterns = []
                for pattern_name, pattern_var in self.variables['protection_patterns'].items():
                    if pattern_var.get():
                        enabled_patterns.append(pattern_name)
                
                text_protector = TextProtector()
                if enabled_patterns:
                    text_protector.set_enabled_patterns(enabled_patterns)
                
                protected, placeholders = text_protector.protect_text(test_text)
                
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
                
            except ImportError:
                self.show_error("ไม่พบโมดูล ai_translator กรุณาตรวจสอบการติดตั้ง")
            except Exception as e:
                self.show_error(f"การทดสอบล้มเหลว: {e}")
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="ทดสอบ", command=run_test).pack(side='left')
        ttk.Button(button_frame, text="ปิด", command=dialog.destroy).pack(side='right')
        
        run_test()
    
    def show_separator_translation_help(self) -> None:
        """แสดงหน้าต่างช่วยเหลือสำหรับฟีเจอร์การแปลเฉพาะหลังเครื่องหมายแบ่ง"""
        help_window = tk.Toplevel(self.parent.winfo_toplevel())
        help_window.title("วิธีใช้ฟีเจอร์การแปลเฉพาะส่วนที่ต้องการ")
        help_window.geometry("550x500")
        help_window.transient(self.parent.winfo_toplevel())
        help_window.grab_set()
        
        help_window.geometry("+%d+%d" % (
            help_window.winfo_toplevel().winfo_x() + 50,
            help_window.winfo_toplevel().winfo_y() + 50
        ))
        
        main_frame = ttk.Frame(help_window, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        title_label = ttk.Label(
            main_frame,
            text="📍 ฟีเจอร์การแปลเฉพาะส่วนที่ต้องการ",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        help_text = """ฟีเจอร์นี้ช่วยให้คุณแปลเฉพาะส่วนของข้อความหลังเครื่องหมายแบ่ง
เหมาะสำหรับไฟล์เกม, config, หรือไฟล์ที่มีรูปแบบ Key: Value

ตัวอย่างการใช้งาน:
• Cook_1: Fried Rice → Cook_1: ข้าวผัด
• ItemName=Magic Sword → ItemName=ดาบเวทมนตร์
• NPC_01|Welcome! → NPC_01|ยินดีต้อนรับ!

เครื่องหมายแบ่งที่รองรับ:
: (colon), = (equals), | (pipe), -> (arrow), => (fat arrow), ~ (tilde), # (hash), @ (at)

วิธีใช้:
1. เปิดใช้งานตัวเลือก "แปลเฉพาะข้อความหลังเครื่องหมายแบ่งเท่านั้น"
2. เลือกหรือกำหนดเครื่องหมายแบ่งที่ต้องการ
3. ทดสอบด้วยช่องทดสอบด้านล่าง
4. เริ่มแปลไฟล์ตามปกติ"""
        
        text_widget = tk.Text(main_frame, wrap='word', height=20, bg='#f9f9f9')
        text_widget.pack(fill='both', expand=True, pady=(0, 10))
        text_widget.insert('1.0', help_text)
        text_widget.config(state='disabled')
        
        ttk.Button(
            main_frame,
            text="ปิด",
            command=help_window.destroy
        ).pack(pady=5)
    
    def show_skip_help(self) -> None:
        """แสดงหน้าต่างช่วยเหลือสำหรับฟีเจอร์การข้าม"""
        help_window = tk.Toplevel(self.parent.winfo_toplevel())
        help_window.title("วิธีใช้ฟีเจอร์การข้ามการแปล")
        help_window.geometry("500x600")
        help_window.transient(self.parent.winfo_toplevel())
        help_window.grab_set()
        
        help_window.geometry("+%d+%d" % (
            help_window.winfo_toplevel().winfo_x() + 50,
            help_window.winfo_toplevel().winfo_y() + 50
        ))
        
        main_frame = ttk.Frame(help_window, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        title_label = ttk.Label(
            main_frame,
            text="🚫 ฟีเจอร์การข้ามการแปล",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        help_text = """ฟีเจอร์การข้ามช่วยให้คุณกำหนดบรรทัดที่ไม่ต้องการแปล
เหมาะสำหรับ:
• บรรทัดที่เป็น code หรือ markup
• ข้อความที่ต้องการเก็บไว้เป็นภาษาเดิม
• ตัวแปร, ชื่อ, หรือคำเฉพาะทาง

วิธีใช้งาน:
1. คลิกที่คอลัมน์ "ข้าม" ในตารางเพื่อเปิด/ปิดการข้ามบรรทัดนั้น
2. ใช้ checkbox ในส่วนแก้ไขสำหรับบรรทัดที่เลือก
3. ใช้ปุ่ม "ข้ามหน้านี้ทั้งหมด" เพื่อข้ามทุกบรรทัดในหน้าปัจจุบัน
4. ใช้ปุ่ม "ตรวจสอบและข้าม Code" เพื่อตรวจจับ code อัตโนมัติ

สัญลักษณ์:
✓ = บรรทัดที่ถูกข้าม (ไม่แปล)
(ว่าง) = บรรทัดที่จะแปล

หมายเหตุ:
• บรรทัดที่ข้ามจะไม่ถูกแปลเมื่อใช้ "แปลหน้านี้ทั้งหมด" หรือ "แปลไฟล์ทั้งหมด"
• คุณยังสามารถแปลบรรทัดที่ข้ามได้ด้วยตนเองโดยเลือกบรรทัดและกด "แปลบรรทัดนี้"
• การข้ามจะถูกบันทึกเมื่อบันทึกไฟล์"""
        
        text_widget = tk.Text(main_frame, wrap='word', height=25, bg='#f9f9f9')
        text_widget.pack(fill='both', expand=True, pady=(0, 10))
        text_widget.insert('1.0', help_text)
        text_widget.config(state='disabled')
        
        ttk.Button(
            main_frame,
            text="ปิด",
            command=help_window.destroy
        ).pack(pady=5)
    
    def is_code_line(self, text: str) -> tuple:
        """
        ตรวจสอบว่าข้อความมีลักษณะเป็น code หรือไม่
        
        Returns:
            tuple: (is_code: bool, reason: str)
        """
        if not text or not text.strip():
            return False, ""
        
        text = text.strip()
        
        code_patterns = [
            (r'^\s*(def|function|func|fn|public|private|protected|static|async|void)\s+\w+\s*\(', 'function definition'),
            (r'^\s*(class|struct|interface|enum)\s+\w+', 'class/struct definition'),
            (r'^\s*(var|let|const|int|float|double|string|bool|char)\s+\w+\s*[=;]', 'variable declaration'),
            (r'^\s*\w+\s*=\s*[\[\{]', 'array/object assignment'),
            (r'^\s*(import|from|include|require|using|#include)\s+', 'import statement'),
            (r'^\s*(if|else|elif|switch|case|for|while|do|try|catch|finally|with)\s*[\(\{:]', 'control structure'),
            (r'^\s*(return|break|continue|pass|yield|throw)\s*[;\s]', 'control keyword'),
            (r'^<[a-zA-Z][^>]*>[^<]*</[a-zA-Z]+>$', 'HTML/XML tag'),
            (r'^<[a-zA-Z][^>]*/?\s*>$', 'self-closing tag'),
            (r'^</[a-zA-Z]+>$', 'closing tag'),
            (r'^\s*[\.\#\w\-]+\s*\{', 'CSS selector'),
            (r'^\s*\w+(-\w+)*\s*:\s*[^;]+;\s*$', 'CSS property'),
            (r'^\s*[\"\'][^\"\']+[\"\']\s*:\s*[\[\{\"\'\d]', 'JSON/Dict entry'),
            (r'^\s*\{[\s\S]*\}\s*$', 'JSON object'),
            (r'^\s*\[[\s\S]*\]\s*$', 'JSON array'),
            (r'^\s*/.+/[gimsu]*\s*$', 'regex pattern'),
            (r'^\s*r[\"\'].+[\"\']\s*$', 'Python raw string/regex'),
            (r'^\s*[$#>]\s+\w+', 'shell command'),
            (r'^\s*(npm|pip|yarn|git|docker|kubectl)\s+\w+', 'CLI command'),
            (r'^\s*(//|#|/\*|\*|<!--)', 'code comment'),
            (r'^\s*[\{\}\[\]\(\)]+\s*$', 'brackets only'),
            (r'^\s*\w+\.\w+\([^)]*\)\s*;?\s*$', 'method call'),
            (r'^\s*\w+\(\s*\)\s*;?\s*$', 'function call'),
            (r'^\s*\w+\s*[+\-*/&|^%]=\s*\w+', 'compound assignment'),
            (r'^\s*\w+\s*[<>=!]+\s*\w+', 'comparison'),
            (r'^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|FROM|WHERE|JOIN)\s+', 'SQL statement'),
            (r'^\s*[\d\.\-]+\s*$', 'number only'),
            (r'^\s*0x[a-fA-F0-9]+\s*$', 'hex number'),
            (r'^[/\\]?[\w\-]+([/\\][\w\-\.]+)+[/\\]?$', 'file path'),
            (r'^[a-zA-Z]:[\\\/]', 'Windows path'),
            (r'^https?://\S+$', 'URL'),
            (r'^\S+@\S+\.\S+$', 'email address'),
            (r'^\s*@\w+(\(.*\))?\s*$', 'decorator/annotation'),
            (r'^\s*\w+\s*=>\s*', 'arrow function'),
            (r'^\s*lambda\s+\w+\s*:', 'lambda function'),
            (r'.*\\[nrtbfv\\\"\'0].*\\[nrtbfv\\\"\'0]', 'escape sequences'),
        ]
        
        for pattern, reason in code_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True, reason
        
        special_chars = set('{}[]()<>+=*/%&|^!~;:@#$\\')
        special_count = sum(1 for c in text if c in special_chars)
        if len(text) > 5 and special_count / len(text) > 0.3:
            return True, "high special char ratio"
        
        camel_snake_pattern = r'^[a-z]+([A-Z][a-z]+)+$|^[a-z]+(_[a-z]+)+$|^[A-Z]+(_[A-Z]+)+$'
        if re.match(camel_snake_pattern, text):
            return True, "code naming convention"
        
        return False, ""
    
    def detect_and_skip_code_lines(self) -> None:
        """ตรวจสอบและข้ามบรรทัดที่เป็น code"""
        if not self.translation_data.lines:
            self.show_error("ไม่มีข้อมูลให้ตรวจสอบ")
            return
        
        dialog = tk.Toplevel(self.parent.winfo_toplevel())
        dialog.title("🔍 ตรวจสอบและข้าม Code")
        dialog.geometry("700x600")
        dialog.transient(self.parent.winfo_toplevel())
        dialog.grab_set()
        
        dialog.geometry("+%d+%d" % (
            dialog.winfo_toplevel().winfo_x() + 50,
            dialog.winfo_toplevel().winfo_y() + 50
        ))
        
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        title_label = ttk.Label(
            main_frame,
            text="🔍 ตรวจสอบบรรทัดที่เป็น Code",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        desc_label = ttk.Label(
            main_frame,
            text="ระบบจะตรวจสอบบรรทัดที่มีลักษณะเป็น code และแนะนำให้ข้าม",
            font=('Arial', 10),
            foreground='gray'
        )
        desc_label.pack(pady=(0, 10))
        
        # Scope selection
        scope_frame = ttk.LabelFrame(main_frame, text="ขอบเขตการตรวจสอบ", padding=5)
        scope_frame.pack(fill='x', pady=(0, 10))
        
        scope_var = tk.StringVar(value='all')
        ttk.Radiobutton(scope_frame, text="ทั้งไฟล์", variable=scope_var, value='all').pack(side='left', padx=(0, 10))
        ttk.Radiobutton(scope_frame, text="เฉพาะหน้าปัจจุบัน", variable=scope_var, value='page').pack(side='left', padx=(0, 10))
        ttk.Radiobutton(scope_frame, text="เฉพาะบรรทัดที่ยังไม่ข้าม", variable=scope_var, value='unskipped').pack(side='left')
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="ผลการตรวจสอบ", padding=5)
        results_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('line_no', 'reason', 'text')
        results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        results_tree.heading('line_no', text='#')
        results_tree.heading('reason', text='ประเภท')
        results_tree.heading('text', text='ข้อความ')
        
        results_tree.column('line_no', width=50, minwidth=40)
        results_tree.column('reason', width=120, minwidth=100)
        results_tree.column('text', width=450, minwidth=300)
        
        tree_scroll_y = ttk.Scrollbar(results_frame, orient='vertical', command=results_tree.yview)
        tree_scroll_x = ttk.Scrollbar(results_frame, orient='horizontal', command=results_tree.xview)
        results_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        tree_scroll_y.pack(side='right', fill='y')
        tree_scroll_x.pack(side='bottom', fill='x')
        results_tree.pack(side='left', fill='both', expand=True)
        
        status_label = ttk.Label(main_frame, text="คลิก 'ตรวจสอบ' เพื่อเริ่มการตรวจสอบ", foreground='gray')
        status_label.pack(pady=(0, 5))
        
        detected_lines = []
        
        def scan_lines():
            nonlocal detected_lines
            detected_lines = []
            
            for item in results_tree.get_children():
                results_tree.delete(item)
            
            scope = scope_var.get()
            lines_to_scan = []
            
            if scope == 'all':
                lines_to_scan = list(range(len(self.translation_data.lines)))
            elif scope == 'page':
                current_page = self.variables['current_page'].get()
                lines_per_page = self.variables['lines_per_page'].get()
                start_index = (current_page - 1) * lines_per_page
                end_index = min(start_index + lines_per_page, len(self.translation_data.lines))
                lines_to_scan = list(range(start_index, end_index))
            else:
                lines_to_scan = [i for i, line in enumerate(self.translation_data.lines) 
                               if not line['skip_translation']]
            
            for line_index in lines_to_scan:
                line_data = self.translation_data.lines[line_index]
                is_code, reason = self.is_code_line(line_data['original'])
                
                if is_code:
                    detected_lines.append((line_index, reason))
                    text_preview = line_data['original'][:60] + "..." if len(line_data['original']) > 60 else line_data['original']
                    results_tree.insert('', 'end', values=(line_data['line_number'], reason, text_preview))
            
            status_label.config(
                text=f"พบบรรทัดที่เป็น code: {len(detected_lines)} บรรทัด จาก {len(lines_to_scan)} บรรทัดที่ตรวจสอบ",
                foreground='#0066cc'
            )
        
        def apply_skip():
            if not detected_lines:
                self.show_error("ไม่มีบรรทัดให้ข้าม กรุณาตรวจสอบก่อน")
                return
            
            skipped_count = 0
            for line_index, reason in detected_lines:
                if not self.translation_data.lines[line_index]['skip_translation']:
                    self.translation_data.toggle_skip_translation(line_index)
                    skipped_count += 1
            
            dialog.destroy()
            self.refresh_grid()
            self.show_success(f"ข้ามบรรทัดที่เป็น code แล้ว {skipped_count} บรรทัด")
        
        def apply_selected():
            selected_items = results_tree.selection()
            if not selected_items:
                self.show_error("กรุณาเลือกบรรทัดที่ต้องการข้าม")
                return
            
            skipped_count = 0
            for item in selected_items:
                values = results_tree.item(item)['values']
                line_number = int(values[0])
                line_index = line_number - 1
                
                if not self.translation_data.lines[line_index]['skip_translation']:
                    self.translation_data.toggle_skip_translation(line_index)
                    skipped_count += 1
            
            dialog.destroy()
            self.refresh_grid()
            self.show_success(f"ข้ามบรรทัดที่เลือก {skipped_count} บรรทัด")
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Button(button_frame, text="🔍 ตรวจสอบ", command=scan_lines).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="✓ ข้ามทั้งหมดที่พบ", command=apply_skip).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="✓ ข้ามเฉพาะที่เลือก", command=apply_selected).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="ปิด", command=dialog.destroy).pack(side='right')
        
        results_tree.configure(selectmode='extended')
        
        scan_lines()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translation Tab Operations - Translation and file operations
Methods สำหรับ operations ของ TranslationTab
"""

import os
import re
import time
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import List


class TranslationTabOperationsMixin:
    """
    Mixin class สำหรับ translation และ file operations
    """
    
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
            
            file_type = self.translation_data.get_file_type_info()
            line_count = self.translation_data.get_line_count()
            self.update_status(f"โหลดไฟล์สำเร็จ: {line_count:,} รายการ [{file_type}]")
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
    
    # === Gemini Operations ===
    
    def toggle_gemini_settings(self) -> None:
        """เปิด/ปิดการใช้งาน Gemini"""
        use_gemini = self.variables['use_gemini'].get()
        state = 'normal' if use_gemini else 'disabled'
        
        if 'gemini_api_entry' in self.widgets:
            self.widgets['gemini_api_entry'].config(state=state)
        if 'prompt_combo' in self.widgets:
            self.widgets['prompt_combo'].config(state=state)
        
        self._initialize_translation_engine()
    
    def save_gemini_settings(self) -> None:
        """บันทึกการตั้งค่า Gemini"""
        api_key = self.variables['gemini_api_key'].get().strip()
        
        if not api_key:
            self.show_error("กรุณาใส่ Gemini API Key")
            return
        
        try:
            from ai_translator import validate_api_key
            if not validate_api_key(api_key):
                self.show_error("รูปแบบ API Key ไม่ถูกต้อง")
                return
        except ImportError:
            pass
        
        self._initialize_translation_engine()
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
    
    def _update_prompt_types(self) -> None:
        """อัปเดตรายการประเภท prompt"""
        try:
            if self.translation_engine and self.translation_engine.is_gemini_available():
                prompts = self.translation_engine.get_gemini_prompts()
                self.widgets['prompt_combo']['values'] = list(prompts.keys())
            else:
                default_prompts = ['general', 'novel', 'game', 'dialogue', 'technical', 'formal']
                self.widgets['prompt_combo']['values'] = default_prompts
        except Exception:
            default_prompts = ['general', 'novel', 'game', 'dialogue', 'technical', 'formal']
            self.widgets['prompt_combo']['values'] = default_prompts
    
    def _initialize_translation_engine(self) -> None:
        """เตรียม Translation Engine"""
        from core.translation_engine import TranslationEngine
        
        use_gemini = self.variables['use_gemini'].get()
        
        if use_gemini:
            api_key = self.variables['gemini_api_key'].get().strip()
            model = self.variables['gemini_model'].get()
            
            if api_key:
                enabled_patterns = []
                for pattern_name, pattern_var in self.variables['protection_patterns'].items():
                    if pattern_var.get():
                        enabled_patterns.append(pattern_name)
                
                self.translation_engine = TranslationEngine(api_key, model, enabled_patterns)
                
                if self.translation_engine.is_gemini_available():
                    self.widgets['gemini_status'].config(text="พร้อมใช้งาน", foreground='green')
                else:
                    self.widgets['gemini_status'].config(text="ไม่พร้อมใช้งาน", foreground='red')
            else:
                self.translation_engine = TranslationEngine()
                self.widgets['gemini_status'].config(text="ไม่ได้ใส่ API Key", foreground='orange')
        else:
            self.translation_engine = TranslationEngine()
            if 'gemini_status' in self.widgets:
                self.widgets['gemini_status'].config(text="ปิดการใช้งาน", foreground='gray')
        
        if 'prompt_combo' in self.widgets:
            self._update_prompt_types()
    
    # === Text Protection Operations ===
    
    def toggle_text_protection(self) -> None:
        """เปิด/ปิดการใช้งาน Text Protection"""
        self.update_protection_settings()
    
    def update_protection_settings(self) -> None:
        """อัปเดตการตั้งค่า Text Protection"""
        if self.translation_engine and self.translation_engine.is_gemini_available():
            enabled_patterns = []
            for pattern_name, pattern_var in self.variables['protection_patterns'].items():
                if pattern_var.get():
                    enabled_patterns.append(pattern_name)
            
            self.translation_engine.gemini_translator.set_protection_patterns(enabled_patterns)
    
    # === Separator Operations ===
    
    def update_separator_translation_settings(self) -> None:
        """อัปเดตการตั้งค่าการแปลเฉพาะหลังเครื่องหมายแบ่ง"""
        pass
    
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
            if any(current_text.startswith(f"Player_01{s}") or current_text.startswith(f"PlayerName{s}") or 
                   current_text.startswith(f"ItemID{s}") for s in [':', '=', '|', '->', '=>', '~', '#', '@']):
                self.widgets['separator_test_entry'].delete(0, tk.END)
                self.widgets['separator_test_entry'].insert(0, test_text)
    
    def test_separator_translation(self) -> None:
        """ทดสอบฟีเจอร์การแปลเฉพาะหลังเครื่องหมายแบ่ง"""
        test_text = self.widgets['separator_test_entry'].get().strip()
        separator = self.variables['custom_separator'].get()
        
        if not test_text:
            self.widgets['separator_test_result'].config(text="กรุณาใส่ข้อความทดสอบ", foreground='red')
            return
        
        if not separator:
            self.widgets['separator_test_result'].config(text="กรุณาเลือกหรือกำหนดเครื่องหมายแบ่ง", foreground='red')
            return
        
        if separator not in test_text:
            self.widgets['separator_test_result'].config(
                text=f"ข้อความต้องมีเครื่องหมาย '{separator}' เพื่อทดสอบฟีเจอร์นี้", 
                foreground='red'
            )
            return
        
        try:
            separator_index = test_text.find(separator)
            prefix = test_text[:separator_index + len(separator)]
            suffix = test_text[separator_index + len(separator):].strip()
            
            if not suffix:
                self.widgets['separator_test_result'].config(
                    text=f"ไม่มีข้อความหลังเครื่องหมาย '{separator}'", 
                    foreground='orange'
                )
                return
            
            result_text = f"ส่วนที่ไม่แปล: '{prefix}'\nส่วนที่จะแปล: '{suffix}'"
            
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
            
            self.widgets['separator_test_result'].config(text=result_text, foreground='#0066cc')
            
        except Exception as e:
            self.widgets['separator_test_result'].config(text=f"เกิดข้อผิดพลาด: {str(e)}", foreground='red')
    
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
        from utils import calculate_pagination, get_page_items
        
        if not self.translation_data.lines:
            return
        
        lines_per_page = self.variables['lines_per_page'].get()
        total_pages, _ = calculate_pagination(len(self.translation_data.lines), lines_per_page)
        self.variables['total_pages'].set(total_pages)
        
        current_page = self.variables['current_page'].get()
        if current_page > total_pages and total_pages > 0:
            current_page = total_pages
            self.variables['current_page'].set(current_page)
        
        self.widgets['page_info'].config(text=f"{current_page}/{total_pages}")
        
        # Clear tree
        for item in self.widgets['tree'].get_children():
            self.widgets['tree'].delete(item)
        
        page_lines = get_page_items(self.translation_data.lines, current_page, lines_per_page)
        
        for line_data in page_lines:
            if line_data['skip_translation']:
                status_icon = "🚫"
                skip_icon = "✓"
            elif line_data['is_translated']:
                status_icon = "✅"
                skip_icon = ""
            else:
                status_icon = "⏳"
                skip_icon = ""
            
            original_preview = line_data['original'][:40] + "..." if len(line_data['original']) > 40 else line_data['original']
            translated_preview = line_data['translated'][:40] + "..." if len(line_data['translated']) > 40 else line_data['translated']
            
            used_engine = line_data.get('used_engine', '')
            if used_engine:
                engine_short = used_engine.replace('Google ', '').replace(' AI', '').replace('Translator', 'Trans')
                if len(engine_short) > 12:
                    engine_short = engine_short[:10] + '..'
            else:
                engine_short = '-'
            
            self.widgets['tree'].insert('', 'end', values=(
                line_data['line_number'],
                skip_icon,
                original_preview,
                translated_preview,
                engine_short,
                status_icon
            ))
    
    # === Tree Events ===
    
    def on_tree_click(self, event) -> None:
        """จัดการเมื่อคลิกที่ตาราง"""
        try:
            item_id = self.widgets['tree'].identify_row(event.y)
            if not item_id:
                return
            
            self.widgets['tree'].selection_set(item_id)
            item = self.widgets['tree'].item(item_id)
            
            if not item['values']:
                return
            
            line_number = int(item['values'][0])
            line_index = line_number - 1
            
            if not (0 <= line_index < len(self.translation_data.lines)):
                return
            
            skip_column_detected = self._is_skip_column_click(event.x)
            
            if skip_column_detected:
                self.toggle_skip_line(line_index)
            else:
                self.variables['selected_line'].set(line_index)
                self.update_edit_area()
                        
        except Exception as e:
            print(f"Tree click error: {e}")
            self._fallback_tree_click(event)
    
    def _is_skip_column_click(self, x_pos: int) -> bool:
        """ตรวจสอบว่าคลิกที่คอลัมน์ skip หรือไม่"""
        try:
            col1_width = 40
            col2_start = col1_width
            col2_end = col1_width + 50
            
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
            pass
    
    def on_tree_motion(self, event) -> None:
        """แสดงคำแนะนำเมื่อเลื่อนเมาส์"""
        try:
            column = self.widgets['tree'].identify_column(event.x)
            if column == '#2':
                self.widgets['tree'].config(cursor="hand2")
                self.update_status("💡 คลิกที่คอลัมน์ 'ข้าม' เพื่อเปิด/ปิดการแปลบรรทัดนั้น")
            else:
                self.widgets['tree'].config(cursor="")
        except Exception:
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
            
            skip_text = " (ข้าม)" if line_data['skip_translation'] else ""
            self.widgets['current_line_info'].config(text=f"บรรทัดที่ {line_data['line_number']}{skip_text}")
            
            self.widgets['original_text'].config(state='normal')
            self.widgets['original_text'].delete(1.0, tk.END)
            self.widgets['original_text'].insert(1.0, line_data['original'])
            self.widgets['original_text'].config(state='disabled')
            
            self.widgets['translated_text'].delete(1.0, tk.END)
            self.widgets['translated_text'].insert(1.0, line_data['translated'])
            
            if 'skip_checkbox' in self.widgets:
                self.widgets['skip_checkbox'].after(1, lambda: self._update_skip_checkbox(line_data['skip_translation']))
        else:
            self.widgets['current_line_info'].config(text="ยังไม่เลือก")
            self.widgets['original_text'].config(state='normal')
            self.widgets['original_text'].delete(1.0, tk.END)
            self.widgets['original_text'].config(state='disabled')
            self.widgets['translated_text'].delete(1.0, tk.END)
            
            if 'skip_checkbox' in self.widgets:
                self.widgets['skip_checkbox'].after(1, lambda: self._update_skip_checkbox(False))
    
    def _update_skip_checkbox(self, skip_value: bool) -> None:
        """อัปเดต skip checkbox อย่างปลอดภัย"""
        if 'skip_checkbox' in self.widgets:
            current_command = self.widgets['skip_checkbox']['command']
            self.widgets['skip_checkbox'].config(command='')
            
            if skip_value:
                self.widgets['skip_checkbox'].state(['selected'])
            else:
                self.widgets['skip_checkbox'].state(['!selected'])
            
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
            selected_engine = self.variables['selected_engine'].get()
            
            self.update_status(f"กำลังแปลบรรทัดที่ {selected_index + 1}...")
            
            prompt_type = self.variables['gemini_prompt_type'].get()
            custom_prompt = self.variables['custom_prompt'].get() if self.variables['custom_prompt'].get().strip() else None
            protect_text = self.variables['enable_text_protection'].get()
            translate_only_after_separator = self.variables['translate_only_after_separator'].get()
            custom_separator = self.variables['custom_separator'].get()
            
            translated_text = None
            current_engine = ''
            
            if selected_engine == 'Gemini AI' or (selected_engine.startswith('auto') and self.translation_engine.is_gemini_available()):
                if self.translation_engine.is_gemini_available():
                    self.update_protection_settings()
                    translated_text = self.translation_engine.gemini_translator.translate_text(
                        original_text, source_lang, target_lang, prompt_type, custom_prompt, 
                        protect_text, translate_only_after_separator, custom_separator
                    )
                    current_engine = f'Gemini ({self.translation_engine.gemini_model})'
            
            if translated_text is None:
                if selected_engine == 'Googletrans':
                    translated_text = self.translation_engine._try_googletrans(original_text, source_lang, target_lang)
                    current_engine = 'Googletrans'
                elif selected_engine == 'Deep Translator':
                    translated_text = self.translation_engine._try_deep_translator(original_text, source_lang, target_lang)
                    current_engine = 'Deep Trans'
                elif selected_engine == 'Google API':
                    translated_text = self.translation_engine._try_google_api(original_text, source_lang, target_lang)
                    current_engine = 'Google API'
                else:
                    translated_text = self.translation_engine.translate(
                        original_text, source_lang, target_lang, prompt_type, custom_prompt,
                        translate_only_after_separator, custom_separator
                    )
                    if self.translation_engine.last_used_engine:
                        current_engine = self.translation_engine.last_used_engine
                        current_engine = current_engine.replace('Google ', '').replace(' AI', '').replace('Translator', 'Trans')
            
            self.translation_data.translate_line(selected_index, translated_text, current_engine)
            
            self.widgets['translated_text'].delete(1.0, tk.END)
            self.widgets['translated_text'].insert(1.0, translated_text)
            
            self.refresh_grid()
            
            engine_info = f" (ใช้ {current_engine})" if current_engine else ""
            self.update_status(f"แปลบรรทัดที่ {selected_index + 1} เสร็จสิ้น{engine_info}")
            
        except Exception as e:
            self.show_error(f"การแปลล้มเหลว: {str(e)}")
    
    def save_selected_line(self) -> None:
        """บันทึกการแปลของบรรทัดที่เลือก"""
        selected_index = self.variables['selected_line'].get()
        
        if selected_index == -1:
            self.show_error("กรุณาเลือกบรรทัดที่จะบันทึก")
            return
        
        translated_text = self.widgets['translated_text'].get(1.0, tk.END).strip()
        self.translation_data.translate_line(selected_index, translated_text)
        self.refresh_grid()
        self.show_success(f"บันทึกการแปลบรรทัดที่ {selected_index + 1} แล้ว")
    
    def reset_selected_line(self) -> None:
        """รีเซ็ตการแปลของบรรทัดที่เลือก"""
        selected_index = self.variables['selected_line'].get()
        
        if selected_index == -1:
            return
        
        self.translation_data.translate_line(selected_index, "")
        self.widgets['translated_text'].delete(1.0, tk.END)
        self.refresh_grid()
    
    def toggle_skip_line(self, line_index: int) -> None:
        """เปิด/ปิดการข้ามการแปลของบรรทัด"""
        if not (0 <= line_index < len(self.translation_data.lines)):
            return
        
        line_data = self.translation_data.lines[line_index]
        self.translation_data.toggle_skip_translation(line_index)
        
        if line_data['skip_translation']:
            self.show_success(f"เปิดการแปลบรรทัดที่ {line_index + 1}")
        else:
            self.show_success(f"ปิดการแปลบรรทัดที่ {line_index + 1} (จะข้ามเมื่อแปลทั้งไฟล์)")
        
        self.refresh_grid()
        
        if self.variables['selected_line'].get() == line_index:
            self.update_edit_area()
    
    def toggle_skip_selected_line(self) -> None:
        """เปิด/ปิดการข้ามของบรรทัดที่เลือก"""
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
        
        current_page = self.variables['current_page'].get()
        lines_per_page = self.variables['lines_per_page'].get()
        start_index = (current_page - 1) * lines_per_page
        end_index = min(start_index + lines_per_page, len(self.translation_data.lines))
        
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
        
        self.set_working(True)
        self.cancel_translation = False
        
        progress_dialog = self.create_progress_dialog(
            self.parent.winfo_toplevel(),
            "กำลังแปลไฟล์",
            f"เตรียมแปลทั้งหมด {len(line_indices)} บรรทัด..."
        )
        
        thread = threading.Thread(target=self._translate_batch_thread, args=(line_indices,))
        thread.daemon = True
        thread.start()
    
    def _translate_batch_thread(self, line_indices: List[int]) -> None:
        """แปลบรรทัดในเทรดแยก"""
        from config.constants import TRANSLATION_DELAY
        
        success_count = 0
        error_count = 0
        total_count = len(line_indices)
        used_engines = set()
        
        source_lang = self.variables['source_lang'].get()
        target_lang = self.variables['target_lang'].get()
        selected_engine = self.variables['selected_engine'].get()
        
        try:
            for i, line_index in enumerate(line_indices):
                if self.cancel_translation:
                    break
                
                try:
                    progress = (i / total_count) * 100
                    self.parent.after(0, self.update_progress_dialog, 
                                    f"แปลบรรทัดที่ {line_index + 1} ({i + 1}/{total_count})")
                    
                    prompt_type = self.variables['gemini_prompt_type'].get()
                    custom_prompt = self.variables['custom_prompt'].get() if self.variables['custom_prompt'].get().strip() else None
                    protect_text = self.variables['enable_text_protection'].get()
                    translate_only_after_separator = self.variables['translate_only_after_separator'].get()
                    custom_separator = self.variables['custom_separator'].get()
                    
                    line_data = self.translation_data.lines[line_index]
                    translated_text = None
                    current_engine = ''
                    
                    if selected_engine == 'Gemini AI' or (selected_engine.startswith('auto') and self.translation_engine.is_gemini_available()):
                        if self.translation_engine.is_gemini_available():
                            self.update_protection_settings()
                            translated_text = self.translation_engine.gemini_translator.translate_text(
                                line_data['original'], source_lang, target_lang, prompt_type, custom_prompt, 
                                protect_text, translate_only_after_separator, custom_separator
                            )
                            current_engine = f'Gemini ({self.translation_engine.gemini_model})'
                    
                    if translated_text is None:
                        if selected_engine == 'Googletrans':
                            translated_text = self.translation_engine._try_googletrans(line_data['original'], source_lang, target_lang)
                            current_engine = 'Googletrans'
                        elif selected_engine == 'Deep Translator':
                            translated_text = self.translation_engine._try_deep_translator(line_data['original'], source_lang, target_lang)
                            current_engine = 'Deep Trans'
                        elif selected_engine == 'Google API':
                            translated_text = self.translation_engine._try_google_api(line_data['original'], source_lang, target_lang)
                            current_engine = 'Google API'
                        else:
                            translated_text = self.translation_engine.translate(
                                line_data['original'], source_lang, target_lang, prompt_type, custom_prompt,
                                translate_only_after_separator, custom_separator
                            )
                            if self.translation_engine.last_used_engine:
                                current_engine = self.translation_engine.last_used_engine
                                current_engine = current_engine.replace('Google ', '').replace(' AI', '').replace('Translator', 'Trans')
                    
                    if translated_text:
                        used_engines.add(current_engine)
                    
                    self.translation_data.translate_line(line_index, translated_text, current_engine)
                    success_count += 1
                    
                    time.sleep(TRANSLATION_DELAY / 1000)
                    
                except Exception as e:
                    error_count += 1
                    continue
            
            self.parent.after(0, self._translation_batch_completed, success_count, error_count, total_count, None, list(used_engines))
            
        except Exception as e:
            self.parent.after(0, self._translation_batch_completed, success_count, error_count, total_count, str(e), list(used_engines))
    
    def _translation_batch_completed(self, success: int, error: int, total: int, exception: str = None, used_engines: list = None) -> None:
        """เรียกเมื่อแปลชุดเสร็จสิ้น"""
        self.set_working(False)
        self.close_progress_dialog()
        
        self.refresh_grid()
        
        if exception:
            self.show_error(f"เกิดข้อผิดพลาด: {exception}")
            return
        
        message = f"แปลเสร็จสิ้น!\n\n"
        message += f"สำเร็จ: {success} บรรทัด\n"
        if error > 0:
            message += f"ล้มเหลว: {error} บรรทัด\n"
        message += f"รวม: {success + error} จาก {total} บรรทัด\n"
        
        if used_engines:
            message += f"\n🔧 ตัวแปลที่ใช้: {', '.join(used_engines)}"
        
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
🔍 บรรทัดที่มีเครื่องหมายแบ่ง: {separator_lines:,} บรรทัด"""
        
        self.show_success(status_text)
    
    def refresh_grid(self) -> None:
        """รีเฟรชตาราง"""
        self.update_grid_display()
    
    def skip_current_page(self) -> None:
        """ข้ามการแปลทั้งหน้าปัจจุบัน"""
        if not self.translation_data.lines:
            self.show_error("ไม่มีข้อมูลให้ดำเนินการ")
            return
        
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

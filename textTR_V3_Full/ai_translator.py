#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Translator Module using Google Gemini API
โมดูลแปลข้อความด้วย AI Gemini สำหรับ Text File Splitter & Merger GUI
"""

import re
from typing import Optional, Dict, Any, List, Tuple
from google.genai import types
from google import genai


class TextProtector:
    """
    คลาสสำหรับปกป้องข้อความที่ไม่ต้องการให้แปล
    เช่น คำสั่งเกม, ตัวแปร, หรืออักขระพิเศษ
    """
    
    # Default protection patterns
    DEFAULT_PATTERNS = {
        'curly_braces': r'\{[^}]*\}',           # {command}, {variable}
        'square_brackets': r'\[[^\]]*\]',        # [tag], [system]
        'angle_brackets': r'<[^>]*>',            # <html>, <xml>
        'variables': r'\$\w+|\%\w+\%',           # $variable, %variable%
        'urls': r'https?://[^\s]+',              # URLs
        'emails': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # emails
        'numbers_with_units': r'\b\d+[\.,]?\d*\s*(?:px|em|rem|%|pt|cm|mm|in)\b',  # CSS units
        'hex_colors': r'#[0-9A-Fa-f]{3,8}',     # hex colors
        'programming_vars': r'\b[a-zA-Z_]\w*\s*[=:]\s*[^;,\n]*',  # variable assignments
        'prefix_before_colon': r'^[^:]*:',       # ข้อความหน้าเครื่องหมาย : รวมทั้งเครื่องหมาย : เอง
    }
    
    def __init__(self, custom_patterns: Optional[Dict[str, str]] = None):
        """
        สร้าง TextProtector
        
        Args:
            custom_patterns: Dict ของ pattern ที่กำหนดเอง {name: regex_pattern}
        """
        self.patterns = self.DEFAULT_PATTERNS.copy()
        if custom_patterns:
            self.patterns.update(custom_patterns)
        
        self.enabled_patterns = set(self.patterns.keys())
        self.placeholder_prefix = "§PROTECTED_"
        self.placeholder_suffix = "§"
    
    def set_enabled_patterns(self, pattern_names: List[str]) -> None:
        """
        ตั้งค่า patterns ที่ต้องการใช้งาน
        
        Args:
            pattern_names: รายชื่อ patterns ที่ต้องการเปิดใช้งาน
        """
        self.enabled_patterns = set(pattern_names) & set(self.patterns.keys())
    
    def add_custom_pattern(self, name: str, pattern: str) -> None:
        """
        เพิ่ม custom pattern
        
        Args:
            name: ชื่อ pattern
            pattern: regex pattern
        """
        self.patterns[name] = pattern
        self.enabled_patterns.add(name)
    
    def protect_text(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        ปกป้องข้อความที่ไม่ต้องการให้แปล
        
        Args:
            text: ข้อความต้นฉบับ
            
        Returns:
            tuple: (ข้อความที่ป้องกันแล้ว, dict ของ placeholders)
        """
        if not text or not self.enabled_patterns:
            return text, {}
        
        protected_text = text
        placeholders = {}
        placeholder_counter = 0
        
        for pattern_name in self.enabled_patterns:
            if pattern_name not in self.patterns:
                continue
                
            pattern = self.patterns[pattern_name]
            
            def replace_match(match):
                nonlocal placeholder_counter
                placeholder_counter += 1
                placeholder = f"{self.placeholder_prefix}{placeholder_counter}{self.placeholder_suffix}"
                placeholders[placeholder] = match.group(0)
                return placeholder
            
            protected_text = re.sub(pattern, replace_match, protected_text, flags=re.IGNORECASE | re.MULTILINE)
        
        return protected_text, placeholders
    
    def restore_text(self, translated_text: str, placeholders: Dict[str, str]) -> str:
        """
        คืนข้อความที่ป้องกันไว้กลับเข้าไปในข้อความที่แปลแล้ว
        
        Args:
            translated_text: ข้อความที่แปลแล้ว
            placeholders: dict ของ placeholders ที่ได้จาก protect_text
            
        Returns:
            ข้อความที่คืนค่าแล้ว
        """
        if not translated_text or not placeholders:
            return translated_text
        
        restored_text = translated_text
        
        for placeholder, original_text in placeholders.items():
            restored_text = restored_text.replace(placeholder, original_text)
        
        return restored_text
    
    def handle_separator_prefix_translation(self, text: str, separator: str = ':') -> Tuple[str, bool]:
        """
        จัดการข้อความที่มีเครื่องหมายแบ่ง โดยแปลเฉพาะส่วนหลังเครื่องหมาย
        
        Args:
            text: ข้อความต้นฉบับ
            separator: เครื่องหมายแบ่ง (เช่น ':', '=', '|', '->')
            
        Returns:
            tuple: (ข้อความที่เตรียมแปล, มีเครื่องหมายแบ่งหรือไม่)
        """
        if separator not in text:
            return text, False
        
        # หาตำแหน่งเครื่องหมายแบ่งแรก
        separator_index = text.find(separator)
        prefix = text[:separator_index + len(separator)]  # รวมเครื่องหมายแบ่ง
        suffix = text[separator_index + len(separator):].strip()  # ข้อความหลังเครื่องหมายแบ่ง
        
        # ถ้าไม่มีข้อความหลังเครื่องหมายแบ่ง ให้ส่งคืนข้อความเดิม
        if not suffix:
            return text, False
        
        return suffix, True
    
    def handle_colon_prefix_translation(self, text: str) -> Tuple[str, bool]:
        """
        จัดการข้อความที่มีเครื่องหมาย : โดยแปลเฉพาะส่วนหลัง : (backward compatibility)
        
        Args:
            text: ข้อความต้นฉบับ
            
        Returns:
            tuple: (ข้อความที่เตรียมแปล, มีเครื่องหมาย : หรือไม่)
        """
        return self.handle_separator_prefix_translation(text, ':')
    
    def restore_separator_prefix_translation(self, original_text: str, translated_suffix: str, separator: str = ':') -> str:
        """
        รวมข้อความที่แปลแล้วกับส่วนหน้าเครื่องหมายแบ่ง
        
        Args:
            original_text: ข้อความต้นฉบับ
            translated_suffix: ข้อความที่แปลแล้ว (เฉพาะส่วนหลังเครื่องหมายแบ่ง)
            separator: เครื่องหมายแบ่ง (เช่น ':', '=', '|', '->')
            
        Returns:
            ข้อความที่รวมแล้ว
        """
        if separator not in original_text:
            return translated_suffix
        
        # หาตำแหน่งเครื่องหมายแบ่งแรก
        separator_index = original_text.find(separator)
        prefix = original_text[:separator_index + len(separator)]  # รวมเครื่องหมายแบ่ง
        
        # เพิ่มช่องว่างหลังเครื่องหมายแบ่งถ้ายังไม่มี
        if not prefix.endswith(' '):
            return f"{prefix} {translated_suffix}".strip()
        else:
            return f"{prefix}{translated_suffix}".strip()
    
    def restore_colon_prefix_translation(self, original_text: str, translated_suffix: str) -> str:
        """
        รวมข้อความที่แปลแล้วกับส่วนหน้าเครื่องหมาย : (backward compatibility)
        
        Args:
            original_text: ข้อความต้นฉบับ
            translated_suffix: ข้อความที่แปลแล้ว (เฉพาะส่วนหลัง :)
            
        Returns:
            ข้อความที่รวมแล้ว
        """
        return self.restore_separator_prefix_translation(original_text, translated_suffix, ':')
    
    def get_available_patterns(self) -> Dict[str, str]:
        """
        ดึงรายการ patterns ที่มีทั้งหมด
        
        Returns:
            Dict ของ patterns {name: description}
        """
        pattern_descriptions = {
            'curly_braces': 'ข้อความในปีกกา { }',
            'square_brackets': 'ข้อความในวงเล็บเหลี่ยม [ ]',
            'angle_brackets': 'ข้อความในวงเล็บมุม < >',
            'variables': 'ตัวแปร $var หรือ %var%',
            'urls': 'URL ลิงก์',
            'emails': 'อีเมล',
            'numbers_with_units': 'ตัวเลขพร้อมหน่วย (px, %, em)',
            'hex_colors': 'รหัสสี hex (#ffffff)',
            'programming_vars': 'การกำหนดค่าตัวแปร (var = value)',
            'prefix_before_colon': 'ข้อความหน้าเครื่องหมาย : (แปลเฉพาะหลัง :)',
        }
        
        result = {}
        for name in self.patterns.keys():
            result[name] = pattern_descriptions.get(name, f'Pattern: {name}')
        
        return result


class GeminiTranslator:
    """
    คลาสสำหรับแปลข้อความด้วย Google Gemini AI
    รองรับ custom prompt เพื่อให้การแปลเป็นธรรมชาติและอิงตามบทบาทได้มากขึ้น
    """
    
    # Default prompts สำหรับการแปลแต่ละประเภท
    DEFAULT_PROMPTS = {
        'general': "คุณเป็นนักแปลมืออาชีพ กรุณาแปลข้อความที่กำหนดให้อย่างถูกต้องและเป็นธรรมชาติ",
        'novel': "คุณเป็นนักแปลนิยายมืออาชีพ กรุณาแปลข้อความโดยให้ความสำคัญกับอารมณ์ บรรยากาศ และการพัฒนาตัวละคร",
        'game': "คุณเป็นนักแปลเกมมืออาชีพ กรุณาแปลข้อความโดยเก็บรักษาความหมายของเทคนิคเกม สกิล และบรรยากาศการผจญภัย",
        'dialogue': "คุณเป็นนักแปลบทสนทนามืออาชีพ กรุณาแปลข้อความโดยให้ความสำคัญกับการสื่อสารที่เป็นธรรมชาติและตรงกับบุคลิกตัวละคร",
        'technical': "คุณเป็นนักแปลเอกสารทางเทคนิคมืออาชีพ กรุณาแปลข้อความโดยรักษาความแม่นยำทางเทคนิคและคำศัพท์เฉพาะด้าน",
        'formal': "คุณเป็นนักแปลเอกสารทางการมืออาชีพ กรุณาแปลข้อความในรูปแบบที่สุภาพและเป็นทางการ"
    }
    
    # Language mappings สำหรับ Gemini
    LANGUAGE_MAPPING = {
        'auto': 'อัตโนมัติ',
        'en': 'อังกฤษ',
        'th': 'ไทย',
        'ja': 'ญี่ปุ่น',
        'ko': 'เกาหลี',
        'zh': 'จีน',
        'zh-cn': 'จีนตัวย่อ',
        'zh-tw': 'จีนตัวเต็ม',
        'de': 'เยอรมัน',
        'fr': 'ฝรั่งเศส',
        'es': 'สเปน',
        'it': 'อิตาลี',
        'pt': 'โปรตุเกส',
        'ru': 'รัสเซีย',
        'ar': 'อารบิก',
        'hi': 'ฮินดี',
        'vi': 'เวียดนาม',
        'id': 'อินโดนีเซีย',
        'ms': 'มาเลย์',
        'tl': 'ฟิลิปปินส์'
    }
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash", 
                 text_protector: Optional[TextProtector] = None):
        """
        สร้าง GeminiTranslator instance
        
        Args:
            api_key: Google Gemini API key
            model_name: ชื่อโมเดล Gemini ที่ใช้ (default: gemini-2.5-flash)
            text_protector: TextProtector instance สำหรับป้องกันข้อความพิเศษ
        """
        self.api_key = api_key
        self.model_name = model_name
        self.client = None
        self.text_protector = text_protector or TextProtector()
        self._initialize_client()
    
    def _initialize_client(self) -> bool:
        """
        เตรียม Gemini client
        
        Returns:
            True ถ้าเตรียมสำเร็จ, False ถ้าล้มเหลว
        """
        try:
            self.client = genai.Client(api_key=self.api_key)
            return True
        except Exception as e:
            print(f"Failed to initialize Gemini client: {e}")
            return False
    
    def is_ready(self) -> bool:
        """
        ตรวจสอบว่า translator พร้อมใช้งานหรือไม่
        
        Returns:
            True ถ้าพร้อมใช้งาน
        """
        return self.client is not None
    
    def translate_text(
        self, 
        text: str, 
        source_lang: str = 'auto', 
        target_lang: str = 'th',
        prompt_type: str = 'general',
        custom_prompt: Optional[str] = None,
        protect_special_text: bool = True,
        translate_only_after_separator: bool = False,
        custom_separator: str = ':'
    ) -> str:
        """
        แปลข้อความด้วย Gemini AI
        
        Args:
            text: ข้อความที่จะแปล
            source_lang: ภาษาต้นฉบับ (ใช้ code เช่น 'en', 'ja')
            target_lang: ภาษาเป้าหมาย (ใช้ code เช่น 'th', 'en')
            prompt_type: ประเภท prompt ('general', 'novel', 'game', 'dialogue', 'technical', 'formal')
            custom_prompt: custom prompt (ถ้าระบุจะใช้แทน default prompt)
            protect_special_text: ป้องกันข้อความพิเศษ (เช่น {commands}, [tags])
            translate_only_after_separator: แปลเฉพาะข้อความหลังเครื่องหมายแบ่ง (เช่น Cook_1: Fried Rice จะแปลเฉพาะ Fried Rice)
            custom_separator: เครื่องหมายแบ่ง (เช่น ':', '=', '|', '->')
        
        Returns:
            ข้อความที่แปลแล้ว
        """
        if not self.is_ready():
            raise Exception("Gemini client ไม่พร้อมใช้งาน")
        
        if not text or not text.strip():
            return text
        
        try:
            # จัดการแปลเฉพาะหลังเครื่องหมายแบ่ง
            original_full_text = text
            has_separator = False
            
            if translate_only_after_separator:
                text_to_translate, has_separator = self.text_protector.handle_separator_prefix_translation(text, custom_separator)
                if has_separator:
                    text = text_to_translate
                # ถ้าไม่มีเครื่องหมายแบ่ง หรือไม่มีข้อความหลังเครื่องหมายแบ่ง ให้ส่งคืนข้อความเดิม
                elif not has_separator or not text.strip():
                    return original_full_text
            
            # ป้องกันข้อความพิเศษ
            protected_text = text
            placeholders = {}
            
            if protect_special_text and self.text_protector:
                protected_text, placeholders = self.text_protector.protect_text(text)
            
            # ถ้าไม่มีข้อความที่ต้องแปล (ทั้งหมดเป็น protected text)
            if not protected_text.strip() or protected_text.strip() in placeholders.values():
                return original_full_text if translate_only_after_separator and has_separator else text
            
            # เตรียม system instruction
            system_instruction = self._build_system_instruction(
                source_lang, target_lang, prompt_type, custom_prompt, placeholders
            )
            
            # เตรียม user message
            user_message = self._build_user_message(protected_text, source_lang, target_lang)
            
            # เรียก Gemini API
            response = self.client.models.generate_content(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3,  # ลดความสุ่มเพื่อให้การแปลคงที่
                    top_p=0.8,
                    max_output_tokens=2000
                ),
                contents=user_message
            )
            
            if response and hasattr(response, 'text'):
                # ทำความสะอาดผลลัพธ์
                translated_text = self._clean_translation_result(response.text)
                
                # คืนข้อความที่ป้องกันไว้
                if protect_special_text and self.text_protector and placeholders:
                    translated_text = self.text_protector.restore_text(translated_text, placeholders)
                
                # รวมกับส่วนหน้าเครื่องหมายแบ่ง ถ้าเป็นการแปลเฉพาะหลังเครื่องหมายแบ่ง
                if translate_only_after_separator and has_separator:
                    translated_text = self.text_protector.restore_separator_prefix_translation(
                        original_full_text, translated_text, custom_separator
                    )
                
                return translated_text
            else:
                raise Exception("ไม่ได้รับผลลัพธ์จาก Gemini API")
                
        except Exception as e:
            raise Exception(f"การแปลด้วย Gemini ล้มเหลว: {str(e)}")
    
    def _build_system_instruction(
        self, 
        source_lang: str, 
        target_lang: str, 
        prompt_type: str, 
        custom_prompt: Optional[str],
        placeholders: Optional[Dict[str, str]] = None
    ) -> str:
        """
        สร้าง system instruction สำหรับ Gemini
        
        Args:
            source_lang: ภาษาต้นฉบับ
            target_lang: ภาษาเป้าหมาย
            prompt_type: ประเภท prompt
            custom_prompt: custom prompt
            placeholders: dict ของ protected text placeholders
            
        Returns:
            System instruction ที่สมบูรณ์
        """
        # ใช้ custom prompt ถ้าระบุมา ไม่งั้นใช้ default
        base_prompt = custom_prompt if custom_prompt else self.DEFAULT_PROMPTS.get(prompt_type, self.DEFAULT_PROMPTS['general'])
        
        # เพิ่มข้อมูลภาษา
        source_lang_name = self.LANGUAGE_MAPPING.get(source_lang, source_lang)
        target_lang_name = self.LANGUAGE_MAPPING.get(target_lang, target_lang)
        
        system_instruction = f"""{base_prompt}

คำแนะนำการแปล:
- แปลจากภาษา{source_lang_name}เป็นภาษา{target_lang_name}
- รักษาความหมายต้นฉบับให้ครบถ้วน
- ใช้ภาษาที่เป็นธรรมชาติและเข้าใจง่าย
- ไม่ต้องเพิ่มคำอธิบายหรือหมายเหตุใดๆ
- ตอบเฉพาะข้อความที่แปลแล้วเท่านั้น
- ถ้าข้อความมีตัวอักษรพิเศษหรือสัญลักษณ์ ให้รักษาไว้ตามเดิม"""

        # เพิ่มคำแนะนำเกี่ยวกับ protected text
        if placeholders:
            system_instruction += f"""

คำแนะนำพิเศษ:
- ข้อความที่ขึ้นต้นด้วย "{self.text_protector.placeholder_prefix}" และลงท้ายด้วย "{self.text_protector.placeholder_suffix}" เป็นข้อความพิเศษ
- ห้ามแปลข้อความพิเศษเหล่านี้ ให้รักษาไว้ตามเดิมทุกตัวอักษร
- ข้อความพิเศษเหล่านี้อาจเป็นคำสั่งเกม, ตัวแปร, หรือรหัสพิเศษ"""
        
        return system_instruction
    
    def _build_user_message(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        สร้าง user message สำหรับ Gemini
        
        Args:
            text: ข้อความที่จะแปล
            source_lang: ภาษาต้นฉบับ
            target_lang: ภาษาเป้าหมาย
            
        Returns:
            User message ที่พร้อมส่ง
        """
        return f"กรุณาแปลข้อความต่อไปนี้:\n\n{text}"
    
    def _clean_translation_result(self, result: str) -> str:
        """
        ทำความสะอาดผลลัพธ์การแปล
        
        Args:
            result: ผลลัพธ์ดิบจาก Gemini
            
        Returns:
            ผลลัพธ์ที่ทำความสะอาดแล้ว
        """
        if not result:
            return ""
        
        # ลบ markdown formatting ถ้ามี
        result = re.sub(r'```.*?\n', '', result)
        result = re.sub(r'\n```', '', result)
        
        # ลบ whitespace ที่ไม่จำเป็น
        result = result.strip()
        
        # ลบบรรทัดที่เป็นคำอธิบายหรือหมายเหตุ
        lines = result.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # ข้ามบรรทัดที่เป็นคำอธิบาย
            if (line.startswith('[') and line.endswith(']')) or \
               (line.startswith('(') and line.endswith(')')) or \
               line.startswith('หมายเหตุ:') or \
               line.startswith('คำอธิบาย:') or \
               line.startswith('แปลว่า:'):
                continue
            
            if line:  # เฉพาะบรรทัดที่ไม่ว่าง
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines) if cleaned_lines else result
    
    def translate_lines(
        self, 
        lines: list, 
        source_lang: str = 'auto', 
        target_lang: str = 'th',
        prompt_type: str = 'general',
        custom_prompt: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> list:
        """
        แปลหลายบรรทัดพร้อมกัน
        
        Args:
            lines: รายการข้อความที่จะแปล
            source_lang: ภาษาต้นฉบับ
            target_lang: ภาษาเป้าหมาย
            prompt_type: ประเภท prompt
            custom_prompt: custom prompt
            progress_callback: callback function สำหรับแสดงความคืบหน้า
        
        Returns:
            รายการข้อความที่แปลแล้ว
        """
        if not self.is_ready():
            raise Exception("Gemini client ไม่พร้อมใช้งาน")
        
        translated_lines = []
        total_lines = len(lines)
        
        for i, line in enumerate(lines):
            try:
                # แจ้งความคืบหน้า
                if progress_callback:
                    progress_callback(i, total_lines, f"แปลบรรทัดที่ {i+1}/{total_lines}")
                
                # แปลข้อความ
                if line.strip():
                    translated = self.translate_text(
                        line, source_lang, target_lang, prompt_type, custom_prompt
                    )
                    translated_lines.append(translated)
                else:
                    translated_lines.append(line)  # รักษาบรรทัดว่าง
                    
            except Exception as e:
                print(f"การแปลบรรทัดที่ {i+1} ล้มเหลว: {e}")
                translated_lines.append(line)  # ใช้ข้อความเดิมถ้าแปลไม่ได้
        
        # แจ้งเสร็จสิ้น
        if progress_callback:
            progress_callback(total_lines, total_lines, "แปลเสร็จสิ้น")
        
        return translated_lines
    
    def test_connection(self) -> tuple:
        """
        ทดสอบการเชื่อมต่อกับ Gemini API
        
        Returns:
            (success: bool, message: str)
        """
        try:
            if not self.is_ready():
                return False, "Gemini client ไม่พร้อมใช้งาน"
            
            # ทดสอบการแปลง่ายๆ
            test_result = self.translate_text("Hello", "en", "th", "general")
            
            if test_result and test_result.strip():
                return True, f"เชื่อมต่อสำเร็จ - ทดสอบการแปล: '{test_result}'"
            else:
                return False, "ไม่ได้รับผลลัพธ์การแปลทดสอบ"
                
        except Exception as e:
            return False, f"การเชื่อมต่อล้มเหลว: {str(e)}"
    
    def get_available_prompts(self) -> Dict[str, str]:
        """
        ดึงรายการ prompt ที่มีให้ใช้งาน
        
        Returns:
            Dict ของ prompt types และคำอธิบาย
        """
        return {
            'general': 'ทั่วไป - สำหรับข้อความทั่วไป',
            'novel': 'นิยาย - เน้นอารมณ์และบรรยากาศ',
            'game': 'เกม - เน้นเทคนิคและการผจญภัย',
            'dialogue': 'บทสนทนา - เน้นความเป็นธรรมชาติ',
            'technical': 'เทคนิค - เน้นความแม่นยำ',
            'formal': 'ทางการ - เน้นความสุภาพ'
        }
    
    def get_prompt_template(self, prompt_type: str) -> str:
        """
        ดึง template ของ prompt
        
        Args:
            prompt_type: ประเภท prompt
            
        Returns:
            Template ของ prompt
        """
        return self.DEFAULT_PROMPTS.get(prompt_type, self.DEFAULT_PROMPTS['general'])
    
    def get_text_protector(self) -> TextProtector:
        """
        ดึง TextProtector instance
        
        Returns:
            TextProtector instance
        """
        return self.text_protector
    
    def set_protection_patterns(self, pattern_names: List[str]) -> None:
        """
        ตั้งค่า protection patterns ที่ต้องการใช้
        
        Args:
            pattern_names: รายชื่อ patterns ที่ต้องการเปิดใช้งาน
        """
        if self.text_protector:
            self.text_protector.set_enabled_patterns(pattern_names)
    
    def add_custom_protection_pattern(self, name: str, pattern: str) -> None:
        """
        เพิ่ม custom protection pattern
        
        Args:
            name: ชื่อ pattern
            pattern: regex pattern
        """
        if self.text_protector:
            self.text_protector.add_custom_pattern(name, pattern)
    
    def get_available_protection_patterns(self) -> Dict[str, str]:
        """
        ดึงรายการ protection patterns ที่มีให้ใช้
        
        Returns:
            Dict ของ patterns {name: description}
        """
        if self.text_protector:
            return self.text_protector.get_available_patterns()
        return {}


# Utility functions
def create_gemini_translator(
    api_key: str, 
    model_name: str = "gemini-2.5-flash",
    protection_patterns: Optional[List[str]] = None,
    custom_patterns: Optional[Dict[str, str]] = None
) -> Optional[GeminiTranslator]:
    """
    สร้าง GeminiTranslator instance และทดสอบการเชื่อมต่อ
    
    Args:
        api_key: Google Gemini API key
        model_name: ชื่อโมเดล Gemini
        protection_patterns: รายการ protection patterns ที่ต้องการใช้
        custom_patterns: custom patterns เพิ่มเติม
        
    Returns:
        GeminiTranslator instance หรือ None ถ้าล้มเหลว
    """
    try:
        # สร้าง TextProtector
        text_protector = TextProtector(custom_patterns)
        
        if protection_patterns:
            text_protector.set_enabled_patterns(protection_patterns)
        else:
            # Default: เปิดใช้ curly_braces และ square_brackets สำหรับเกม
            text_protector.set_enabled_patterns(['curly_braces', 'square_brackets'])
        
        translator = GeminiTranslator(api_key, model_name, text_protector)
        success, message = translator.test_connection()
        
        if success:
            return translator
        else:
            print(f"การสร้าง Gemini translator ล้มเหลว: {message}")
            return None
            
    except Exception as e:
        print(f"การสร้าง Gemini translator ล้มเหลว: {e}")
        return None


def validate_api_key(api_key: str) -> bool:
    """
    ตรวจสอบความถูกต้องของ API key
    
    Args:
        api_key: API key ที่จะตรวจสอบ
        
    Returns:
        True ถ้า API key ถูกต้อง
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    # ตรวจสอบรูปแบบพื้นฐานของ Google API key
    if not api_key.startswith('AIza') or len(api_key) < 35:
        return False
    
    return True
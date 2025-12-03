#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translation Engine
เครื่องมือแปลข้อความที่รองรับหลายวิธี รวมทั้ง AI Gemini
"""

from typing import Optional


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
                    result = engine(text, source_lang, target_lang, prompt_type, custom_prompt, 
                                   translate_only_after_separator, custom_separator)
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
                protect_special_text=True, 
                translate_only_after_separator=translate_only_after_separator, 
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
        
        dict_key = (source_lang, target_lang)
        if dict_key in basic_dict:
            words = text.lower().split()
            translated_words = []
            
            for word in words:
                if word in basic_dict[dict_key]:
                    translated = basic_dict[dict_key][word]
                    if translated:
                        translated_words.append(translated)
                else:
                    translated_words.append(word)
            
            if translated_words:
                return ' '.join(translated_words)
        
        return f"[ต้องติดตั้ง translation library เพื่อแปลจาก {source_lang} เป็น {target_lang}]: {text}"

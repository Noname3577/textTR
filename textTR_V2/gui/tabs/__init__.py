#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI Tabs Package
โมดูล Tabs สำหรับแอปพลิเคชัน GUI
"""

from gui.tabs.splitter_tab import FileSplitterTab
from gui.tabs.merger_tab import FileMergerTab
from gui.tabs.viewer_tab import FileViewerTab
from gui.tabs.settings_tab import SettingsTab
from gui.tabs.translation_tab import TranslationTab

__all__ = [
    'FileSplitterTab',
    'FileMergerTab',
    'FileViewerTab',
    'SettingsTab',
    'TranslationTab'
]
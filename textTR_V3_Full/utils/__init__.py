#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilities package
"""

from utils.file_utils import (
    format_file_size,
    format_timestamp,
    get_file_info,
    count_lines_in_file,
    read_file_lines,
    write_file_lines,
    validate_file_path,
    validate_directory_path,
    create_backup_file,
    get_unique_filename,
    sanitize_filename,
    is_text_file
)

from utils.json_utils import (
    is_json_file,
    read_json_file,
    write_json_file,
    json_to_text_lines,
    text_lines_to_json,
    extract_json_strings,
    update_json_strings,
    get_json_structure_info,
    count_lines_in_json
)

from utils.ui_utils import (
    center_window,
    open_file_manager,
    show_error_dialog,
    show_success_dialog,
    show_warning_dialog,
    truncate_text,
    safe_int_conversion,
    calculate_pagination,
    get_page_items
)

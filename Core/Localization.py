#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import threading
import xml.etree.ElementTree as ElementTree
from xml.sax.saxutils import escape


class Localization:
    """
    Android-style string resource loader.

    Resource layout:
      Resources/values/strings.xml       default language
      Resources/values-zh/strings.xml    Chinese fallback
      Resources/values-<code>/strings.xml
    """

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if Localization._initialized:
            return
        with Localization._lock:
            if Localization._initialized:
                return
        self.resources_dir = os.path.join(os.getcwd(), "Resources")
        self.default_language = "en"
        self.language = "en"
        self.default_strings = {}
        self.current_strings = {}
        Localization._initialized = True

    def initialize(self, resources_dir=None, language=None, default_language="en"):
        self.resources_dir = resources_dir or self.resources_dir
        self.default_language = default_language or "en"
        self.language = language or self.default_language
        self.default_strings = self._load_language(self.default_language)
        self.current_strings = self._load_language(self.language)

    def get(self, key, **kwargs):
        value = self.current_strings.get(key)
        if value is None:
            value = self.default_strings.get(key)
        if value is None:
            value = key
        if kwargs:
            try:
                return value.format(**kwargs)
            except (KeyError, IndexError, ValueError):
                return value
        return value

    def _load_language(self, language):
        paths_to_try = []
        if language == self.default_language:
            paths_to_try.append(os.path.join(self.resources_dir, "values", "strings.xml"))
        else:
            paths_to_try.append(os.path.join(self.resources_dir, "values-" + language, "strings.xml"))
            if "-" in language:
                paths_to_try.append(os.path.join(self.resources_dir, "values-" + language.split("-", 1)[0], "strings.xml"))

        for path in paths_to_try:
            if os.path.exists(path):
                return self._parse_strings_xml(path)
        return {}

    @staticmethod
    def _parse_strings_xml(path):
        result = {}
        tree = ElementTree.parse(path)
        root = tree.getroot()
        for string_node in root.findall("string"):
            name = string_node.attrib.get("name")
            if not name:
                continue
            result[name] = "".join(string_node.itertext())
        return result


class StringResourceChecker:
    """
    Compare default English strings against the selected language resource.
    """

    DEFAULT_LANGUAGE = "en"

    @staticmethod
    def get_language_resource_path(resources_dir, language):
        if language == StringResourceChecker.DEFAULT_LANGUAGE:
            return os.path.join(resources_dir, "values", "strings.xml")
        return os.path.join(resources_dir, "values-" + language, "strings.xml")

    @staticmethod
    def get_missing_strings(resources_dir=None, language=None):
        if resources_dir is None or language is None:
            from Core.GlobalConfigUtils import GlobalConfigInfo
            global_config = GlobalConfigInfo()
            resources_dir = resources_dir or global_config.get_value("resource_dir") or "./Resources"
            language = language or global_config.get_value("language") or StringResourceChecker.DEFAULT_LANGUAGE

        default_path = StringResourceChecker.get_language_resource_path(
            resources_dir, StringResourceChecker.DEFAULT_LANGUAGE)
        selected_path = StringResourceChecker.get_language_resource_path(resources_dir, language)

        default_strings = Localization._parse_strings_xml(default_path)
        if os.path.abspath(default_path) == os.path.abspath(selected_path):
            return {}
        if not os.path.exists(selected_path):
            return default_strings

        selected_strings = Localization._parse_strings_xml(selected_path)
        missing_strings = {}
        for key, value in default_strings.items():
            if key not in selected_strings:
                missing_strings[key] = value
        return missing_strings

    @staticmethod
    def build_xml_string_entry(key, value):
        return f'    <string name="{escape(key)}">{escape(value)}</string>'


def t(key, **kwargs):
    return Localization().get(key, **kwargs)

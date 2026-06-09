#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import threading
import xml.etree.ElementTree as ElementTree


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


def t(key, **kwargs):
    return Localization().get(key, **kwargs)

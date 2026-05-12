#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading

import Core.LogUtils as LogUtils


class GlobalConfigUtils:
    TAG = "GlobalConfigUtils"
    def __init__(self):
        self.my_logger = LogUtils.LogUtils()

    def parse_key_value_file(self, path_to_file):
        """
        Parse key-value pairs from a file, returns a dict.
        """
        result = {}
        line_num = 0

        with open(path_to_file, 'r', encoding='utf-8') as file:
            for raw_line in file:
                line_num += 1
                line = raw_line.rstrip('\n\r')
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                if '=' not in stripped:
                    raise ValueError(f"Missing \"=\" in line {line_num}, content: {stripped}")

                # Find first equal
                eq_pos = stripped.find('=')
                key_part = stripped[:eq_pos]
                value_part = stripped[eq_pos + 1:]

                # Check space bar
                if key_part.endswith(' ') or value_part.startswith(' '):
                    raise ValueError(
                        f"Line {line_num}, no space allowed around \"=\": {stripped}"
                    )

                # Extract key
                key = key_part

                # Check value format
                if not (value_part.startswith('"') and value_part.endswith('"')):
                    raise ValueError(
                        f"Line {line_num}, invalid value format, \"\" are required: {value_part}"
                    )
                value = value_part[1:-1]
                if key in result:
                    self.my_logger.log("W", f"Line {line_num}, duplicated key '{key}' ! Overriding old value.", self.TAG)

                result[key] = value

        return result

    def save_config_to_file(self, path_to_file, dict_to_save):
        with open(path_to_file, 'w', encoding='utf-8') as file:
            for key in dict_to_save:
                file.write(self.__build_key_value_pair_line(key, dict_to_save[key]) + "\n")

    @staticmethod
    def __build_key_value_pair_line(key, value) -> str:
        return f"{key}=\"{value}\""


class GlobalConfigInfo:

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
        if GlobalConfigInfo._initialized:
            return
        with GlobalConfigInfo._lock:
            if GlobalConfigInfo._initialized:
                return
        self.__my_config_utils = GlobalConfigUtils()
        self.__config_dict = {}
        GlobalConfigInfo._initialized = True

    def clear_values(self):
        self.__config_dict = {}

    def get_value(self, key):
        return self.__config_dict.get(key, None)

    def get_keys(self):
        return self.__config_dict.keys()

    def get_values(self, keys):
        value_list = []
        for key in keys:
            value_list.append(self.get_value(key))
        return value_list

    def set_value(self, key, value): # This method only affects the config copy in memory, to permanently modify the config, edit the config file.
        self.__config_dict[key] = value

    def set_values(self, keys, value_list):
        for key in keys:
            self.set_value(key, value_list[key])

    def set_values_by_dict(self, dictionary):
        for key in dictionary:
            self.set_value(key, dictionary[key])
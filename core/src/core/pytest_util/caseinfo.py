#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 熊🐻来个🥬
# @Date:  2025/9/20
# @Description: [对文件功能等的简要描述（可自行添加）]
"""caseinfo used for pytest testcase fixture"""

import pytest
from allure_commons.types import LabelType
from allure_pytest.utils import ALLURE_DISPLAY_NAME_MARK, ALLURE_LABEL_MARK, allure_name
from allure_pytest.utils import ALLURE_DESCRIPTION_MARK
from allure_pytest.utils import get_marker_value
from allure_pytest.utils import allure_label
from allure_pytest.utils import allure_title


class SafeTupleComparator(tuple):
    def __lt__(self, other):
        return str(self) < str(other)

def safe_sort(values: []):
    return sorted(values, key=SafeTupleComparator)

class CaseInfoUtil:
    """utility class used for caseinfo.py"""
    DESCRIPTION = ALLURE_DESCRIPTION_MARK
    TITLE = ALLURE_DISPLAY_NAME_MARK
    PARAMETRIZE = 'parametrize'
    OWNER = 'owner'
    ZONE = 'zone'
    VERSION = 'version'
    SKIP = 'skip'
    PRIORITY_DICT = {
        'blocker': 'P0',
        'critical': 'P1',
        'normal': 'P2'
    }

    @classmethod
    def label(cls, label_type, *labels):
        label = getattr(pytest.mark, ALLURE_LABEL_MARK)
        return label(*labels, label_type=label_type)

    @classmethod
    def get_title(cls, item):
        return allure_title(item)

    @classmethod
    def get_priority(cls, item):
        labels = allure_label(item, LabelType.SEVERITY)
        if not labels:
            return None
        return cls.PRIORITY_DICT.get(labels[0])

    @classmethod
    def get_owner(cls, item):
        return get_marker_value(item, cls.OWNER)

    @classmethod
    def get_zone(cls, item):
        return get_marker_value(item, cls.ZONE)

    @classmethod
    def get_version(cls, item):
        return get_marker_value(item, cls.VERSION)

    @classmethod
    def has_parametrize_ids(cls, item):
        for mark in item.iter_markers(name=cls.PARAMETRIZE):
            if not mark.kwargs.get('ids'):
                return False
        return True

    @classmethod
    def get_parametrize_marks(cls, item):
        return list(item.iter_markers(name=cls.PARAMETRIZE))

    @classmethod
    def get_allure_name(cls, item):
        params = item.callspec.params if hasattr(item, 'callspec') else {}
        try:
            allure_name_result = allure_name(item, params)
        except KeyError:
            allure_name_result = allure_title(item)
        return allure_name_result

    @classmethod
    def update_allure_title(cls, item, name):
        title_marker = getattr(pytest.mark, cls.TITLE)
        item.add_marker(title_marker(name), append=False)


class CaseInfo:
    """case info class, used for pytest fixture"""

    @staticmethod
    def title(title_value):
        title = getattr(pytest.mark, CaseInfoUtil.TITLE)
        return title(title_value)

    @staticmethod
    def owner(owner_value):
        owner_mark = getattr(pytest.mark, CaseInfoUtil.OWNER)
        return owner_mark(owner_value)

    @staticmethod
    def priority(test_priority):
        for key, value in CaseInfoUtil.PRIORITY_DICT.items():
            if test_priority == value:
                return CaseInfoUtil.label(LabelType.SEVERITY, key)
        return CaseInfoUtil.label(LabelType.SEVERITY, test_priority)

    @staticmethod
    def zone(test_zone):
        zone_dec = getattr(pytest.mark, CaseInfoUtil.ZONE)
        return zone_dec(test_zone)

    @staticmethod
    def version(test_version):
        version_dec = getattr(pytest.mark, CaseInfoUtil.VERSION)
        return version_dec(test_version)

    @staticmethod
    def skip(reason):
        skip_dec = getattr(pytest.mark, CaseInfoUtil.SKIP)
        return skip_dec(reason=reason)

    @staticmethod
    def parametrize(arg_dicts, indirect=False, scope=None, sequential=False):
        """Method used with generated/parameterized tests, can be used to decorate
        your test_demo function with the parameters.

        Each dict in your list represents a generated test_demo.
        The keys in that dict are the parameters to be used for that generated test_demo
        """
        if not arg_dicts or len(arg_dicts) == 0:
            raise ValueError('[parametrize]: list cannot be none or empty')
        if isinstance(arg_dicts, dict):
            arg_dicts = [arg_dicts]

        arg_keys = set()
        for arg_dict in arg_dicts:
            arg_keys = arg_keys.union(set(arg_dict.keys()))
        arg_keys = sorted(arg_keys)

        ids = [arg_dict.get('desc', '') for arg_dict in arg_dicts]
        if 'desc' in arg_keys:
            arg_keys.remove('desc')
        # 如果有的数据驱动没有写desc，那么清空ids
        ids = ids if len(arg_dicts) == len(ids) else None
        arg_values = list()
        for arg_dict in arg_dicts:
            arg_value = tuple(arg_dict.get(key) for key in arg_keys)
            arg_values.append(arg_value)
        parametrize_dec = getattr(pytest.mark, CaseInfoUtil.PARAMETRIZE)

        if not sequential:
            arg_values = safe_sort(arg_values)
        return parametrize_dec(argnames=arg_keys, argvalues=arg_values,
                               indirect=indirect, ids=ids, scope=scope)

    @staticmethod
    def feature(*features):
        return CaseInfoUtil.label(LabelType.FEATURE, *features)

    @staticmethod
    def story(*stories):
        return CaseInfoUtil.label(LabelType.STORY, *stories)

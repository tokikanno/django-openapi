# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function


SCHEMA_ERROR_TYPE_SET = {
    'TYPE_MISMATCH',
    'VALUE_NOT_IN_ENUM',
    'VALUE_MUST_GREATER_THAN',
    'VALUE_MUST_GREATER_EQUAL_THAN',
    'VALUE_MUST_LESSER_THAN',
    'VALUE_MUST_LESSER_EQUAL_THAN',
    'VALUE_NOT_MUTLIPLE_OF',
    'ARRAY_HAS_TOO_FEW_ITEMS',
    'ARRAY_HAS_TOO_MANY_ITEMS',
    'ARRAY_HAS_NON_UNIQUE_ITEM',
    'TEXT_TOO_LONG',
    'TEXT_TOO_SHORT',
    'REGEX_NOT_MATCH',
    'FIELD_IS_REQUIRED',
}

NO_DEFULAT_VALUE = object()
NOT_SET = object()

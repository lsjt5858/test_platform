#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 熊🐻来个🥬
# @Date:  2025/9/17
# @Description: [对文件功能等的简要描述（可自行添加）]
import  os
from core.data_util.schema_loader import SchemaLoader

file_path = os.path.dirname(__file__)
(dirname, _) = os.path.split(file_path)
schema_path = os.path.join(dirname, 'schemas')

USER_SCHEMA_LOADER = SchemaLoader(schema_path)
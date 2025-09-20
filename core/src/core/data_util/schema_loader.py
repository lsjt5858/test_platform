#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 熊🐻来个🥬
# @Date:  2025/9/20
# @Description: [对文件功能等的简要描述（可自行添加）]
import os
from jsonschema import RefResolver
from core.data_util.data_file_loader import DataFileLoader


class SchemaLoader:
    """Class to load JSON schemas and schema stores, as well as to help resolve references"""
    def __init__(self, *schema_dirs):
        """Instantiates the schema store from the schema path"""
        self.schema_store = {}
        self.load_dir(*schema_dirs)

    def load_dir(self, *schema_dirs):
        """Adds another directory of schemas into the schema store"""
        for schema_folder in schema_dirs:
            schema_loader = DataFileLoader(schema_folder)
            for file in os.listdir(schema_folder):
                if file[-5:] == ".json":
                    schema = schema_loader.get_content(file)
                    schema_id = schema.get("$id")
                    self.schema_store[schema_id] = schema

    def get_schema(self, schema_id):
        """Gets a schema without resolving references from the schema store"""
        return self.schema_store[schema_id]

    def get_schema_ref_resolver(self, schema_id):
        """Gets a schema and a reference resolver for said schema from the schema store"""
        return self.schema_store[schema_id], RefResolver.from_schema(
            self.get_schema(schema_id),
            store=self.schema_store
        )

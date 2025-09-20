#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 熊🐻来个🥬
# @Date:  2025/9/20
# @Description: [对文件功能等的简要描述（可自行添加）]
import datetime
import json
import sys
import uuid

CURRENT_MODULE = sys.modules[__name__]

from jsonschema import Draft4Validator


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def is_valid_int(val):
    try:
        int(val)
        return True
    except ValueError:
        return False


def is_valid_str(val):
    try:
        str(val)
        return True
    except ValueError:
        return False


def is_valid_datetime(val, dt_format="%Y-%m-%dT%H:%M:%f"):
    try:
        val = val.split('.')[0] + val.split('.')[0][:3]
        datetime.datetime.strptime(val, dt_format)
        return True
    except ValueError:
        return False


def value_validator(value, reference):
    if str(reference).startswith('validate_'):
        data = reference.split('_')
        function_name = data[1]

        try:
            validator = getattr(CURRENT_MODULE, 'is_valid_' + str(function_name))
        except AttributeError:
            raise AttributeError(f'please check the validator name {str(reference)}')

        if len(data) == 2:
            return validator(value)
        elif len(data) == 3:
            return validator(value, data[2])
        else:
            raise ValueError(f'please check {str(reference)}')

    else:
        return value == reference


def jsonschema_validator(schema, data):
    validator = Draft4Validator(schema)
    errors = list(validator.iter_errors(data))
    if errors:
        print("JSON data is not in expected format:")
        for error in errors:
            print(error)
        return False
    else:
        return True


def recursive_dict_compare(input_dict, reference_dict):
    """
    Recursively compares two dictionaries
    value1 is reference
    value2 is input_dict
    """
    if len(reference_dict) != len(input_dict):
        raise AssertionError(f'the number of dict key is not matched!')

    for key, value1 in reference_dict.items():
        value2 = input_dict.get(key)
        if isinstance(value1, dict) and isinstance(value2, dict):
            recursive_dict_compare(value1, value2)
        elif isinstance(value1, list) and isinstance(value2, list):
            if len(value1) != len(value2):
                return False
            for i in range(len(value1)):
                if isinstance(value1[i], dict) and isinstance(value2[i], dict):
                    recursive_dict_compare(value1[i], value2[i])
                elif value1[i] != value2[i]:
                    raise AssertionError(f'{value1[i]} != {value2[i]}, please check the key {key}')
        else:
            if not value_validator(value1, value2):
                raise AssertionError(f'{value1} != {value2}, please check the key {key}')
    return True


if __name__ == "__main__":
    d1 = """
      {
      "data": [
          {
              "sessionID": "8559c454-9e61-4a7e-9a1c-eb64fd824e5f",
              "status": "SUCCESS",
              "sqlStatement": "USE auot_udf_test",
              "executionType": "COMMAND",
              "startTime": "2023-02-15T02:49:38.336959562Z",
              "endTime": "2023-02-15T02:49:38.352654767Z",
              "columns": [
                  {
                      "name": "Query",
                      "type": "String",
                      "nullable": false
                  }
              ],
              "rows": [
                  [
                      "CREATE FUNCTION `auot_udf_test`.`udf_linear_eq`nAS (x, k, b) -> (k * x) + b"
                  ]
              ],
              "rowsNum": 1,
              "durationInMs": 18,
              "vwResumeDurationInMs": 0,
              "errorMessage": null
          }
      ]
    }
    """

    d1 = json.loads(d1)

    reference = """
      {
      "data": [
          {
              "sessionID": "validate_uuid",
              "status": "SUCCESS",
              "sqlStatement": "USE auot_udf_test",
              "executionType": "COMMAND",
              "startTime": "validate_datetime",
              "endTime": "validate_datetime_%Y-%m-%dT%H:%M:%f",
              "columns": [
                  {
                      "name": "Query",
                      "type": "String",
                      "nullable": false
                  }
              ],
              "rows": [
                  [
                      "CREATE FUNCTION `auot_udf_test`.`udf_linear_eq`nAS (x, k, b) -> (k * x) + b"
                  ]
              ],
              "rowsNum": 1,
              "durationInMs": 18,
              "vwResumeDurationInMs": 0,
              "errorMessage": null
          }
      ]
    }
    """

    d2 = json.loads(reference)

    print(recursive_dict_compare(d1, d2))

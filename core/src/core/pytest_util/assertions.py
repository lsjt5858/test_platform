import pytest

class CustomAssertions:
    @staticmethod
    def assert_status_code(response, expected_code=200):
        assert response.status_code == expected_code, f"Expected {expected_code}, got {response.status_code}"

    @staticmethod
    def assert_json_key(response, key):
        assert key in response.json(), f"Key '{key}' not found in response"

    @staticmethod
    def assert_json_value(response, key, value):
        assert response.json()[key] == value, f"Value '{value}' for key '{key}' not found in response"

    @staticmethod
    def assert_json_values(response, key, values):
        assert response.json()[key] in values, f"Value '{response.json()[key]}' for key '{key}' not found in response"

    @staticmethod
    def assert_json_values_not(response, key, values):
        assert response.json()[key] not in values, f"Value '{response.json()[key]}' for key '{key}' found in response"

    @staticmethod
    def assert_json_value_not(response, key, value):
        assert response.json()[key] != value, f"Value '{value}' for key '{key}' found in response"

    @staticmethod
    def assert_json_value_type(response, key, value_type):
        assert isinstance(response.json()[key], value_type), f"Value '{response.json()[key]}' for key '{key}' is not of type {value_type}"

    @staticmethod
    def assert_json_value_type_not(response, key, value_type):
        assert not isinstance(response.json()[key], value_type), f"Value '{response.json()[key]}' for key '{key}' is of type {value_type}"

    @staticmethod
    def assert_json_value_type_not(response, key, value_type):
        assert not isinstance(response.json()[key], value_type), f"Value '{response.json()[key]}' for key '{key}' is of type {value_type}"
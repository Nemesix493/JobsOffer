from typing import Any, get_args, get_origin
from types import UnionType
from json import loads, JSONDecodeError


class JsonParseMixin:
    @classmethod
    def json_parse(cls, json_text) -> dict | list | None:
        try:
            instance = loads(json_text)
        except JSONDecodeError as e:
            print(f"The send json is not correct\n\"{e}\"")
            return None
        return instance

    @classmethod
    def json_parse_validate(cls, json_text: str, expected_type: Any) -> dict | list | None:
        instance = cls.json_parse(json_text)
        if instance is None:
            return None
        if not cls.validate(instance, expected_type):
            print("The json sent has not the expected type !")
            return None
        return instance

    @classmethod
    def validate(cls, instance: Any, expected_type: Any) -> bool:
        origin = get_origin(expected_type)
        args = get_args(expected_type)

        if origin is None or origin is UnionType:
            return isinstance(instance, expected_type)

        if origin is dict and isinstance(instance, dict):
            key_type, value_type = args
            return all(
                cls.validate(k, key_type) and cls.validate(v, value_type)
                for k, v in instance.items()
            )

        if origin in {list, tuple} and isinstance(instance, origin):
            item_type = args[0]
            return all(cls.validate(item, item_type) for item in instance)
        if origin is set and isinstance(instance, set):
            item_type = args[0]
            return all(cls.validate(item, item_type) for item in instance)

        return False

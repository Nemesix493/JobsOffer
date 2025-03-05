from abc import ABC, ABCMeta, abstractmethod

class ModelMetaClass(ABCMeta):
    _suported_field_type = [
        str,
        int,
        float,
        bool
    ]
    _suported_field_instance_type = []
    @classmethod
    def check_fields(cls, fields: dict):
        for key, val in fields.items():
            if not isinstance(key, str):
                raise TypeError('Field name must be a string')
            if val not in cls._suported_field_type :
                raise TypeError(
                    f"Field type must be in {cls._suported_field_type}"
                )
    
    def __new__(cls, name, bases, class_dict):
        new_class = super().__new__(cls, name, bases, class_dict)
        if hasattr(new_class, 'fields'):
            cls.check_fields(new_class.fields)
        else:
           new_class.fields = {}
        new_class.fields['id'] = int 
        print(f'instaciate {new_class}')
        return new_class
    
    def _get_table_name(self) -> str:
        return ''.join(
            self.__name__[0].lower(),
            *[
                letter if letter.islower() else f'_{letter.lower()}'
                for letter in self.__name__[1:]
            ]
        )
    
    def _get_fields(self) -> dict:
        return self.fields
            

class Model(ABC, metaclass=ModelMetaClass):
    @abstractmethod
    def abs_method(self):
        pass

    


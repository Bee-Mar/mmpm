#!/usr/bin/env python3


class __SingletonMeta(type):
    """
    This metaclass ensures that derived classes only create a single instance.
    The same instance is returned every time the class is instantiated.

    Attributes:
        _instances (dict): A dictionary mapping each class to its created instance.

    Methods:
        __call__(*args, **kwargs): Returns a single instance of the class, creating it if necessary.
    """

    _instances = {}  # type: ignore

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(metaclass=__SingletonMeta):
    """
    Base class for implementing the Singleton design pattern.

    Classes derived from this base class will be Singletons, ensuring only one
    instance of the class is created throughout the program's lifecycle.

    Inherit from this class to create a Singleton.
    """

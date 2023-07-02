#!/usr/bin/env python3
class Singleton:
    _instance = None
    _initialized = False

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self.init()

    def init(self):
        # This method will only be called once during the first instantiation.
        pass

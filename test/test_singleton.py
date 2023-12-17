#!/usr/bin/env python3
import unittest

from mmpm.singleton import Singleton


class SingletonTestCase(unittest.TestCase):
    def test_singleton_instance(self):
        instance_1 = Singleton()
        instance_2 = Singleton()

        self.assertIs(instance_1, instance_2, "Multiple instances of Singleton were created.")


if __name__ == "__main__":
    unittest.main()

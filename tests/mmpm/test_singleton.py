#!/usr/bin/env python3
import random

class SingletonTestCase(unittest.TestCase):
    def test_singleton_instance(self):
        class MySingleton(Singleton):
            def __init__(self, value):
                super().__init__()
                self.value = value

        # Generate randomized values
        value1 = random.randint(0, 100)
        value2 = random.randint(0, 100)

        # Create instances of the singleton class with randomized values
        instance1 = MySingleton(value1)
        instance2 = MySingleton(value2)

        # Both instances should be the same object
        self.assertIs(instance1, instance2)

        # The value should be consistent across instances
        self.assertEqual(instance1.value, instance2.value)
        self.assertEqual(instance1.value, value2)

        # Modifying the value in one instance should reflect in the other instance
        instance1.value = random.randint(0, 100)
        self.assertEqual(instance2.value, instance1.value)


if __name__ == '__main__':
    unittest.main()

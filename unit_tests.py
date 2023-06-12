import unittest
from datetime import datetime
from RattleCache import Cache, cached, cached_args, cached_dependency


class CacheModuleTest(unittest.TestCase):

    def setUp(self):
        # initialize cache with 10 mb storage
        self.cache = Cache(memory_limit=10)

    def test_add_and_get(self):
        # Test adding a key-value pair to the cache and retrieving the value
        self.cache.add("key1", "value1")
        self.assertEqual(self.cache.get("key1"), "value1")

    def test_add_with_memory_limit(self):
        # Test adding a key-value pair to the cache with serialization and retrieving the value
        self.cache.add("key1", "value1", serialize=True)
        self.assertEqual(self.cache.get("key1"), "value1")

    def test_update(self):
        # Test updating the value of a key in the cache
        self.cache.add("key1", "value1")
        self.cache.update("key1", "updated_value")
        self.assertEqual(self.cache.get("key1"), "updated_value")

    def test_delete(self):
        # Test deleting a key-value pair from the cache
        self.cache.add("key1", "value1")
        self.cache.delete("key1")
        self.assertIsNone(self.cache.get("key1"))

    def test_clear_cache(self):
        # Test clearing the cache
        self.cache.add("key1", "value1")
        self.cache.clear_cache()
        self.assertIsNone(self.cache.get("key1"))

    def test_identifiers(self):
        # Test retrieving the list of cache identifiers
        self.cache.add("key1", "value1")
        self.cache.add("key2", "value2")
        self.assertEqual(self.cache.identifiers(), ["key1", "key2"])

    def test_cached_decorator(self):
        # Test the `cached` decorator with a function that has no arguments
        @cached(self.cache, "func1")
        def func1():
            return datetime.now()

        result1 = func1()
        result2 = func1()
        # Check that the cached values are the same
        self.assertEqual(result1, result2)

    def test_cached_args_decorator(self):
        # Test the `cached_args` decorator with a function that has multiple arguments
        @cached_args(self.cache)
        def func2(a, b, c):
            return a + b + c

        result1 = func2(1, 2, 3)
        result2 = func2(1, 2, 3)
        # Check that the cached values are the same
        self.assertEqual(result1, result2)

        result3 = func2(4, 5, 6)
        # Check that the cached values are different for different arguments
        self.assertNotEqual(result1, result3)

    def test_cached_dependency_decorator(self):
        # Test the `cached_dependency` decorator with a function that has a dependency function
        def dependency_func(a, b):
            return a + b

        @cached_dependency(self.cache, dependency_func)
        def func3(a, b):
            return a * b

        result1 = func3(2, 3)
        result2 = func3(2, 3)
        # Check that the cached values are the same
        self.assertEqual(result1, result2)

        result3 = func3(4, 5)
        # Check that the cached values are different for different arguments
        self.assertNotEqual(result1, result3)

    def test_cached_decorator_with_multiple_args(self):
        # Test the `cached` decorator with a function that has multiple arguments
        @cached(self.cache, "func4")
        def func4(a, arr):
            return a * sum(arr)

        arr_1 = [1, 2, 3, 4]
        arr_2 = [1000, 20000]

        result_1 = func4(2, arr_1)
        result_2 = func4(2, arr_1)
        # Check that the cached values are the same
        self.assertEqual(result_1, result_2)

        result_1 = func4(2, arr_1)
        result_2 = func4(2, arr_2)
        # Check that the cached values are the same
        self.assertEqual(result_1, result_2)

        result_3 = func4(2, arr_2, update_cache=True)
        # Check that the cached values are different for different arguments
        self.assertNotEqual(result_1, result_3)

    def test_cached_decorator_checked_update(self):
        # Test the `cached` decorator with the `checked_update` parameter set to `True` for a function
        @cached(self.cache, "func5")
        def func5(a, b):
            return a * b

        result1 = func5(2, 3)
        result2 = func5(200000, 3)
        # Check that the cached values are the same
        self.assertEqual(result1, result2)

        result3 = func5(200000, 3, update_cache=True)
        # Check that the cached values are different for same arguments after update
        self.assertNotEqual(result2, result3)


if __name__ == '__main__':
    unittest.main()

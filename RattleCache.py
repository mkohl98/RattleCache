"""
RattleCache by Marcel Kohl: https://github.com/mkohl98


The module provides a Cache class that allows you to create cache instances with different eviction modes such as LRU
(Least Recently Used), LRA (Least Recently Added), and LFU (Least Frequently Used). It supports features like setting a
memory limit for the cache, serialization of data, and efficient eviction of entries when the memory limit is reached.

The Cache class provides methods for adding, retrieving, updating, and deleting entries from the cache. It also allows
you to get an overview of all identifiers in the cache and their corresponding data size. Additionally, you can
calculate the memory usage and usage percentage of the cache.

The module includes two decorator functions: cache_result and cache_with_dependency. These decorators can be used to
cache the results of function or method calls using the Cache instance. The cache_result decorator caches the result
based on a unique identifier, while the cache_with_dependency decorator caches the result based on a
specific dependency value.
"""


### Dependencies

from collections import OrderedDict, defaultdict
import pickle
import sys
import functools
import heapq


### Constants

MAX_SHARED_CACHE_MEMORY: int = None
"""int, Constant to set if you want to set a maximum shared memory [megabyte] of all Cache class instances."""


### Main Class

class Cache:
    """
    Cache class that allows you to create cache instances with different eviction modes such as LRU
    (Least Recently Used), LRA (Least Recently Added), and LFU (Least Frequently Used). It supports features like
    setting a memory limit for the cache, serialization of data, and efficient eviction of entries when the memory
    limit is reached.

    Attributes (read-only after instance construction):
        memory_limit (int): The memory limit in megabytes for the cache instance.
        mode (str): The eviction mode for the cache (LRU, LRA, or LFU).
        eviction_percentage (float): The eviction percentage to determine when to start evicting entries.
        serialize_limit: The limit in megabytes for automatically serializing large data entries.

    Methods:
        has(identifier: str) -> bool:
            Checks if an identifier exists in the cache.

        add(identifier: str, data, serialize: bool = False):
            Adds an entry to the cache.

        get(identifier: str):
            Retrieves an entry from the cache.

        update(identifier: str, data, serialize: bool = False):
            Updates data in cache, cached by identifier.

        delete(identifier: str):
            Deletes an entry from the cache.

        clear_cache():
            Clears the cache.

        get_overview() -> str:
            Returns an overview of all identifiers and their data size.

        get_memory_usage() -> float:
            Returns the used cache memory in megabytes.

        get_memory_usage_percentage() -> float:
            Returns the currently used memory in percentage.

        identifiers() -> list:
            Returns a list with all identifiers.
    """

    # class variables
    __max_shared_memory_limit = MAX_SHARED_CACHE_MEMORY   # retrieve constant
    __shared_caches = []   # store references to all cache instances

    def __init__(self,
                 memory_limit: int,
                 mode: str = "LRU",
                 eviction_percentage: float = 0.9,
                 serialize_limit=None,
                 ):

        if mode not in ("LRU", "LRA", "LFU"):
            raise AttributeError(f"'{mode}' is not a valid eviction mode")

        self.__memory_limit = memory_limit
        self.__mode = mode
        self.__eviction_percentage = eviction_percentage
        self.__serialize_limit = serialize_limit
        self.__cache = OrderedDict()

        # LFU mode only data
        if self.__mode == "LFU":
            self.__frequency = defaultdict(int)  # Track the frequency of cache entries
            self.__frequency_heap = []  # Heap to keep track of entries based on their frequency

        # show that you exceed max_memory_shared
        self.__shared_caches.append(self)
        if self.__max_shared_memory_limit is not None:
            if type(self.__max_shared_memory_limit) != int:
                raise TypeError("MAX_SHARED_CACHE_MEMORY has to be either None or int.")
            check_sum = 0
            for cache in self.__shared_caches:
                check_sum += cache.memory_limit
            if check_sum > self.__max_shared_memory_limit:
                print("\x1b[31;20mCacheWarning: "
                      "Most recent initialized instance of Cache class exceeds your set MAX_SHARED_CACHE_MEMORY.\n"
                      "This Cache instance will be deleted. "
                      "Check all your instances or adjust MAX_SHARED_CACHE_MEMORY only once at the "
                      "start of your application.\x1b[0m"
                      )
                del self

    # attributes and properties
    @property
    def memory_limit(self) -> int:
        return self.__memory_limit

    @property
    def mode(self) -> str:
        return self.__mode

    @property
    def eviction_percentage(self) -> float:
        return self.__eviction_percentage

    @property
    def serialize_limit(self):
        return self.__serialize_limit

    # private methods
    def __getitem__(self, identifier: str):
        return self.get(identifier)

    def __setitem__(self, identifier: str, data):
        # this does not update!!!
        self.add(identifier, data)

    @staticmethod
    def __serialize_data(data):
        """ Serializes data using pickle """
        return pickle.dumps(data)

    @staticmethod
    def __deserialize_data(serialized_data):
        """  Deserializes data using pickle. """
        return pickle.loads(serialized_data)

    def __evict_entry(self):
        """  Evicts the least recently used entry from the cache. """
        if self.__mode == "LRA":
            key = self.__get_least_key()
            del self.__cache[key]
        elif self.__mode == "LRU":
            key = self.__get_least_key()
            del self.__cache[key]
        elif self.__mode == "LFU":
            # Evict the least frequently used entry
            while self.__frequency_heap:
                frequency, key = heapq.heappop(self.__frequency_heap)
                if key in self.__cache:
                    del self.__cache[key]
                    break

    def __get_least_key(self) -> str:
        """ Returns the least recently used key in the cache without need to create iter but just view. """
        return next(iter(self.__cache))

    @staticmethod
    def __get_data_size(data) -> float:
        """ Returns the current size of data in megabytes. """
        return sys.getsizeof(data) / (1024 * 1024)

    def __update_frequency(self, identifier):
        """ Increase frequency of item by identifier"""
        if self.__mode == "LFU":
            self.__frequency[identifier] += 1

    # public methods
    def has(self, identifier: str) -> bool:
        """ Checks if an identifier exists in the cache. """
        return identifier in self.__cache

    def add(self, identifier: str, data, serialize: bool = False):
        """
        Adds an entry to the cache.
        Bracket notation is also available: **my_cache_instance[identifier] = data** (This uses serialization only if
        serialization_limit is set.)
        """
        # eviction if needed
        if self.__memory_limit is not None:
            data_size = self.__get_data_size(data)
            while (sys.getsizeof(self.__cache) + data_size) > self.__memory_limit:
                self.__evict_entry()
        # serialization
        if self.__serialize_limit is not None and self.__get_data_size(data) > self.__serialize_limit:
            serialize = True
        if serialize:
            data = self.__serialize_data(data)
        # mode specifics
        if self.__mode == "LFU":
            self.__update_frequency(identifier)
        # set data
        self.__cache[identifier] = data

    def get(self, identifier: str):
        """
        Retrieves an entry from the cache.
        Bracket notation is also available: **data = my_cache_instance[identifier]**.
        """
        if identifier not in self.__cache:
            return None
        data = self.__cache[identifier]
        if isinstance(data, bytes):
            return pickle.loads(data)

        # eviction mode
        if self.__mode == "LRU":
            self.__cache.move_to_end(identifier)
        if self.__mode == "LFU":
            self.__update_frequency(identifier)

        return data

    def update(self, identifier: str, data, serialize: bool = False):
        """ Update data in cache, cached by identifier. """
        self.delete(identifier)
        self.add(identifier, data, serialize=serialize)

    def delete(self, identifier: str):
        """ Deletes an entry from the cache. """
        if identifier in self.__cache:
            del self.__cache[identifier]

    def clear_cache(self) -> None:
        """ Clears cache. """
        self.__cache = OrderedDict()
        if self.__mode == "LFU":
            self.__frequency = defaultdict(int)
            self.__frequency_heap = []

    def get_overview(self) -> None:
        """ Prints an overview of all identifiers and their data size. """
        overview = [
            "Cache Overview",
            f"Memory Limit: {self.__memory_limit} mb",
            f"Memory used: {self.get_memory_usage()} mb",
            f"Eviction Mode: {self.__mode}\n",
            "Identifier\tData Type\tMemory (MB)"
        ]

        # sort data increasingly by memory space occupied
        sorted_entries = sorted(
            self.__cache.items(),
            key=lambda entry: self.__get_data_size(entry[1]),
            reverse=True
        )

        for identifier, data in sorted_entries:
            data_type = type(data).__name__
            data_size = self.__get_data_size(data)
            overview.append(f"{identifier}\t{data_type}\t{data_size:.2f}")

        print("\n".join(overview))

    def get_memory_usage(self) -> float:
        """ Returns the used cache memory in mb. """
        total_size = sum(sys.getsizeof(value) for value in self.__cache.values())
        return total_size / (1024 * 1024)  # Convert to megabytes

    def get_memory_usage_percentage(self) -> float:
        """ Returns the currently used memory in percent. """
        if self.__memory_limit > 0:
            used_memory = self.get_memory_usage()
            return (used_memory / self.__memory_limit) * 100
        else:
            return 0.0

    def identifiers(self) -> list:
        """ Returns a list with all identifiers. """
        return list(self.__cache.keys())


### Decorator Functions

def cache_result(cache: Cache, identifier: str, *args_cache, **kwargs_cache):
    """
    Decorator that caches the result of a function or method call using the provided cache.

    Args:
        cache (Cache): An instance of the Cache class to store the cached results.
        identifier (str): The unique identifier for the cached result.
        *args_cache: Additional arguments to pass to the cache's add method.
        **kwargs_cache: Additional keyword arguments to pass to the cache's add method.

    Returns:
        The decorator function.
    """
    if not isinstance(cache, Cache):
        raise ValueError("The 'cache' argument must be an instance of the Cache class.")

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if cache.has(identifier):
                return cache.get(identifier)
            result = func(*args, **kwargs)
            cache.add(identifier, result, *args_cache, **kwargs_cache)
            return result
        return wrapper
    return decorator


def cache_with_dependency(cache: Cache, dependency_func, *args_cache, **kwargs_cache):
    """
    Decorator that caches the result of a function or method call based on a specific dependency value.

    Args:
        cache (Cache): An instance of the Cache class to store the cached results.
        dependency_func (callable): A function that calculates the dependency value.
        *args_cache: Additional arguments to pass to the cache's add method.
        **kwargs_cache: Additional keyword arguments to pass to the cache's add method.

    Returns:
        The decorator function.
    """
    if not isinstance(cache, Cache):
        raise ValueError("The 'cache' argument must be an instance of the Cache class.")

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            dependency_value = dependency_func(*args, **kwargs)
            identifier = f"{func.__name__}:{dependency_value}"
            if cache.has(identifier):
                return cache.get(identifier)
            result = func(*args, **kwargs)
            cache.add(identifier, result, *args_cache, **kwargs_cache)
            return result
        return wrapper
    return decorator


if __name__ == "__main__":
    # Testing Area
    ...

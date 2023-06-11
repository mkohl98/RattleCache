# RattleCache

## Overview
RattleCache is a Python module that provides a Cache class for creating cache instances with different eviction modes such as LRU (Least Recently Used), LRA (Least Recently Added), and LFU (Least Frequently Used). It supports features like setting a memory limit for the cache, serialization of data, and efficient eviction of entries when the memory limit is reached.

## Features
- Create cache instances with different eviction modes: LRU, LRA, and LFU.
- Set a memory limit for the cache.
- Serialize large data entries automatically.
- Efficient eviction of entries when the memory limit is reached.
- Add, retrieve, update, and delete entries from the cache.
- Get an overview of all identifiers in the cache and their corresponding data size.
- Calculate the memory usage and usage percentage of the cache.

## WIP
- Create argument-bound identifiers for caching using decorators
- Create a more simple way to update cached data when using decorators

## Dependencies

All dependencies are inbuild Python modules, icluding following:

- **collections.OrderedDict**: Used for maintaining the cache entries in insertion order.
- **collections.defaultdict**: Used for tracking the frequency of cache entries in LFU mode.
- **pickle**: Used for serialization and deserialization of data.
- **sys**: Used for getting the size of data.
- **functools**: Used for creating decorator functions.
- **heapq**: Used for maintaining a heap of entries based on their frequency in LFU mode.

## Installation

To use RattleCache, you can clone the repository from GitHub:

bash:
`git clone https://github.com/mkohl98/RattleCache.git`

## Usage
### Cache Class

The Cache class is the main component of RattleCache. Here's an basic overview of its attributes and methods for manual caching:

Python:
```python
from RattleCache import Cache

# Create a cache instance
cache = Cache(memory_limit=1024, mode="LRU")

# Add an entry to the cache
small_data_1 = [_ for _ in range(10)]
small_data_2 = [_ for _ in range(10, 20)]

cache.add("small_data_1", small_data_1)
cache["small_data_2"] = small_data_2

# Retrieve an entry from the cache
data_1 = cache.get("small_data_1")
data_2 = cache["small_data_2"]

# Update an entry in the cache
small_data_1_reprocessed = list(range(10))
cache.update("small_data_1", small_data_1_reprocessed)

# Delete an entry from the cache
cache.delete("small_data_1")

# Clear the cache
cache.clear_cache()

# Get an overview of all identifiers and their data size
overview = cache.get_overview()

# Get the used cache memory in megabytes
memory_usage = cache.get_memory_usage()

# Get the currently used memory as a percentage
memory_usage_percentage = cache.get_memory_usage_percentage()

# Get a list of all identifiers in the cache
identifiers = cache.identifiers()
```

### Eviction Modes

The cache instance can be configured with different eviction modes. These are fixed and can not be modified once the Cache instance is created:
- LRU (Least Recently Used): Evicts the least recently used entry when the memory limit is reached.
- LRA (Least Recently Added): Evicts the least recently added entry when the memory limit is reached.
- LFU (Least Frequently Used): Evicts the least frequently used entry when the memory limit is reached.

Python:
```python
# Create a cache instance with LRU eviction mode
cache_lru = Cache(memory_limit=1024, mode="LRU")

# Create a cache instance with LRA eviction mode
cache_lra = Cache(memory_limit=1024, mode="LRA")

# Create a cache instance with LFU eviction mode
cache_lfu = Cache(memory_limit=1024, mode="LFU")
```

### Serialization

RattleCache supports automatic serialization of large data entries. You can set a serialize limit to specify the threshold size for serialization. By default, serialization is disabled. Deserialization is handled automatically.

Python:
```python
# Create a cache instance with serialization enabled
cache = Cache(memory_limit= 4096, serialize_limit=200)

# Add a large data entry that exceeds the serialize limit
large_data_1 = function_that_returns_large_data()  # This entry exceeds the serialize limit

cache.add("large_data_1", large_data_1)

# Retrieve the large data entry from the cache, it will be deserialized automatically
retrieved_data = cache.get("large_data_1")
```

### Decorators

RattleCache provides decorators for easily caching the return values of functions and methods. The decorators handle the caching automatically and transparently and are the simple go-to method to use in big projects.

Python:
```python
from RattleCache import Cache, cache_result

# Create a cache instance with 4 GB and LRU mode
cache = Cache(memory_limit=4096, mode="LRU")

# Apply the cache_function decorator to a function
@cache_result(cache, "function_cache_key")
def expensive_function(arg1, arg2):
    # Perform expensive computation
    return result

# Apply the cache_method decorator to a class method
class MyClass:
    @cache_result(cache, "method_cache_key")
    def expensive_method(self, arg1, arg2):
        # Perform expensive computation
        return result

# The return values of the decorated function and method will be cached based on the provided cache key
expensive_result = expensive_function(arg1, arg2)

# Since the function is called once, its result is cached and will be accessed if the function is called again
cached_expensive_result = cache.get("function_cache_key")
```

## License
This project underlies MIT-License.
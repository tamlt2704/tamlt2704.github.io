# Chapter 10: The Import System

[← Chapter 9: Closures](chapter-09-closures.md) | [Chapter 11: AST Manipulation →](chapter-11-ast.md)

---

## The Problem

FrameForge has a plugin system. Users drop Python files into a `plugins/` directory, and the framework should auto-discover and register them:

```
plugins/
├── json_handler.py      # class JsonHandler(BasePlugin): ...
├── xml_handler.py       # class XmlHandler(BasePlugin): ...
├── csv_handler.py       # class CsvHandler(BasePlugin): ...
└── custom_handler.py    # class CustomHandler(BasePlugin): ...
```

The naive approach: manually import each one.

```python
# Hardcoded imports — breaks when users add new plugins
from plugins.json_handler import JsonHandler
from plugins.xml_handler import XmlHandler
from plugins.csv_handler import CsvHandler
from plugins.custom_handler import CustomHandler

PLUGINS = [JsonHandler, XmlHandler, CsvHandler, CustomHandler]
```

Every new plugin requires editing this file. Users can't add plugins without modifying framework code.

Vera: "The framework should scan the directory and load everything automatically. Zero configuration."

## How Python Imports Work

When you write `import foo`, Python:

1. Checks `sys.modules` (cache) — if already imported, returns cached module
2. Finds the module using **finders** in `sys.meta_path`
3. Loads the module using the finder's **loader**
4. Executes the module code
5. Stores in `sys.modules`

```python
import sys

# The module cache:
print(len(sys.modules))  # Hundreds of already-imported modules

# The finders (in order):
print(sys.meta_path)
# [<BuiltinImporter>, <FrozenImporter>, <PathFinder>]

# The search paths:
print(sys.path)
# ['', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', ...]
```

## Solution: Plugin Auto-Discovery

```python
import importlib
import pkgutil
import inspect
from pathlib import Path

class BasePlugin:
    """All plugins must inherit from this."""
    name = None

    def execute(self, data):
        raise NotImplementedError

def discover_plugins(package_path, base_class=BasePlugin):
    """Auto-discover all plugin classes in a package directory."""
    plugins = {}

    # Find all Python modules in the directory
    package_dir = Path(package_path)
    for finder, module_name, is_pkg in pkgutil.iter_modules([str(package_dir)]):
        # Import the module
        spec = importlib.util.spec_from_file_location(
            module_name,
            package_dir / f"{module_name}.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find all classes that inherit from base_class
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, base_class) and obj is not base_class:
                plugin_name = getattr(obj, 'name', None) or name
                plugins[plugin_name] = obj

    return plugins

# Usage:
plugins = discover_plugins("./plugins")
print(plugins)
# {'JsonHandler': <class 'JsonHandler'>, 'XmlHandler': <class 'XmlHandler'>, ...}

# Instantiate and use:
handler = plugins["JsonHandler"]()
handler.execute(data)
```

Drop a new `.py` file in `plugins/`, restart the app — it's automatically discovered.

## importlib: Programmatic Imports

```python
import importlib

# Import a module by name (string):
json_module = importlib.import_module("json")
json_module.dumps({"key": "value"})

# Import from a package:
handler = importlib.import_module("plugins.json_handler")

# Reload a module (useful for development):
importlib.reload(json_module)

# Import with a dynamic name:
module_name = "csv"  # Could come from config
mod = importlib.import_module(module_name)
```

## Lazy Imports

Some modules are expensive to import (numpy, pandas, tensorflow). Load them only when first used:

```python
import importlib
import sys

class LazyModule:
    """Import a module only when an attribute is first accessed."""

    def __init__(self, module_name):
        self._module_name = module_name
        self._module = None

    def _load(self):
        if self._module is None:
            self._module = importlib.import_module(self._module_name)
        return self._module

    def __getattr__(self, name):
        return getattr(self._load(), name)

# Usage:
np = LazyModule("numpy")       # No import happens yet
pd = LazyModule("pandas")      # No import happens yet

# Only imports when first used:
array = np.array([1, 2, 3])   # NOW numpy is imported
```

A simpler approach for Python 3.7+:

```python
def __getattr__(name):
    """Module-level __getattr__ for lazy imports."""
    if name == "numpy":
        import numpy
        globals()["numpy"] = numpy
        return numpy
    if name == "pandas":
        import pandas
        globals()["pandas"] = pandas
        return pandas
    raise AttributeError(f"module has no attribute {name}")
```

## Custom Import Hooks: sys.meta_path

For advanced cases, you can add custom finders to `sys.meta_path`:

```python
import sys
import importlib.abc
import importlib.machinery

class PluginFinder(importlib.abc.MetaPathFinder):
    """Custom finder that loads plugins from a registry."""

    def __init__(self, plugin_dir):
        self.plugin_dir = Path(plugin_dir)

    def find_spec(self, fullname, path, target=None):
        """Called by Python's import system to find a module."""
        if fullname.startswith("frameforge_plugins."):
            plugin_name = fullname.split(".")[-1]
            plugin_path = self.plugin_dir / f"{plugin_name}.py"
            if plugin_path.exists():
                return importlib.util.spec_from_file_location(
                    fullname, plugin_path
                )
        return None  # Not our responsibility

# Install the finder:
sys.meta_path.append(PluginFinder("./plugins"))

# Now this works even though 'frameforge_plugins' isn't a real package:
import frameforge_plugins.json_handler  # Loads from ./plugins/json_handler.py
```

## A Complete Plugin System

```python
import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Dict, Type

class PluginRegistry:
    """Auto-discovering plugin registry for FrameForge."""

    def __init__(self):
        self._plugins: Dict[str, Type] = {}
        self._loaded_modules = set()

    def discover(self, package_path: str, base_class: type = None):
        """Scan a directory for plugin classes."""
        package_dir = Path(package_path)
        if not package_dir.exists():
            return

        for finder, module_name, is_pkg in pkgutil.iter_modules([str(package_dir)]):
            if module_name.startswith('_'):
                continue  # Skip private modules

            try:
                spec = importlib.util.spec_from_file_location(
                    module_name,
                    package_dir / f"{module_name}.py"
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self._loaded_modules.add(module_name)

                # Register all qualifying classes
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if base_class and not issubclass(obj, base_class):
                        continue
                    if obj is base_class:
                        continue
                    if obj.__module__ != module.__name__:
                        continue  # Skip imported classes

                    key = getattr(obj, 'plugin_name', name)
                    self._plugins[key] = obj

            except Exception as e:
                print(f"Warning: Failed to load plugin {module_name}: {e}")

    def get(self, name: str):
        """Get a plugin class by name."""
        if name not in self._plugins:
            raise KeyError(f"Unknown plugin: {name}. Available: {list(self._plugins.keys())}")
        return self._plugins[name]

    def create(self, name: str, *args, **kwargs):
        """Instantiate a plugin by name."""
        cls = self.get(name)
        return cls(*args, **kwargs)

    def list_plugins(self):
        """List all registered plugins."""
        return list(self._plugins.keys())

    def __contains__(self, name):
        return name in self._plugins

    def __iter__(self):
        return iter(self._plugins.items())


# Usage:
registry = PluginRegistry()
registry.discover("./plugins", base_class=BasePlugin)

print(registry.list_plugins())
# ['JsonHandler', 'XmlHandler', 'CsvHandler']

handler = registry.create("JsonHandler")
result = handler.execute(raw_data)
```

## Entry Points: The Standard Plugin Mechanism

For distributed plugins (installed via pip), use entry points:

```python
# In plugin's setup.py or pyproject.toml:
# [project.entry-points."frameforge.plugins"]
# json = "my_plugin.handlers:JsonHandler"

# In the framework:
from importlib.metadata import entry_points

def load_installed_plugins():
    """Load plugins installed as packages."""
    plugins = {}
    eps = entry_points(group="frameforge.plugins")
    for ep in eps:
        plugins[ep.name] = ep.load()  # Imports and returns the object
    return plugins
```

## Conditional and Deferred Imports

```python
# Conditional import — handle optional dependencies:
try:
    import ujson as json  # Fast JSON if available
except ImportError:
    import json  # Fall back to stdlib

# Deferred import — avoid circular imports:
def get_user_model():
    from myapp.models import User  # Import inside function
    return User

# Import guard — only import in type checking:
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from heavy_module import HeavyClass  # Only for type checkers, not runtime
```

## What You Learned

- **`importlib.import_module()`** imports modules by string name
- **`pkgutil.iter_modules()`** discovers all modules in a directory
- **`sys.meta_path`** contains finders that control how imports work
- **Custom finders** let you load modules from anywhere (databases, URLs, registries)
- **Lazy imports** defer expensive module loading until first use
- **Entry points** are the standard mechanism for distributed plugins
- **`inspect.getmembers()`** finds classes/functions in a loaded module
- **Module-level `__getattr__`** (Python 3.7+) enables lazy attribute access on modules

## Key Insight

> The import system lets you discover and load code dynamically. But what if you need to *generate* code? Not load existing files — create new Python code from a schema, a config, or another language? That's AST manipulation.

---

[Chapter 11: AST Manipulation →](chapter-11-ast.md)

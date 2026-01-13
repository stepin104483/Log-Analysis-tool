"""
Module Registry for Auto-Discovery

Handles automatic discovery and registration of analysis modules.
Modules are discovered from the 'modules/' directory.
"""

import os
import importlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Type

from .base_analyzer import BaseAnalyzer
from .placeholder_analyzer import PlaceholderAnalyzer

logger = logging.getLogger(__name__)

# Base classes that should not be instantiated directly
_ABSTRACT_ANALYZERS = {BaseAnalyzer, PlaceholderAnalyzer}


class ModuleRegistry:
    """
    Central registry for all analysis modules.

    Provides auto-discovery of modules from the modules/ directory
    and maintains a registry of available analyzers.
    """

    _instance = None
    _modules: Dict[str, BaseAnalyzer] = {}
    _initialized = False

    def __new__(cls):
        """Singleton pattern - only one registry instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> 'ModuleRegistry':
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def discover_modules(cls, modules_path: str = None) -> None:
        """
        Discover and register all modules from the modules directory.

        Args:
            modules_path: Path to modules directory (optional)
        """
        if cls._initialized:
            return

        if modules_path is None:
            # Default to modules/ directory relative to this file
            base_dir = Path(__file__).parent.parent
            modules_path = base_dir / 'modules'

        modules_path = Path(modules_path)

        if not modules_path.exists():
            logger.warning(f"Modules directory not found: {modules_path}")
            return

        logger.info(f"Discovering modules from: {modules_path}")

        for module_dir in sorted(modules_path.iterdir()):
            if module_dir.is_dir() and not module_dir.name.startswith('_'):
                cls._load_module(module_dir)

        cls._initialized = True
        logger.info(f"Discovered {len(cls._modules)} modules: {list(cls._modules.keys())}")

    @classmethod
    def _load_module(cls, module_dir: Path) -> None:
        """
        Load a single module from its directory.

        Args:
            module_dir: Path to the module directory
        """
        module_name = module_dir.name
        init_file = module_dir / '__init__.py'
        analyzer_file = module_dir / 'analyzer.py'

        if not init_file.exists():
            logger.debug(f"Skipping {module_name}: no __init__.py")
            return

        try:
            # Import the module
            module_import_path = f"modules.{module_name}"

            # Check if analyzer.py exists
            if analyzer_file.exists():
                analyzer_import_path = f"modules.{module_name}.analyzer"
                analyzer_module = importlib.import_module(analyzer_import_path)

                # Find the analyzer class (subclass of BaseAnalyzer, excluding abstract bases)
                analyzer_class = None
                for attr_name in dir(analyzer_module):
                    attr = getattr(analyzer_module, attr_name)
                    if (isinstance(attr, type) and
                        issubclass(attr, BaseAnalyzer) and
                        attr not in _ABSTRACT_ANALYZERS):
                        analyzer_class = attr
                        break

                if analyzer_class:
                    # Instantiate and register
                    analyzer_instance = analyzer_class()
                    cls._modules[analyzer_instance.module_id] = analyzer_instance
                    logger.info(f"Registered module: {analyzer_instance.module_id} "
                               f"({analyzer_instance.display_name})")
                else:
                    logger.warning(f"No BaseAnalyzer subclass found in {module_name}")
            else:
                # Try loading from __init__.py
                init_module = importlib.import_module(module_import_path)

                if hasattr(init_module, 'get_analyzer'):
                    analyzer_instance = init_module.get_analyzer()
                    cls._modules[analyzer_instance.module_id] = analyzer_instance
                    logger.info(f"Registered module: {analyzer_instance.module_id}")

        except Exception as e:
            logger.error(f"Failed to load module {module_name}: {e}")

    @classmethod
    def register(cls, analyzer: BaseAnalyzer) -> None:
        """
        Manually register an analyzer.

        Args:
            analyzer: The analyzer instance to register
        """
        cls._modules[analyzer.module_id] = analyzer
        logger.info(f"Manually registered module: {analyzer.module_id}")

    @classmethod
    def get_module(cls, module_id: str) -> Optional[BaseAnalyzer]:
        """
        Get a module by its ID.

        Args:
            module_id: The module identifier

        Returns:
            The analyzer instance or None if not found
        """
        return cls._modules.get(module_id)

    @classmethod
    def get_all_modules(cls) -> Dict[str, BaseAnalyzer]:
        """
        Get all registered modules.

        Returns:
            Dictionary of module_id -> analyzer instance
        """
        return cls._modules.copy()

    @classmethod
    def get_active_modules(cls) -> Dict[str, BaseAnalyzer]:
        """
        Get only active (non-coming-soon) modules.

        Returns:
            Dictionary of active module_id -> analyzer instance
        """
        return {
            k: v for k, v in cls._modules.items()
            if v.status == 'active'
        }

    @classmethod
    def get_module_list(cls) -> List[Dict]:
        """
        Get list of all modules with their info.

        Returns:
            List of module info dictionaries
        """
        return [
            analyzer.get_module_info()
            for analyzer in cls._modules.values()
        ]

    @classmethod
    def clear(cls) -> None:
        """Clear all registered modules (useful for testing)."""
        cls._modules.clear()
        cls._initialized = False

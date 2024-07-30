# custom_exceptions.py

class CoreSystemError(Exception):
    """Exception raised for errors in the Core System."""
    pass

class DependencyInjectionError(Exception):
    """Exception raised for errors in the Dependency Injection Layer."""
    pass

class PluginManagementError(Exception):
    """Exception raised for errors in the Plugin Management Layer."""
    pass

class PluginLoaderError(Exception):
    """Exception raised for errors in the Plugin Loader."""
    pass

class PluginRegistryError(Exception):
    """Exception raised for errors in the Plugin Registry."""
    pass

from importlib.metadata import PackageNotFoundError, version

from .modules import (
    INKS,
    FONTS,
    PAPERS,
    LAYOUTS,
    Layout,
    Assignment,
    AssignmentResult,
    AssignmentConfigOptions,
    available_fonts,
    available_papers,
)

try:
    __version__ = version("assignmentwriter")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = [
    "INKS",
    "FONTS",
    "PAPERS",
    "LAYOUTS",
    "Layout",
    "Assignment",
    "AssignmentResult",
    "AssignmentConfigOptions",
    "available_fonts",
    "available_papers",
    "__version__",
]

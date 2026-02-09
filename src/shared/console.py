"""Console output utilities for safe printing across platforms.

This module provides utilities for printing to console that handle
encoding issues on Windows and other platforms.
"""


def safe_print(*args, **kwargs):
    """Print to console with fallback for encoding issues.

    This function attempts to print normally, but falls back to ASCII
    if the console doesn't support UTF-8 characters (common on Windows).

    Args:
        *args: Positional arguments to print
        **kwargs: Keyword arguments for print()
    """
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Fallback: remove problematic characters
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                # Replace common emojis with text equivalents
                safe_arg = (
                    arg.replace("🎯", "[PLANNER]")
                    .replace("✍️", "[WRITER]")
                    .replace("🔍", "[CRITIQUE]")
                    .replace("📋", "[INFO]")
                    .replace("📄", "[DOCUMENT]")
                    .replace("📊", "[RESULTS]")
                    .replace("✅", "[APPROVED]")
                    .replace("❌", "[REJECTED]")
                    .replace("🚀", "[START]")
                    .replace("🏁", "[COMPLETE]")
                    .replace("⚠️", "[WARNING]")
                    .replace("🔄", "[REWRITE]")
                    .replace("✓", "[OK]")
                    .replace("💰", "[$]")
                )
                # Remove any remaining non-ASCII characters
                safe_arg = safe_arg.encode("ascii", errors="ignore").decode("ascii")
                safe_args.append(safe_arg)
            else:
                safe_args.append(str(arg))

        print(*safe_args, **kwargs)


def print_separator(char="=", width=80):
    """Print a separator line.

    Args:
        char: Character to use for the separator
        width: Width of the separator line
    """
    safe_print(char * width)


def print_header(text: str, width: int = 80):
    """Print a formatted header.

    Args:
        text: Header text
        width: Width of the header
    """
    print_separator("#", width)
    safe_print(text)
    print_separator("#", width)


def print_section(text: str, width: int = 80):
    """Print a formatted section header.

    Args:
        text: Section text
        width: Width of the section
    """
    print_separator("=", width)
    safe_print(text)
    print_separator("=", width)


def print_subsection(text: str, width: int = 80):
    """Print a formatted subsection.

    Args:
        text: Subsection text
        width: Width of the subsection
    """
    print_separator("-", width)
    safe_print(text)
    print_separator("-", width)

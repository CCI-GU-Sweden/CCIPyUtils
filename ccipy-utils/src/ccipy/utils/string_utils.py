import string

def format_by_order(fmt: str, values):
    """
    Fills a Python format string using values in order,
    ignoring the placeholder names (e.g. {x}, {y}, etc.).
    
    Example:
        format_by_order("Hello {name}, you have {count} messages", ["Alice", 5])
        → "Hello Alice, you have 5 messages"
    """
    # Extract field names in order of appearance
    keys = [f for _, f, _, _ in string.Formatter().parse(fmt) if f]

    # Build a mapping from keys → provided values
    data = dict(zip(keys, values))

    # Fill the template
    return fmt.format_map(data)

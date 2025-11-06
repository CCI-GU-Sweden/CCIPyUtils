from ccipy.utils import string_utils

def test_format_by_order():
    fmt = "Hello {name}, you have {count} messages"
    res_string = string_utils.format_by_order(fmt, ["Alice", 5])
    assert res_string == "Hello Alice, you have 5 messages"
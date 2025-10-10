from ccipy.omero import connect

def test_connect_has_flag():
    h = connect("localhost", "u", "p")
    assert h["connected"] is True

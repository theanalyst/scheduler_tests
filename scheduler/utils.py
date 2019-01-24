import platform

def assert_py_version():
    major, minor, _ = platform.python_version_tuple()
    assert int(major) >= 3 and int(minor) >=5

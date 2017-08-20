from os import path
# Parse dynamic version info
version_tuple = (1, 0, 0)

def version_parse(v):
    return tuple(map(int, (v.split("."))))

with open(path.join(path.dirname(path.abspath(__file__)), 'VERSION')) as version_file:
    version = version_file.read().strip()
    version_tuple = version_parse(version)
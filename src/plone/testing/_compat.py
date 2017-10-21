"""Python 3 compat module"""
import sys


PY3 = sys.version_info[0] == 3
if PY3:
    from io import StringIO
else:
    from cStringIO import StringIO
 
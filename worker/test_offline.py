"""Pytest entrypoint with DNS and sockets denied in this interpreter."""
import sys
from collect_v3.offline import no_network
if __name__=='__main__':
    import pytest
    with no_network():raise SystemExit(pytest.main(['-q','-p','no:cacheprovider',*sys.argv[1:]]))

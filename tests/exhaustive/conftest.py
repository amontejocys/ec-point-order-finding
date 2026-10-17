"""Mark every test placed in this directory as slow."""

import pytest


def pytest_collection_modifyitems(items):
    for item in items:
        if "exhaustive" in item.path.relative_to(item.config.rootpath).parts:
            item.add_marker(pytest.mark.slow)

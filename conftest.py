import os

import pytest

# Playwright's sync API keeps an event loop running in the test thread. Django's
# ORM sees that loop and raises SynchronousOnlyOperation during test-database
# setup and during ORM writes inside functional tests. Our database driver is
# synchronous, so those calls are safe. This flag tells Django to allow them.
# It is read at call time, so setting it here (before any test runs) is enough,
# and it is harmless for the inner-loop tests that never touch an event loop.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "1")


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    # Chromium's sandbox cannot run as root, which is how the Playwright
    # container launches by default. Disabling it is safe here because the
    # tests only visit our own local server. Harmless in CI and local runs too.
    return {**browser_type_launch_args, "args": ["--no-sandbox"]}

"""This file contains the test class for steps APIs of TestMonitor."""
import pytest
from nisystemlink.clients.testmonitor import TestMonitorClient

print(TestMonitorClient().get_steps(continuationToken=None, take=1, returnCount=False))

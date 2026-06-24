"""Test CLI module."""

import sys

import pytest

pytest_plugins = [
    'grafana_backup.test.fixtures.fixtures',
]


@pytest.fixture(autouse=True)
def _mock_sys_argv(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['grafana-backup', '--help'])


def test_cli_module_imports():
    from grafana_backup import cli
    assert hasattr(cli, 'main')
    assert hasattr(cli, 'docstring')


@pytest.mark.parametrize(
    'keyword',
    ['save', 'restore', 'delete', 'tools', '--config', '--components', '--no-archive', '--version', '--help'],
)
def test_cli_docstring_contains_keyword(_mock_sys_argv, keyword):
    from grafana_backup.cli import docstring
    assert keyword in docstring

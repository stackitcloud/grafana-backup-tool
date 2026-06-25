"""Test create_alert_rule module."""

import json
import os

import pytest
from packaging import version

from grafana_backup import create_alert_rule

pytest_plugins = [
    'grafana_backup.test.fixtures.fixtures',
]


@pytest.fixture
def alert_rule_file(tmp_path, sample_alert_rule):
    file_path = os.path.join(str(tmp_path), 'alert_rule.json')
    with open(file_path, 'w') as f:
        json.dump(sample_alert_rule, f)
    return file_path


def test_create_alert_rule_version_too_old(mocker, default_settings, alert_rule_file, capsys):
    mocker.patch('grafana_backup.create_alert_rule.get_grafana_version', return_value=version.parse('9.3.0'))

    create_alert_rule.main({}, default_settings, alert_rule_file)

    captured = capsys.readouterr()
    assert 'Unable to create alert rules' in captured.out
    assert '9.4.0' in captured.out


def test_create_alert_rule_version_9_4_0_creates_new(mocker, default_settings, alert_rule_file, sample_alert_rule):
    mocker.patch('grafana_backup.create_alert_rule.get_grafana_version', return_value=version.parse('9.4.0'))
    mocker.patch('grafana_backup.create_alert_rule.get_alert_rule', return_value=(404, {}))
    mock_create = mocker.patch('grafana_backup.create_alert_rule.create_alert_rule', return_value=(200, {'id': 1}))

    create_alert_rule.main({}, default_settings, alert_rule_file)

    mock_create.assert_called_once()
    call_args = mock_create.call_args[0]
    alert_data = json.loads(call_args[0])
    assert 'id' not in alert_data
    assert alert_data['uid'] == sample_alert_rule['uid']


def test_create_alert_rule_version_9_4_0_updates_existing(mocker, default_settings, alert_rule_file, sample_alert_rule):
    mocker.patch('grafana_backup.create_alert_rule.get_grafana_version', return_value=version.parse('9.4.0'))
    mocker.patch('grafana_backup.create_alert_rule.get_alert_rule', return_value=(200, sample_alert_rule))
    mock_update = mocker.patch('grafana_backup.create_alert_rule.update_alert_rule', return_value=(200, {'id': 1}))

    create_alert_rule.main({}, default_settings, alert_rule_file)

    mock_update.assert_called_once()
    call_args = mock_update.call_args[0]
    assert call_args[0] == sample_alert_rule['uid']
    alert_data = json.loads(call_args[1])
    assert 'id' not in alert_data


def test_create_alert_rule_version_10_0_0_creates(mocker, default_settings, alert_rule_file):
    mocker.patch('grafana_backup.create_alert_rule.get_grafana_version', return_value=version.parse('10.0.0'))
    mocker.patch('grafana_backup.create_alert_rule.get_alert_rule', return_value=(404, {}))
    mocker.patch('grafana_backup.create_alert_rule.create_alert_rule', return_value=(200, {'id': 1}))

    create_alert_rule.main({}, default_settings, alert_rule_file)


def test_create_alert_rule_sets_disable_provenance_header(mocker, default_settings, alert_rule_file):
    mocker.patch('grafana_backup.create_alert_rule.get_grafana_version', return_value=version.parse('9.4.0'))
    mocker.patch('grafana_backup.create_alert_rule.get_alert_rule', return_value=(404, {}))
    mocker.patch('grafana_backup.create_alert_rule.create_alert_rule', return_value=(200, {}))

    create_alert_rule.main({}, default_settings, alert_rule_file)

    assert default_settings['HTTP_POST_HEADERS']['x-disable-provenance'] == '*'


def test_create_alert_rule_version_not_set_raises_exception(mocker, default_settings, alert_rule_file):
    default_settings['GRAFANA_VERSION'] = None
    mocker.patch('grafana_backup.create_alert_rule.get_grafana_version', side_effect=KeyError('version'))

    with pytest.raises(Exception):
        create_alert_rule.main({}, default_settings, alert_rule_file)

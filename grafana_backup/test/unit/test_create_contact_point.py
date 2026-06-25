"""Test create_contact_point module."""

import json
import os

import pytest
from packaging import version

from grafana_backup import create_contact_point

pytest_plugins = [
    'grafana_backup.test.fixtures.fixtures',
]


@pytest.fixture
def contact_point_file(tmp_path, sample_contact_point):
    file_path = os.path.join(str(tmp_path), 'contact_point.json')
    with open(file_path, 'w') as f:
        json.dump([sample_contact_point], f)
    return file_path


def test_create_contact_point_version_too_old(mocker, default_settings, contact_point_file, capsys):
    mocker.patch('grafana_backup.create_contact_point.get_grafana_version', return_value=version.parse('9.3.0'))

    create_contact_point.main({}, default_settings, contact_point_file)

    captured = capsys.readouterr()
    assert 'Unable to create contact points' in captured.out
    assert '9.4.0' in captured.out


def test_create_contact_point_creates_new(mocker, default_settings, contact_point_file, sample_contact_point):
    mocker.patch('grafana_backup.create_contact_point.get_grafana_version', return_value=version.parse('9.4.0'))
    mocker.patch('grafana_backup.create_contact_point.search_contact_points', return_value=(200, []))
    mock_create = mocker.patch('grafana_backup.create_contact_point.create_contact_point', return_value=(202, {}))

    create_contact_point.main({}, default_settings, contact_point_file)

    mock_create.assert_called_once()
    call_args = mock_create.call_args[0]
    contact_data = json.loads(call_args[0])
    assert contact_data['uid'] == sample_contact_point['uid']


def test_create_contact_point_updates_existing(mocker, default_settings, contact_point_file, sample_contact_point):
    mocker.patch('grafana_backup.create_contact_point.get_grafana_version', return_value=version.parse('9.4.0'))
    mocker.patch(
        'grafana_backup.create_contact_point.search_contact_points',
        return_value=(200, [{'uid': sample_contact_point['uid']}]),
    )
    mock_update = mocker.patch('grafana_backup.create_contact_point.update_contact_point', return_value=(202, {}))

    create_contact_point.main({}, default_settings, contact_point_file)

    mock_update.assert_called_once()
    call_args = mock_update.call_args[0]
    assert call_args[0] == sample_contact_point['uid']


def test_create_contact_point_multiple_points(mocker, default_settings, tmp_path, sample_contact_point):
    cp1 = sample_contact_point.copy()
    cp1['uid'] = 'uid-1'
    cp2 = sample_contact_point.copy()
    cp2['uid'] = 'uid-2'

    file_path = os.path.join(str(tmp_path), 'contact_points.json')
    with open(file_path, 'w') as f:
        json.dump([cp1, cp2], f)

    mocker.patch('grafana_backup.create_contact_point.get_grafana_version', return_value=version.parse('9.4.0'))
    mocker.patch('grafana_backup.create_contact_point.search_contact_points', return_value=(200, [{'uid': 'uid-1'}]))
    mock_create = mocker.patch('grafana_backup.create_contact_point.create_contact_point', return_value=(202, {}))
    mock_update = mocker.patch('grafana_backup.create_contact_point.update_contact_point', return_value=(202, {}))

    create_contact_point.main({}, default_settings, file_path)

    assert mock_update.call_count == 1
    assert mock_create.call_count == 1


def test_create_contact_point_create_failure(mocker, default_settings, contact_point_file, capsys):
    mocker.patch('grafana_backup.create_contact_point.get_grafana_version', return_value=version.parse('9.4.0'))
    mocker.patch('grafana_backup.create_contact_point.search_contact_points', return_value=(200, []))
    mocker.patch('grafana_backup.create_contact_point.create_contact_point', return_value=(400, 'Bad request'))

    create_contact_point.main({}, default_settings, contact_point_file)

    captured = capsys.readouterr()
    assert '[ERROR]' in captured.out
    assert 'failed to create' in captured.out


def test_create_contact_point_update_failure(
    mocker, default_settings, contact_point_file, sample_contact_point, capsys
):
    mocker.patch('grafana_backup.create_contact_point.get_grafana_version', return_value=version.parse('9.4.0'))
    mocker.patch(
        'grafana_backup.create_contact_point.search_contact_points',
        return_value=(200, [{'uid': sample_contact_point['uid']}]),
    )
    mocker.patch('grafana_backup.create_contact_point.update_contact_point', return_value=(400, 'Bad request'))

    create_contact_point.main({}, default_settings, contact_point_file)

    captured = capsys.readouterr()
    assert '[ERROR]' in captured.out
    assert 'failed to update' in captured.out


def test_create_contact_point_search_failure(mocker, default_settings, contact_point_file):
    mocker.patch('grafana_backup.create_contact_point.get_grafana_version', return_value=version.parse('9.4.0'))
    mocker.patch('grafana_backup.create_contact_point.search_contact_points', return_value=(500, 'Error'))
    mock_create = mocker.patch('grafana_backup.create_contact_point.create_contact_point', return_value=(202, {}))

    create_contact_point.main({}, default_settings, contact_point_file)

    mock_create.assert_called_once()


def test_create_contact_point_version_not_set_raises_exception(mocker, default_settings, contact_point_file):
    default_settings['GRAFANA_VERSION'] = None
    mocker.patch('grafana_backup.create_contact_point.get_grafana_version', side_effect=KeyError('version'))

    with pytest.raises(Exception):
        create_contact_point.main({}, default_settings, contact_point_file)

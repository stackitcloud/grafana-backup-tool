"""Test create_dashboard module."""

import json
import os

import pytest

from grafana_backup import create_dashboard

pytest_plugins = [
    'grafana_backup.test.fixtures.fixtures',
]


@pytest.fixture
def dashboard_file(tmp_path, sample_dashboard_full):
    file_path = os.path.join(str(tmp_path), 'dashboard.json')
    with open(file_path, 'w') as f:
        json.dump(sample_dashboard_full, f)
    return file_path


def test_create_dashboard_sets_id_to_none(mocker, default_settings, dashboard_file):
    mocker.patch('grafana_backup.create_dashboard.get_folder_id', return_value=1)
    mock_create = mocker.patch('grafana_backup.create_dashboard.create_dashboard', return_value=(200, {'id': 1}))
    
    create_dashboard.main({}, default_settings, dashboard_file)
    
    call_args = mock_create.call_args[0]
    payload = json.loads(call_args[0])
    assert payload['dashboard']['id'] is None


def test_create_dashboard_resolves_folder_id(mocker, default_settings, dashboard_file, sample_dashboard_full):
    mock_get_folder_id = mocker.patch('grafana_backup.create_dashboard.get_folder_id', return_value=5)
    mocker.patch('grafana_backup.create_dashboard.create_dashboard', return_value=(200, {'id': 1}))
    
    create_dashboard.main({}, default_settings, dashboard_file)
    
    mock_get_folder_id.assert_called_once()


def test_create_dashboard_payload_structure(mocker, default_settings, dashboard_file, sample_dashboard_full):
    mocker.patch('grafana_backup.create_dashboard.get_folder_id', return_value=1)
    mock_create = mocker.patch('grafana_backup.create_dashboard.create_dashboard', return_value=(200, {'id': 1}))
    
    create_dashboard.main({}, default_settings, dashboard_file)
    
    call_args = mock_create.call_args[0]
    payload = json.loads(call_args[0])
    assert 'dashboard' in payload
    assert 'folderId' in payload
    assert payload['overwrite'] is True


def test_create_dashboard_with_folder_uid(mocker, default_settings, dashboard_file, sample_dashboard_full):
    mocker.patch('grafana_backup.create_dashboard.get_folder_id', return_value=10)
    mock_create = mocker.patch('grafana_backup.create_dashboard.create_dashboard', return_value=(200, {'id': 1}))
    
    create_dashboard.main({}, default_settings, dashboard_file)
    
    call_args = mock_create.call_args[0]
    payload = json.loads(call_args[0])
    assert payload['folderId'] == 10


def test_create_dashboard_without_folder(mocker, default_settings, tmp_path, sample_dashboard_full):
    sample_dashboard_full['meta']['folderUid'] = ''
    sample_dashboard_full['meta']['folderUrl'] = ''
    
    file_path = os.path.join(str(tmp_path), 'dashboard.json')
    with open(file_path, 'w') as f:
        json.dump(sample_dashboard_full, f)
    
    mocker.patch('grafana_backup.create_dashboard.get_folder_id', return_value=0)
    mock_create = mocker.patch('grafana_backup.create_dashboard.create_dashboard', return_value=(200, {'id': 1}))
    
    create_dashboard.main({}, default_settings, file_path)
    
    call_args = mock_create.call_args[0]
    payload = json.loads(call_args[0])
    assert payload['folderId'] == 0


def test_create_dashboard_preserves_dashboard_content(mocker, default_settings, dashboard_file, sample_dashboard_full):
    mocker.patch('grafana_backup.create_dashboard.get_folder_id', return_value=1)
    mock_create = mocker.patch('grafana_backup.create_dashboard.create_dashboard', return_value=(200, {'id': 1}))
    
    create_dashboard.main({}, default_settings, dashboard_file)
    
    call_args = mock_create.call_args[0]
    payload = json.loads(call_args[0])
    assert payload['dashboard']['title'] == sample_dashboard_full['dashboard']['title']
    assert payload['dashboard']['uid'] == sample_dashboard_full['dashboard']['uid']

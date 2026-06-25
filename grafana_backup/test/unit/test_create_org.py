"""Test create_org module."""

import json
import os

import pytest

from grafana_backup import create_org

pytest_plugins = [
    'grafana_backup.test.fixtures.fixtures',
]


@pytest.fixture
def org_file(tmp_path, sample_org):
    file_path = os.path.join(str(tmp_path), 'org.json')
    with open(file_path, 'w') as f:
        json.dump(sample_org, f)
    return file_path


@pytest.fixture(autouse=True)
def setup_basic_auth(default_settings):
    default_settings['HTTP_POST_HEADERS_BASIC_AUTH'] = {'Authorization': 'Basic dGVzdDp0ZXN0'}


def test_create_org_id_1_calls_update(mocker, default_settings, org_file, sample_org):
    sample_org['id'] = 1
    with open(org_file, 'w') as f:
        json.dump(sample_org, f)

    mock_update = mocker.patch('grafana_backup.create_org.update_org', return_value=(200, {}))
    mock_create = mocker.patch('grafana_backup.create_org.create_org')

    create_org.main({}, default_settings, org_file)

    mock_update.assert_called_once()
    mock_create.assert_not_called()


def test_create_org_id_not_1_calls_create(mocker, default_settings, org_file, sample_org):
    sample_org['id'] = 2
    with open(org_file, 'w') as f:
        json.dump(sample_org, f)

    mock_update = mocker.patch('grafana_backup.create_org.update_org')
    mock_create = mocker.patch('grafana_backup.create_org.create_org', return_value=(200, {}))

    create_org.main({}, default_settings, org_file)

    mock_create.assert_called_once()
    mock_update.assert_not_called()


def test_create_org_requires_basic_auth(mocker, default_settings, org_file, capsys):
    default_settings['HTTP_POST_HEADERS_BASIC_AUTH'] = None

    create_org.main({}, default_settings, org_file)

    captured = capsys.readouterr()
    assert '[ERROR]' in captured.out
    assert 'GRAFANA_ADMIN_ACCOUNT' in captured.out


def test_create_org_update_passes_correct_args(mocker, default_settings, org_file, sample_org):
    sample_org['id'] = 1
    with open(org_file, 'w') as f:
        json.dump(sample_org, f)

    mock_update = mocker.patch('grafana_backup.create_org.update_org', return_value=(200, {}))

    create_org.main({}, default_settings, org_file)

    call_args = mock_update.call_args[0]
    assert call_args[0] == 1
    org_data = json.loads(call_args[1])
    assert org_data['name'] == sample_org['name']


def test_create_org_create_passes_correct_args(mocker, default_settings, org_file, sample_org):
    sample_org['id'] = 2
    with open(org_file, 'w') as f:
        json.dump(sample_org, f)

    mock_create = mocker.patch('grafana_backup.create_org.create_org', return_value=(200, {}))

    create_org.main({}, default_settings, org_file)

    call_args = mock_create.call_args[0]
    org_data = json.loads(call_args[0])
    assert org_data['name'] == sample_org['name']
    assert org_data['id'] == 2


@pytest.mark.parametrize('org_id', [1, 2, 3, 10])
def test_create_org_multiple_ids(mocker, default_settings, tmp_path, sample_org, org_id):
    sample_org['id'] = org_id
    file_path = os.path.join(str(tmp_path), f'org_{org_id}.json')
    with open(file_path, 'w') as f:
        json.dump(sample_org, f)

    mock_update = mocker.patch('grafana_backup.create_org.update_org', return_value=(200, {}))
    mock_create = mocker.patch('grafana_backup.create_org.create_org', return_value=(200, {}))

    create_org.main({}, default_settings, file_path)

    if org_id == 1:
        mock_update.assert_called_once()
        mock_create.assert_not_called()
    else:
        mock_create.assert_called_once()
        mock_update.assert_not_called()

"""Test create_user module."""

import json
import os

import pytest

from grafana_backup import create_user

pytest_plugins = [
    'grafana_backup.test.fixtures.fixtures',
]


@pytest.fixture
def user_file(tmp_path, sample_user):
    file_path = os.path.join(str(tmp_path), 'user.json')
    with open(file_path, 'w') as f:
        json.dump(sample_user, f)
    return file_path


@pytest.fixture(autouse=True)
def setup_basic_auth(default_settings):
    default_settings['HTTP_POST_HEADERS_BASIC_AUTH'] = {'Authorization': 'Basic dGVzdDp0ZXN0'}


def test_create_user_sets_default_password(mocker, default_settings, user_file, sample_user):
    mock_create = mocker.patch('grafana_backup.create_user.create_user', return_value=(200, {}))
    mocker.patch('grafana_backup.create_user.add_user_to_org', return_value=(200, {}))
    
    create_user.main({}, default_settings, user_file)
    
    call_args = mock_create.call_args[0]
    user_data = json.loads(call_args[0])
    assert user_data['password'] == default_settings['DEFAULT_USER_PASSWORD']


def test_create_user_requires_basic_auth(mocker, default_settings, user_file, capsys):
    default_settings['HTTP_POST_HEADERS_BASIC_AUTH'] = None
    
    create_user.main({}, default_settings, user_file)
    
    captured = capsys.readouterr()
    assert '[ERROR]' in captured.out
    assert 'GRAFANA_ADMIN_ACCOUNT' in captured.out


def test_create_user_adds_to_orgs_on_success(mocker, default_settings, user_file, sample_user):
    mocker.patch('grafana_backup.create_user.create_user', return_value=(200, {}))
    mock_add_to_org = mocker.patch('grafana_backup.create_user.add_user_to_org', return_value=(200, {}))
    
    create_user.main({}, default_settings, user_file)
    
    assert mock_add_to_org.call_count == len(sample_user.get('orgs', []))


def test_create_user_does_not_add_to_orgs_on_failure(mocker, default_settings, user_file):
    mocker.patch('grafana_backup.create_user.create_user', return_value=(400, 'Bad request'))
    mock_add_to_org = mocker.patch('grafana_backup.create_user.add_user_to_org')
    
    create_user.main({}, default_settings, user_file)
    
    mock_add_to_org.assert_not_called()


def test_create_user_org_payload_structure(mocker, default_settings, user_file, sample_user):
    mocker.patch('grafana_backup.create_user.create_user', return_value=(200, {}))
    mock_add_to_org = mocker.patch('grafana_backup.create_user.add_user_to_org', return_value=(200, {}))
    
    create_user.main({}, default_settings, user_file)
    
    for i, org in enumerate(sample_user.get('orgs', [])):
        call_args = mock_add_to_org.call_args_list[i][0]
        assert call_args[0] == org['orgId']
        org_payload = json.loads(call_args[1])
        assert org_payload['loginOrEmail'] == sample_user['login']
        assert org_payload['role'] == org['role']


def test_create_user_no_orgs(mocker, default_settings, tmp_path, sample_user):
    sample_user['orgs'] = []
    file_path = os.path.join(str(tmp_path), 'user.json')
    with open(file_path, 'w') as f:
        json.dump(sample_user, f)
    
    mocker.patch('grafana_backup.create_user.create_user', return_value=(200, {}))
    mock_add_to_org = mocker.patch('grafana_backup.create_user.add_user_to_org')
    
    create_user.main({}, default_settings, file_path)
    
    mock_add_to_org.assert_not_called()


def test_create_user_multiple_orgs(mocker, default_settings, tmp_path, sample_user):
    sample_user['orgs'] = [
        {'orgId': 1, 'name': 'Org1', 'role': 'Admin'},
        {'orgId': 2, 'name': 'Org2', 'role': 'Editor'},
        {'orgId': 3, 'name': 'Org3', 'role': 'Viewer'},
    ]
    file_path = os.path.join(str(tmp_path), 'user.json')
    with open(file_path, 'w') as f:
        json.dump(sample_user, f)
    
    mocker.patch('grafana_backup.create_user.create_user', return_value=(200, {}))
    mock_add_to_org = mocker.patch('grafana_backup.create_user.add_user_to_org', return_value=(200, {}))
    
    create_user.main({}, default_settings, file_path)
    
    assert mock_add_to_org.call_count == 3


def test_create_user_preserves_user_data(mocker, default_settings, user_file, sample_user):
    mock_create = mocker.patch('grafana_backup.create_user.create_user', return_value=(200, {}))
    mocker.patch('grafana_backup.create_user.add_user_to_org', return_value=(200, {}))
    
    create_user.main({}, default_settings, user_file)
    
    call_args = mock_create.call_args[0]
    user_data = json.loads(call_args[0])
    assert user_data['login'] == sample_user['login']
    assert user_data['email'] == sample_user['email']
    assert user_data['name'] == sample_user['name']


@pytest.mark.parametrize('status_code', [200, 201, 400, 500])
def test_create_user_various_status_codes(mocker, default_settings, user_file, status_code):
    mock_create = mocker.patch('grafana_backup.create_user.create_user', return_value=(status_code, {}))
    mock_add_to_org = mocker.patch('grafana_backup.create_user.add_user_to_org', return_value=(200, {}))
    
    create_user.main({}, default_settings, user_file)
    
    mock_create.assert_called_once()
    if status_code == 200:
        assert mock_add_to_org.called
    else:
        mock_add_to_org.assert_not_called()

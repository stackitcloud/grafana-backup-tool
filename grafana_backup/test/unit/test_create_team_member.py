"""Test create_team_member module."""

import json
import os

import pytest

from grafana_backup import create_team_member

pytest_plugins = [
    'grafana_backup.test.fixtures.fixtures',
]


@pytest.fixture
def team_member_file(tmp_path, sample_team_member):
    file_path = os.path.join(str(tmp_path), 'team_member.json')
    with open(file_path, 'w') as f:
        json.dump(sample_team_member, f)
    return file_path


@pytest.fixture(autouse=True)
def setup_basic_auth(default_settings):
    default_settings['HTTP_GET_HEADERS_BASIC_AUTH'] = {'Authorization': 'Basic dGVzdDp0ZXN0'}


def test_create_team_member_lookup_by_email(mocker, default_settings, team_member_file, sample_team_member):
    mock_get_user = mocker.patch(
        'grafana_backup.create_team_member.get_user_by_email_or_username', return_value=(200, {'id': 123})
    )
    mock_create = mocker.patch('grafana_backup.create_team_member.create_team_member', return_value=(200, {}))

    create_team_member.main({}, default_settings, team_member_file)

    mock_get_user.assert_called_once()
    call_args = mock_get_user.call_args[0]
    assert 'user%40example.com' in call_args[0] or 'user@example.com' in call_args[0]

    mock_create.assert_called_once()
    create_call_args = mock_create.call_args[0]
    user_data = json.loads(create_call_args[0])
    assert user_data['userId'] == 123


def test_create_team_member_fallback_to_name(mocker, default_settings, team_member_file, sample_team_member):
    mock_get_user = mocker.patch(
        'grafana_backup.create_team_member.get_user_by_email_or_username', side_effect=[(404, {}), (200, {'id': 456})]
    )
    mock_create = mocker.patch('grafana_backup.create_team_member.create_team_member', return_value=(200, {}))

    create_team_member.main({}, default_settings, team_member_file)

    assert mock_get_user.call_count == 2
    second_call_args = mock_get_user.call_args_list[1][0]
    assert 'Test%20User' in second_call_args[0] or 'Test User' in second_call_args[0]

    mock_create.assert_called_once()
    create_call_args = mock_create.call_args[0]
    user_data = json.loads(create_call_args[0])
    assert user_data['userId'] == 456


def test_create_team_member_user_not_found(mocker, default_settings, team_member_file):
    mocker.patch('grafana_backup.create_team_member.get_user_by_email_or_username', side_effect=[(404, {}), (404, {})])
    mock_create = mocker.patch('grafana_backup.create_team_member.create_team_member')

    create_team_member.main({}, default_settings, team_member_file)

    mock_create.assert_not_called()


def test_create_team_member_requires_basic_auth(mocker, default_settings, team_member_file, capsys):
    default_settings['HTTP_GET_HEADERS_BASIC_AUTH'] = None

    create_team_member.main({}, default_settings, team_member_file)

    captured = capsys.readouterr()
    assert '[ERROR]' in captured.out
    assert 'GRAFANA_ADMIN_ACCOUNT' in captured.out


def test_create_team_member_passes_team_id(mocker, default_settings, team_member_file, sample_team_member):
    mocker.patch('grafana_backup.create_team_member.get_user_by_email_or_username', return_value=(200, {'id': 123}))
    mock_create = mocker.patch('grafana_backup.create_team_member.create_team_member', return_value=(200, {}))

    create_team_member.main({}, default_settings, team_member_file)

    call_args = mock_create.call_args[0]
    assert call_args[1] == sample_team_member['teamId']


def test_create_team_member_email_url_encoded(mocker, default_settings, team_member_file, sample_team_member):
    sample_team_member['email'] = 'user+test@example.com'
    with open(team_member_file, 'w') as f:
        json.dump(sample_team_member, f)

    mock_get_user = mocker.patch(
        'grafana_backup.create_team_member.get_user_by_email_or_username', return_value=(200, {'id': 123})
    )
    mocker.patch('grafana_backup.create_team_member.create_team_member', return_value=(200, {}))

    create_team_member.main({}, default_settings, team_member_file)

    call_args = mock_get_user.call_args[0]
    assert '%2B' in call_args[0] or '+' in call_args[0]

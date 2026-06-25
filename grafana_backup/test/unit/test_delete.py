"""Test delete module."""

import pytest

from grafana_backup import delete

pytest_plugins = [
    'grafana_backup.test.fixtures.fixtures',
]

DELETE_API_CHECKS_RETURN = (200, {}, True, True, True)

DELETE_FUNCTIONS = [
    ('dashboards', 'delete_dashboards'),
    ('datasources', 'delete_datasources'),
    ('folders', 'delete_folders'),
    ('alert-channels', 'delete_alert_channels'),
    ('snapshots', 'delete_snapshots'),
    ('annotations', 'delete_annotations'),
    ('library-elements', 'delete_library_elements'),
    ('team-members', 'delete_team_members'),
]


def test_delete_all_components(mocker, default_settings):
    mocker.patch('grafana_backup.delete.api_checks', return_value=DELETE_API_CHECKS_RETURN)

    mocked = {}
    for _, func_name in DELETE_FUNCTIONS:
        mocked[func_name] = mocker.patch(f'grafana_backup.delete.{func_name}')

    args = {'--components': False}
    delete.main(args, default_settings)

    for func_name, fn in mocked.items():
        fn.assert_called_once_with(args, default_settings)


@pytest.mark.parametrize(('component', 'func_name'), DELETE_FUNCTIONS)
def test_delete_specific_component(mocker, default_settings, component, func_name):
    mocker.patch('grafana_backup.delete.api_checks', return_value=DELETE_API_CHECKS_RETURN)
    mock_fn = mocker.patch(f'grafana_backup.delete.{func_name}')

    args = {'--components': component}
    delete.main(args, default_settings)

    mock_fn.assert_called_once()


def test_delete_api_failure_exits(mocker, default_settings):
    mocker.patch('grafana_backup.delete.api_checks', return_value=(500, {'message': 'error'}, None, None, None))
    mock_delete = mocker.patch('grafana_backup.delete.delete_dashboards')

    args = {'--components': 'dashboards'}
    with pytest.raises(SystemExit):
        delete.main(args, default_settings)
    mock_delete.assert_not_called()


def test_delete_updates_settings_with_feature_flags(mocker, default_settings):
    mocker.patch('grafana_backup.delete.api_checks', return_value=(200, {}, True, False, True))
    mocker.patch('grafana_backup.delete.delete_dashboards')

    args = {'--components': 'dashboards'}
    delete.main(args, default_settings)

    assert default_settings['DASHBOARD_UID_SUPPORT'] is True
    assert default_settings['DATASOURCE_UID_SUPPORT'] is False
    assert default_settings['PAGING_SUPPORT'] is True


def test_delete_teams_not_in_default_functions(mocker, default_settings):
    mocker.patch('grafana_backup.delete.api_checks', return_value=DELETE_API_CHECKS_RETURN)
    for _, func_name in DELETE_FUNCTIONS:
        mocker.patch(f'grafana_backup.delete.{func_name}')

    args = {'--components': False}
    delete.main(args, default_settings)

    import inspect

    from grafana_backup.delete import main as delete_main

    source = inspect.getsource(delete_main)
    assert 'delete_teams' not in source or 'teams' not in source.split('delete_functions')[1].split('{')[1]

"""Test save module."""

import pytest

from grafana_backup import save

pytest_plugins = [
    'grafana_backup.test.fixtures.fixtures',
]

SAVE_API_CHECKS_RETURN = (200, {}, True, True, True, True)

SAVE_FUNCTIONS = [
    ('dashboards', 'save_dashboards'),
    ('datasources', 'save_datasources'),
    ('folders', 'save_folders'),
    ('alert-channels', 'save_alert_channels'),
    ('organizations', 'save_orgs'),
    ('users', 'save_users'),
    ('snapshots', 'save_snapshots'),
    ('annotations', 'save_annotations'),
    ('library-elements', 'save_library_elements'),
    ('teams', 'save_teams'),
    ('team-members', 'save_team_members'),
    ('alert-rules', 'save_alert_rules'),
    ('contact-points', 'save_contact_points'),
    ('notification-policy', 'save_notification_policies'),
]


def test_save_all_components(mocker, default_settings):
    mocker.patch('grafana_backup.save.api_checks', return_value=SAVE_API_CHECKS_RETURN)

    mocked = {}
    for _, func_name in SAVE_FUNCTIONS:
        mocked[func_name] = mocker.patch(f'grafana_backup.save.{func_name}')
    mocked['save_dashboard_versions'] = mocker.patch('grafana_backup.save.save_dashboard_versions')

    mocker.patch('grafana_backup.save.archive')

    args = {'--components': False, '--no-archive': False}
    save.main(args, default_settings)

    for func_name, fn in mocked.items():
        if func_name == 'save_dashboard_versions':
            assert fn.call_count == 2
        else:
            fn.assert_called_once()


def test_save_dashboard_versions_called_twice_for_versions_and_dashboard_versions(mocker, default_settings):
    mocker.patch('grafana_backup.save.api_checks', return_value=SAVE_API_CHECKS_RETURN)
    mock_versions = mocker.patch('grafana_backup.save.save_dashboard_versions')
    for _, func_name in SAVE_FUNCTIONS:
        if func_name != 'save_dashboard_versions':
            mocker.patch(f'grafana_backup.save.{func_name}')
    mocker.patch('grafana_backup.save.archive')

    args = {'--components': False, '--no-archive': False}
    save.main(args, default_settings)

    assert mock_versions.call_count == 2


@pytest.mark.parametrize(('component', 'func_name'), SAVE_FUNCTIONS)
def test_save_specific_component(mocker, default_settings, component, func_name):
    mocker.patch('grafana_backup.save.api_checks', return_value=SAVE_API_CHECKS_RETURN)
    mock_fn = mocker.patch(f'grafana_backup.save.{func_name}')
    mocker.patch('grafana_backup.save.archive')

    args = {'--components': component, '--no-archive': False}
    save.main(args, default_settings)

    mock_fn.assert_called_once()


@pytest.mark.parametrize(
    ('no_archive', 'archive_called'),
    [(True, False), (False, True)],
)
def test_save_archive_flag(mocker, default_settings, no_archive, archive_called):
    mocker.patch('grafana_backup.save.api_checks', return_value=SAVE_API_CHECKS_RETURN)
    mocker.patch('grafana_backup.save.save_dashboards')
    mock_archive = mocker.patch('grafana_backup.save.archive')

    args = {'--components': 'dashboards', '--no-archive': no_archive}
    save.main(args, default_settings)

    assert mock_archive.called == archive_called


def test_save_api_failure_exits(mocker, default_settings):
    mocker.patch('grafana_backup.save.api_checks', return_value=(500, {'message': 'error'}, None, None, None, None))
    mock_save = mocker.patch('grafana_backup.save.save_dashboards')

    args = {'--components': 'dashboards', '--no-archive': False}
    with pytest.raises(SystemExit):
        save.main(args, default_settings)
    mock_save.assert_not_called()


@pytest.mark.parametrize(
    ('setting_key', 'setting_value', 'upload_func'),
    [
        ('AWS_S3_BUCKET_NAME', 'my-bucket', 's3_upload'),
        ('AZURE_STORAGE_CONTAINER_NAME', 'my-container', 'azure_storage_upload'),
        ('GCS_BUCKET_NAME', 'my-gcs-bucket', 'gcs_upload'),
        ('INFLUXDB_HOST', 'influx.example.com', 'influx'),
    ],
)
def test_save_upload_targets(mocker, default_settings, setting_key, setting_value, upload_func):
    mocker.patch('grafana_backup.save.api_checks', return_value=SAVE_API_CHECKS_RETURN)
    mocker.patch('grafana_backup.save.save_dashboards')
    mocker.patch('grafana_backup.save.archive')
    mock_upload = mocker.patch(f'grafana_backup.save.{upload_func}')

    default_settings[setting_key] = setting_value

    args = {'--components': 'dashboards', '--no-archive': False}
    save.main(args, default_settings)

    mock_upload.assert_called_once()


def test_save_updates_settings_with_feature_flags(mocker, default_settings):
    mocker.patch('grafana_backup.save.api_checks', return_value=(200, {}, True, False, True, True))
    mocker.patch('grafana_backup.save.save_dashboards')
    mocker.patch('grafana_backup.save.archive')

    args = {'--components': 'dashboards', '--no-archive': False}
    save.main(args, default_settings)

    assert default_settings['DASHBOARD_UID_SUPPORT'] is True
    assert default_settings['DATASOURCE_UID_SUPPORT'] is False
    assert default_settings['PAGING_SUPPORT'] is True
    assert default_settings['CONTACT_POINT_SUPPORT'] is True


@pytest.mark.parametrize(
    ('components_arg', 'expected_funcs'),
    [
        ('library_elements', ['save_library_elements']),
        ('dashboard_versions', ['save_dashboard_versions']),
        ('alert-rules,contact-points', ['save_alert_rules', 'save_contact_points']),
    ],
)
def test_save_component_name_normalization(mocker, default_settings, components_arg, expected_funcs):
    mocker.patch('grafana_backup.save.api_checks', return_value=SAVE_API_CHECKS_RETURN)
    mocked = {}
    for func_name in expected_funcs:
        mocked[func_name] = mocker.patch(f'grafana_backup.save.{func_name}')
    mocker.patch('grafana_backup.save.archive')

    args = {'--components': components_arg, '--no-archive': False}
    save.main(args, default_settings)

    for func_name, fn in mocked.items():
        fn.assert_called()

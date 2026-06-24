"""Test restore module."""

import io
import json
import os
import tarfile
import tempfile

import pytest

from grafana_backup import restore

pytest_plugins = [
    'grafana_backup.test.fixtures.fixtures',
]

RESTORE_API_CHECKS_RETURN = (200, {}, True, True, True, True)


@pytest.fixture
def backup_archive(tmp_path, default_settings):
    backup_dir = str(tmp_path / 'backup')
    os.makedirs(backup_dir)
    timestamp = '202401011200'

    for folder, ext in [('folders', 'folder'), ('datasources', 'datasource'), ('dashboards', 'dashboard')]:
        folder_path = os.path.join(backup_dir, folder, timestamp)
        os.makedirs(folder_path)
        with open(os.path.join(folder_path, f'test.{ext}'), 'w') as f:
            json.dump({'title': 'Test', 'uid': 'test-uid'}, f)

    archive_path = os.path.join(backup_dir, f'{timestamp}.tar.gz')
    with tarfile.open(archive_path, 'w:gz') as tar:
        for folder in ['folders', 'datasources', 'dashboards']:
            folder_path = os.path.join(backup_dir, folder, timestamp)
            tar.add(folder_path, arcname=os.path.join(folder, timestamp))

    return archive_path


def test_restore_all_components(mocker, default_settings, backup_archive):
    mocker.patch('grafana_backup.restore.api_checks', return_value=RESTORE_API_CHECKS_RETURN)

    for name in [
        'create_folder', 'create_datasource', 'create_library_element', 'create_dashboard',
        'create_alert_channel', 'create_org', 'create_user', 'create_snapshot',
        'create_annotation', 'create_team', 'create_team_member',
        'update_folder_permissions', 'create_alert_rule', 'create_contact_point',
    ]:
        mocker.patch(f'grafana_backup.restore.{name}')

    args = {'<archive_file>': backup_archive, '--components': []}
    restore.main(args, default_settings)


def test_restore_api_failure_exits(mocker, default_settings, backup_archive):
    mocker.patch('grafana_backup.restore.api_checks', return_value=(500, {'message': 'error'}, None, None, None, None))
    mock_create = mocker.patch('grafana_backup.restore.create_folder')

    args = {'<archive_file>': backup_archive, '--components': []}
    with pytest.raises(SystemExit):
        restore.main(args, default_settings)
    mock_create.assert_not_called()


@pytest.mark.parametrize(
    ('storage_key', 'storage_value', 'download_func'),
    [
        ('AWS_S3_BUCKET_NAME', 'my-bucket', 's3_download'),
        ('AZURE_STORAGE_CONTAINER_NAME', 'my-container', 'azure_storage_download'),
        ('GCS_BUCKET_NAME', 'my-gcs-bucket', 'gcs_download'),
    ],
)
def test_restore_from_cloud_storage(mocker, default_settings, storage_key, storage_value, download_func):
    mocker.patch('grafana_backup.restore.api_checks', return_value=RESTORE_API_CHECKS_RETURN)

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w:gz'):
        pass
    buf.seek(0)

    mocker.patch(f'grafana_backup.restore.{download_func}', return_value=buf)
    mocker.patch('grafana_backup.restore.restore_components')

    default_settings[storage_key] = storage_value

    args = {'<archive_file>': 'test.tar.gz', '--components': []}
    restore.main(args, default_settings)


def test_restore_updates_contact_point_setting(mocker, default_settings, backup_archive):
    mocker.patch('grafana_backup.restore.api_checks', return_value=RESTORE_API_CHECKS_RETURN)
    mocker.patch('grafana_backup.restore.restore_components')

    args = {'<archive_file>': backup_archive, '--components': []}
    restore.main(args, default_settings)
    assert 'CONTACT_POINT_SUPPORT' in default_settings


def test_restore_components_with_components_arg(mocker, default_settings):
    mock_create_folder = mocker.Mock()
    restore_functions = {'folder': mock_create_folder}

    with tempfile.TemporaryDirectory() as tmpdir:
        folder_path = os.path.join(tmpdir, 'test.folder')
        with open(folder_path, 'w') as f:
            f.write('{}')

        args = {'--components': 'folders'}
        restore.restore_components(args, default_settings, restore_functions, tmpdir)

    mock_create_folder.assert_called_once()


def test_restore_components_without_components_arg(mocker, default_settings):
    mock_create_folder = mocker.Mock()
    restore_functions = {'folder': mock_create_folder}

    with tempfile.TemporaryDirectory() as tmpdir:
        folder_path = os.path.join(tmpdir, 'test.folder')
        with open(folder_path, 'w') as f:
            f.write('{}')

        args = {'--components': []}
        restore.restore_components(args, default_settings, restore_functions, tmpdir)

    mock_create_folder.assert_called_once()


@pytest.mark.parametrize(
    ('components_arg', 'ext_pattern'),
    [
        ('folders', 'folder'),
        ('dashboards', 'dashboard'),
        ('datasources', 'datasource'),
    ],
)
def test_restore_components_matches_correct_extensions(mocker, default_settings, components_arg, ext_pattern):
    mock_fn = mocker.Mock()
    restore_functions = {ext_pattern: mock_fn}

    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, f'test.{ext_pattern}'), 'w') as f:
            f.write('{}')

        args = {'--components': components_arg}
        restore.restore_components(args, default_settings, restore_functions, tmpdir)

    mock_fn.assert_called_once()

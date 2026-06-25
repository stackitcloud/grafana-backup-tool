"""Test archive module."""

import os
import tarfile

import pytest

from grafana_backup import archive

pytest_plugins = [
    'grafana_backup.test.fixtures.fixtures',
]


def test_archive_creates_tarball(tmp_path, default_settings):
    backup_dir = str(tmp_path / 'backup')
    os.makedirs(backup_dir)
    default_settings['BACKUP_DIR'] = backup_dir

    for folder in ['dashboards', 'datasources', 'folders']:
        folder_path = os.path.join(backup_dir, folder, '202401011200')
        os.makedirs(folder_path)
        with open(os.path.join(folder_path, 'test.json'), 'w') as f:
            f.write('{}')

    archive.main({}, default_settings)

    archive_file = os.path.join(backup_dir, '202401011200.tar.gz')
    assert os.path.exists(archive_file)
    assert tarfile.is_tarfile(archive_file)


def test_archive_contains_expected_files(tmp_path, default_settings):
    backup_dir = str(tmp_path / 'backup')
    os.makedirs(backup_dir)
    default_settings['BACKUP_DIR'] = backup_dir

    folder_path = os.path.join(backup_dir, 'dashboards', '202401011200')
    os.makedirs(folder_path)
    with open(os.path.join(folder_path, 'dashboard1.json'), 'w') as f:
        f.write('{"title": "Test"}')

    archive.main({}, default_settings)

    archive_file = os.path.join(backup_dir, '202401011200.tar.gz')
    with tarfile.open(archive_file, 'r:gz') as tar:
        names = tar.getnames()
    assert len(names) > 0


def test_archive_removes_source_directories(tmp_path, default_settings):
    backup_dir = str(tmp_path / 'backup')
    os.makedirs(backup_dir)
    default_settings['BACKUP_DIR'] = backup_dir

    folder_path = os.path.join(backup_dir, 'dashboards', '202401011200')
    os.makedirs(folder_path)
    with open(os.path.join(folder_path, 'test.json'), 'w') as f:
        f.write('{}')

    archive.main({}, default_settings)
    assert not os.path.exists(folder_path)


def test_archive_overwrites_existing(tmp_path, default_settings):
    backup_dir = str(tmp_path / 'backup')
    os.makedirs(backup_dir)
    default_settings['BACKUP_DIR'] = backup_dir

    archive_file = os.path.join(backup_dir, '202401011200.tar.gz')
    with open(archive_file, 'w') as f:
        f.write('old content')

    folder_path = os.path.join(backup_dir, 'dashboards', '202401011200')
    os.makedirs(folder_path)
    with open(os.path.join(folder_path, 'test.json'), 'w') as f:
        f.write('{}')

    archive.main({}, default_settings)

    with tarfile.open(archive_file, 'r:gz') as tar:
        assert len(tar.getnames()) > 0


def test_archive_empty_backup_dir(tmp_path, default_settings):
    backup_dir = str(tmp_path / 'backup')
    os.makedirs(backup_dir)
    default_settings['BACKUP_DIR'] = backup_dir

    archive.main({}, default_settings)

    archive_file = os.path.join(backup_dir, '202401011200.tar.gz')
    assert os.path.exists(archive_file)
    with tarfile.open(archive_file, 'r:gz') as tar:
        assert len(tar.getnames()) == 0


ALL_FOLDERS = [
    'folders',
    'datasources',
    'dashboards',
    'alert_channels',
    'organizations',
    'users',
    'snapshots',
    'dashboard_versions',
    'annotations',
    'library-elements',
    'teams',
    'team_members',
    'alert_rules',
    'contact_points',
    'notification_policies',
]


@pytest.mark.parametrize('folder', ALL_FOLDERS)
def test_archive_each_component_folder(tmp_path, default_settings, folder):
    backup_dir = str(tmp_path / 'backup')
    os.makedirs(backup_dir)
    default_settings['BACKUP_DIR'] = backup_dir

    folder_path = os.path.join(backup_dir, folder, '202401011200')
    os.makedirs(folder_path)
    with open(os.path.join(folder_path, 'item.json'), 'w') as f:
        f.write('{}')

    archive.main({}, default_settings)

    archive_file = os.path.join(backup_dir, '202401011200.tar.gz')
    with tarfile.open(archive_file, 'r:gz') as tar:
        names = tar.getnames()
    file_entries = [n for n in names if n.endswith('item.json')]
    assert len(file_entries) == 1

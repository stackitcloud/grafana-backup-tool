"""Global pytest fixtures."""

import pytest


@pytest.fixture
def default_settings():
    return {
        'GRAFANA_URL': 'http://localhost:3000',
        'GRAFANA_VERSION': '10.0.0',
        'GRAFANA_ADMIN_ACCOUNT': 'admin',
        'GRAFANA_ADMIN_PASSWORD': 'admin',
        'TOKEN': 'test-token',
        'SEARCH_API_LIMIT': 5000,
        'DEFAULT_USER_PASSWORD': '00000000',
        'DEBUG': False,
        'API_HEALTH_CHECK': True,
        'API_AUTH_CHECK': True,
        'VERIFY_SSL': False,
        'CLIENT_CERT': None,
        'BACKUP_DIR': '/tmp/grafana-backup',
        'BACKUP_FILE_FORMAT': '%Y%m%d%H%M',
        'PRETTY_PRINT': False,
        'UID_DASHBOARD_SLUG_SUFFIX': False,
        'EXTRA_HEADERS': {},
        'HTTP_GET_HEADERS': {'Authorization': 'Bearer test-token'},
        'HTTP_POST_HEADERS': {'Authorization': 'Bearer test-token', 'Content-Type': 'application/json'},
        'HTTP_GET_HEADERS_BASIC_AUTH': None,
        'HTTP_POST_HEADERS_BASIC_AUTH': None,
        'TIMESTAMP': '202401011200',
        'DASHBOARD_UID_SUPPORT': True,
        'DATASOURCE_UID_SUPPORT': True,
        'PAGING_SUPPORT': True,
        'CONTACT_POINT_SUPPORT': True,
        'AWS_S3_BUCKET_NAME': '',
        'AWS_S3_BUCKET_KEY': '',
        'AWS_DEFAULT_REGION': '',
        'AWS_ACCESS_KEY_ID': '',
        'AWS_SECRET_ACCESS_KEY': '',
        'AWS_ENDPOINT_URL': None,
        'AZURE_STORAGE_CONTAINER_NAME': '',
        'AZURE_STORAGE_CONNECTION_STRING': '',
        'GCS_BUCKET_NAME': '',
        'GCS_BUCKET_PATH': '',
        'INFLUXDB_MEASUREMENT': 'grafana_backup',
        'INFLUXDB_HOST': '',
        'INFLUXDB_PORT': 8086,
        'INFLUXDB_USERNAME': '',
        'INFLUXDB_PASSWORD': '',
        'INFLUXDB_DATABASE': '',
    }


@pytest.fixture
def sample_dashboard():
    return {
        'id': 1,
        'uid': 'abc123',
        'title': 'Test Dashboard',
        'tags': ['test'],
        'timezone': 'browser',
        'schemaVersion': 30,
        'version': 1,
    }


@pytest.fixture
def sample_dashboard_full():
    return {
        'meta': {
            'type': 'db',
            'canSave': True,
            'canEdit': True,
            'canAdmin': True,
            'canStar': True,
            'slug': 'test-dashboard',
            'url': '/d/abc123/test-dashboard',
            'folderId': 1,
            'folderUid': 'folder-uid-1',
            'folderTitle': 'Test Folder',
            'folderUrl': '/dashboards/f/folder-uid-1/test-folder',
        },
        'dashboard': {
            'id': 1,
            'uid': 'abc123',
            'title': 'Test Dashboard',
            'tags': ['test'],
            'timezone': 'browser',
            'schemaVersion': 30,
            'version': 1,
        },
    }


@pytest.fixture
def sample_datasource():
    return {
        'id': 1,
        'uid': 'ds-uid-1',
        'orgId': 1,
        'name': 'Prometheus',
        'type': 'prometheus',
        'typeLogoUrl': '',
        'access': 'proxy',
        'url': 'http://localhost:9090',
        'password': '',
        'user': '',
        'database': '',
        'basicAuth': False,
        'isDefault': True,
        'jsonData': {},
        'readOnly': False,
    }


@pytest.fixture
def sample_folder():
    return {
        'id': 1,
        'uid': 'folder-uid-1',
        'title': 'Test Folder',
        'url': '/dashboards/f/folder-uid-1/test-folder',
        'hasAcl': False,
        'canSave': True,
        'canEdit': True,
        'canAdmin': True,
    }


@pytest.fixture
def sample_folder_permissions():
    return [
        {
            'uid': 'folder-uid-1',
            'title': 'Test Folder',
            'items': [
                {'role': 'Viewer', 'permission': 1},
                {'role': 'Editor', 'permission': 2},
            ],
        }
    ]


@pytest.fixture
def sample_alert_channel():
    return {
        'id': 1,
        'uid': 'alert-ch-uid-1',
        'name': 'Test Alert Channel',
        'type': 'email',
        'isDefault': False,
        'sendReminder': False,
        'settings': {'addresses': 'test@example.com'},
    }


@pytest.fixture
def sample_org():
    return {
        'id': 1,
        'name': 'Main Org.',
        'address': {'address1': '', 'address2': '', 'city': '', 'zipCode': '', 'state': '', 'country': ''},
    }


@pytest.fixture
def sample_user():
    return {
        'id': 1,
        'userId': 1,
        'login': 'admin',
        'name': 'Admin',
        'email': 'admin@example.com',
        'role': 'Admin',
        'orgs': [{'orgId': 1, 'name': 'Main Org.', 'role': 'Admin'}],
    }


@pytest.fixture
def sample_team():
    return {
        'id': 1,
        'uid': 'team-uid-1',
        'name': 'Test Team',
        'email': 'team@example.com',
        'avatarUrl': '',
        'memberCount': 2,
        'permission': 0,
    }


@pytest.fixture
def sample_team_member():
    return {
        'userId': 1,
        'teamId': 1,
        'email': 'user@example.com',
        'name': 'Test User',
        'login': 'testuser',
    }


@pytest.fixture
def sample_snapshot():
    return {
        'id': 1,
        'name': 'Test Snapshot',
        'key': 'snapshot-key-1',
        'deleteKey': 'delete-key-1',
        'url': 'http://localhost:3000/dashboard/snapshot/snapshot-key-1',
        'dashboard': {
            'title': 'Test Snapshot Dashboard',
            'tags': ['test'],
        },
    }


@pytest.fixture
def sample_annotation():
    return {
        'id': 1,
        'alertId': 0,
        'userId': 1,
        'dashboardId': 1,
        'panelId': 1,
        'text': 'Test annotation',
        'time': 1704067200000,
        'timeEnd': 1704067200000,
        'tags': ['test'],
    }


@pytest.fixture
def sample_library_element():
    return {
        'id': 1,
        'uid': 'lib-elem-uid-1',
        'orgId': 1,
        'folderId': 1,
        'name': 'Test Panel',
        'kind': 1,
        'type': 'timeseries',
        'description': '',
        'model': {'type': 'timeseries'},
        'version': 1,
        'meta': {
            'folderUid': 'folder-uid-1',
            'folderName': 'Test Folder',
        },
    }


@pytest.fixture
def sample_alert_rule():
    return {
        'id': 1,
        'uid': 'alert-rule-uid-1',
        'orgID': 1,
        'folderUID': 'folder-uid-1',
        'ruleGroup': 'test-group',
        'title': 'Test Alert Rule',
        'condition': 'A',
        'data': [],
        'noDataState': 'NoData',
        'execErrState': 'Error',
    }


@pytest.fixture
def sample_contact_point():
    return {
        'uid': 'cp-uid-1',
        'name': 'Test Contact Point',
        'type': 'email',
        'settings': {'addresses': 'test@example.com'},
    }


@pytest.fixture
def sample_notification_policy():
    return {
        'receiver': 'grafana-default-email',
        'group_by': ['grafana_folder', 'alertname'],
        'routes': [],
    }

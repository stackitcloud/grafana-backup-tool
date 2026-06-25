"""Test grafanaSettings module."""

import json
import os

import pytest

from grafana_backup import grafanaSettings

pytest_plugins = [
    'grafana_backup.test.fixtures.fixtures',
]


@pytest.fixture
def config_file(tmp_path):
    config_data = {
        'grafana': {
            'url': 'http://localhost:3000',
            'token': 'test-token',
            'search_api_limit': 5000,
            'default_user_password': '00000000',
            'version': '10.0.0',
            'admin_account': 'admin',
            'admin_password': 'admin',
        },
        'general': {
            'debug': False,
            'api_health_check': True,
            'api_auth_check': True,
            'verify_ssl': False,
            'client_cert': None,
            'backup_dir': '_OUTPUT_',
            'backup_file_format': '%Y%m%d%H%M',
            'uid_dashboard_slug_suffix': False,
            'pretty_print': False,
        },
        'aws': {
            's3_bucket_name': '',
            's3_bucket_key': '',
            'default_region': '',
            'access_key_id': '',
            'secret_access_key': '',
            'endpoint_url': None,
        },
        'azure': {'container_name': '', 'connection_string': ''},
        'gcp': {'gcs_bucket_name': '', 'gcs_bucket_path': '', 'google_application_credentials': ''},
        'influxdb': {
            'measurement': 'grafana_backup',
            'host': '',
            'port': 8086,
            'username': '',
            'password': '',
            'database': '',
        },
    }
    config_path = os.path.join(str(tmp_path), 'grafanaSettings.json')
    with open(config_path, 'w') as f:
        json.dump(config_data, f)
    return config_path


def test_main_loads_config(config_file):
    settings = grafanaSettings.main(config_file)
    assert settings['GRAFANA_URL'] == 'http://localhost:3000'
    assert settings['TOKEN'] == 'test-token'
    assert settings['SEARCH_API_LIMIT'] == 5000


@pytest.mark.parametrize(
    ('env_var', 'env_value', 'setting_key', 'expected'),
    [
        ('GRAFANA_URL', 'http://override:3000', 'GRAFANA_URL', 'http://override:3000'),
        ('GRAFANA_TOKEN', 'override-token', 'TOKEN', 'override-token'),
        ('VERIFY_SSL', 'true', 'VERIFY_SSL', True),
        ('DEBUG', 'true', 'DEBUG', True),
        ('PRETTY_PRINT', 'true', 'PRETTY_PRINT', True),
        ('AWS_S3_BUCKET_NAME', 'my-bucket', 'AWS_S3_BUCKET_NAME', 'my-bucket'),
        ('AWS_DEFAULT_REGION', 'us-east-1', 'AWS_DEFAULT_REGION', 'us-east-1'),
        ('AZURE_STORAGE_CONTAINER_NAME', 'my-container', 'AZURE_STORAGE_CONTAINER_NAME', 'my-container'),
        ('GCS_BUCKET_NAME', 'my-gcs-bucket', 'GCS_BUCKET_NAME', 'my-gcs-bucket'),
        ('INFLUXDB_HOST', 'influx.example.com', 'INFLUXDB_HOST', 'influx.example.com'),
    ],
)
def test_main_env_overrides(config_file, monkeypatch, env_var, env_value, setting_key, expected):
    monkeypatch.setenv(env_var, env_value)
    settings = grafanaSettings.main(config_file)
    assert settings[setting_key] == expected


def test_main_influxdb_port_override(config_file, monkeypatch):
    monkeypatch.setenv('INFLUXDB_PORT', '9999')
    settings = grafanaSettings.main(config_file)
    assert settings['INFLUXDB_PORT'] == 9999


def test_main_token_sets_bearer_headers(config_file):
    settings = grafanaSettings.main(config_file)
    assert settings['HTTP_GET_HEADERS'] == {'Authorization': 'Bearer test-token'}
    assert settings['HTTP_POST_HEADERS'] == {
        'Authorization': 'Bearer test-token',
        'Content-Type': 'application/json',
    }


def test_main_no_token_sets_empty_get_headers(config_file, monkeypatch):
    monkeypatch.setenv('GRAFANA_TOKEN', '')
    settings = grafanaSettings.main(config_file)
    assert settings['HTTP_GET_HEADERS'] == {}
    assert settings['HTTP_POST_HEADERS'] == {'Content-Type': 'application/json'}


def test_main_basic_auth_generated(config_file):
    settings = grafanaSettings.main(config_file)
    assert settings['HTTP_GET_HEADERS_BASIC_AUTH'] is not None
    assert settings['HTTP_POST_HEADERS_BASIC_AUTH'] is not None
    assert 'Basic' in settings['HTTP_GET_HEADERS_BASIC_AUTH']['Authorization']


def test_main_basic_auth_not_generated_without_credentials(config_file, monkeypatch):
    monkeypatch.setenv('GRAFANA_ADMIN_ACCOUNT', '')
    monkeypatch.setenv('GRAFANA_ADMIN_PASSWORD', '')
    settings = grafanaSettings.main(config_file)
    assert settings['HTTP_GET_HEADERS_BASIC_AUTH'] is None
    assert settings['HTTP_POST_HEADERS_BASIC_AUTH'] is None


def test_main_extra_headers(config_file, monkeypatch):
    monkeypatch.setenv('GRAFANA_HEADERS', 'X-Custom:value1,X-Other:value2')
    settings = grafanaSettings.main(config_file)
    assert settings['HTTP_GET_HEADERS'].get('X-Custom') == 'value1'
    assert settings['HTTP_POST_HEADERS'].get('X-Other') == 'value2'


def test_main_timestamp_format(config_file):
    settings = grafanaSettings.main(config_file)
    assert len(settings['TIMESTAMP']) > 0


@pytest.mark.parametrize(
    'key',
    [
        'GRAFANA_URL',
        'GRAFANA_VERSION',
        'TOKEN',
        'SEARCH_API_LIMIT',
        'DEBUG',
        'VERIFY_SSL',
        'BACKUP_DIR',
        'TIMESTAMP',
        'HTTP_GET_HEADERS',
        'HTTP_POST_HEADERS',
    ],
)
def test_main_config_dict_keys(config_file, key):
    settings = grafanaSettings.main(config_file)
    assert key in settings

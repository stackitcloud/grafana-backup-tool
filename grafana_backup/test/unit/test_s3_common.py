"""Test s3_common module."""

import boto3
import pytest

from grafana_backup import s3_common

pytest_plugins = [
    'grafana_backup.test.fixtures.fixtures',
]


@pytest.mark.parametrize(
    ('access_key', 'secret_key', 'region'),
    [
        ('AKIAIOSFODNN7EXAMPLE', 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY', 'us-east-1'),
        ('AKIAIOSFODNN7EXAMPLE', 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY', 'eu-west-1'),
    ],
)
def test_get_boto_session_with_credentials(access_key, secret_key, region):
    settings = {
        'AWS_DEFAULT_REGION': region,
        'AWS_ACCESS_KEY_ID': access_key,
        'AWS_SECRET_ACCESS_KEY': secret_key,
    }
    session = s3_common.get_boto_session(settings)
    assert isinstance(session, boto3.Session)
    assert session.region_name == region


def test_get_boto_session_without_credentials():
    settings = {
        'AWS_DEFAULT_REGION': 'eu-west-1',
        'AWS_ACCESS_KEY_ID': None,
        'AWS_SECRET_ACCESS_KEY': None,
    }
    session = s3_common.get_boto_session(settings)
    assert isinstance(session, boto3.Session)
    assert session.region_name == 'eu-west-1'


@pytest.mark.parametrize(
    ('endpoint_url',),
    [
        (None,),
        ('http://localhost:9000',),
    ],
)
def test_get_s3_resource(endpoint_url):
    settings = {
        'AWS_DEFAULT_REGION': 'us-east-1',
        'AWS_ACCESS_KEY_ID': 'AKIAIOSFODNN7EXAMPLE',
        'AWS_SECRET_ACCESS_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
        'AWS_ENDPOINT_URL': endpoint_url,
    }
    s3 = s3_common.get_s3_resource(settings)
    assert s3 is not None


@pytest.mark.parametrize(
    ('bucket_key', 'file_name', 'expected_key'),
    [
        ('backups', 'backup.tar.gz', 'backups/backup.tar.gz'),
        ('', 'backup.tar.gz', '/backup.tar.gz'),
        ('deep/nested/path', 'archive.tar.gz', 'deep/nested/path/archive.tar.gz'),
    ],
)
def test_get_s3_object(bucket_key, file_name, expected_key):
    settings = {
        'AWS_DEFAULT_REGION': 'us-east-1',
        'AWS_ACCESS_KEY_ID': 'AKIAIOSFODNN7EXAMPLE',
        'AWS_SECRET_ACCESS_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
        'AWS_ENDPOINT_URL': None,
        'AWS_S3_BUCKET_NAME': 'test-bucket',
        'AWS_S3_BUCKET_KEY': bucket_key,
    }
    s3_obj = s3_common.get_s3_object(settings, file_name)
    assert s3_obj is not None
    assert s3_obj.key == expected_key

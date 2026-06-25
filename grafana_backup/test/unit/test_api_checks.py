"""Test api_checks module."""

import pytest

from grafana_backup import api_checks

pytest_plugins = [
    'grafana_backup.test.fixtures.fixtures',
]


def test_api_checks_all_passing(mocker, default_settings):
    mocker.patch('grafana_backup.api_checks.health_check', return_value=(200, {'status': 'ok'}))
    mocker.patch('grafana_backup.api_checks.auth_check', return_value=(200, {'orgId': 1}))
    mocker.patch('grafana_backup.api_checks.uid_feature_check', return_value=(True, True))
    mocker.patch('grafana_backup.api_checks.paging_feature_check', return_value=True)
    mocker.patch('grafana_backup.api_checks.contact_point_check', return_value=True)

    result = api_checks.main(default_settings)

    assert result[0] == 200
    assert result[2] is True
    assert result[3] is True
    assert result[4] is True
    assert result[5] is True


@pytest.mark.parametrize(
    ('check_func', 'check_key', 'return_value', 'expected_status'),
    [
        ('health_check', 'API_HEALTH_CHECK', (503, {'status': 'error'}), 503),
        ('auth_check', 'API_AUTH_CHECK', (401, {'message': 'unauthorized'}), 401),
    ],
)
def test_api_checks_failure_returns_early(
    mocker, default_settings, check_func, check_key, return_value, expected_status
):
    if check_func == 'health_check':
        mocker.patch('grafana_backup.api_checks.health_check', return_value=return_value)
    else:
        mocker.patch('grafana_backup.api_checks.health_check', return_value=(200, {'status': 'ok'}))
        mocker.patch(f'grafana_backup.api_checks.{check_func}', return_value=return_value)

    result = api_checks.main(default_settings)
    assert result[0] == expected_status
    assert len(result) == 5


def test_api_checks_uid_feature_check_raises(mocker, default_settings):
    mocker.patch('grafana_backup.api_checks.health_check', return_value=(200, {'status': 'ok'}))
    mocker.patch('grafana_backup.api_checks.auth_check', return_value=(200, {'orgId': 1}))
    mocker.patch(
        'grafana_backup.api_checks.uid_feature_check',
        return_value=('get dashboards failed, status: 500, msg: error', True),
    )
    with pytest.raises(Exception, match='get dashboards failed'):
        api_checks.main(default_settings)


def test_api_checks_paging_feature_check_raises(mocker, default_settings):
    mocker.patch('grafana_backup.api_checks.health_check', return_value=(200, {'status': 'ok'}))
    mocker.patch('grafana_backup.api_checks.auth_check', return_value=(200, {'orgId': 1}))
    mocker.patch('grafana_backup.api_checks.uid_feature_check', return_value=(True, True))
    mocker.patch(
        'grafana_backup.api_checks.paging_feature_check',
        return_value='get dashboards failed, status: 500, msg: error',
    )
    with pytest.raises(Exception, match='get dashboards failed'):
        api_checks.main(default_settings)


@pytest.mark.parametrize(
    ('setting_key', 'check_func'),
    [
        ('API_HEALTH_CHECK', 'health_check'),
        ('API_AUTH_CHECK', 'auth_check'),
    ],
)
def test_api_checks_skips_disabled_checks(mocker, default_settings, setting_key, check_func):
    default_settings[setting_key] = False
    mock_check = mocker.patch(f'grafana_backup.api_checks.{check_func}')
    mocker.patch('grafana_backup.api_checks.health_check', return_value=(200, {'status': 'ok'}))
    mocker.patch('grafana_backup.api_checks.auth_check', return_value=(200, {'orgId': 1}))
    mocker.patch('grafana_backup.api_checks.uid_feature_check', return_value=(True, True))
    mocker.patch('grafana_backup.api_checks.paging_feature_check', return_value=True)
    mocker.patch('grafana_backup.api_checks.contact_point_check', return_value=True)

    api_checks.main(default_settings)
    mock_check.assert_not_called()


@pytest.mark.parametrize(
    ('contact_point_return', 'expected'),
    [
        (True, True),
        (False, False),
    ],
)
def test_api_checks_contact_point_availability(mocker, default_settings, contact_point_return, expected):
    mocker.patch('grafana_backup.api_checks.health_check', return_value=(200, {'status': 'ok'}))
    mocker.patch('grafana_backup.api_checks.auth_check', return_value=(200, {'orgId': 1}))
    mocker.patch('grafana_backup.api_checks.uid_feature_check', return_value=(True, True))
    mocker.patch('grafana_backup.api_checks.paging_feature_check', return_value=True)
    mocker.patch('grafana_backup.api_checks.contact_point_check', return_value=contact_point_return)

    result = api_checks.main(default_settings)
    assert result[5] is expected

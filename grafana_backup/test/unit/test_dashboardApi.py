"""Test dashboardApi module."""

import pytest

from grafana_backup import dashboardApi

pytest_plugins = [
    'grafana_backup.test.fixtures.fixtures',
]


@pytest.fixture
def api_args():
    return {
        'grafana_url': 'http://localhost:3000',
        'http_get_headers': {'Authorization': 'Bearer test-token'},
        'http_post_headers': {'Authorization': 'Bearer test-token', 'Content-Type': 'application/json'},
        'verify_ssl': False,
        'client_cert': None,
        'debug': False,
    }


def test_health_check(mocker, api_args):
    mocker.patch('grafana_backup.dashboardApi.send_grafana_get', return_value=(200, {'status': 'ok'}))
    status, content = dashboardApi.health_check(
        api_args['grafana_url'],
        api_args['http_get_headers'],
        api_args['verify_ssl'],
        api_args['client_cert'],
        api_args['debug'],
    )
    assert status == 200
    assert content == {'status': 'ok'}


def test_auth_check(mocker, api_args):
    mocker.patch('grafana_backup.dashboardApi.send_grafana_get', return_value=(200, {'orgId': 1}))
    status, content = dashboardApi.auth_check(
        api_args['grafana_url'],
        api_args['http_get_headers'],
        api_args['verify_ssl'],
        api_args['client_cert'],
        api_args['debug'],
    )
    assert status == 200


@pytest.mark.parametrize(
    ('func_name', 'api_func', 'extra_args', 'expected_url_fragment'),
    [
        ('search_dashboard', dashboardApi.search_dashboard, (1, 5000), '/api/search/'),
        ('search_datasource', dashboardApi.search_datasource, (), '/api/datasources'),
        ('search_folders', dashboardApi.search_folders, (), '/api/search/'),
        ('search_alert_channels', dashboardApi.search_alert_channels, (), '/api/alert-notifications'),
        ('search_teams', dashboardApi.search_teams, (), '/api/teams/search'),
        ('search_orgs', dashboardApi.search_orgs, (), '/api/orgs'),
        ('search_users', dashboardApi.search_users, (1, 5000), '/api/users'),
        ('search_contact_points', dashboardApi.search_contact_points, (), '/api/v1/provisioning/contact-points'),
        ('search_alert_rules', dashboardApi.search_alert_rules, (), '/api/v1/provisioning/alert-rules'),
        ('search_library_elements', dashboardApi.search_library_elements, (), '/api/library-elements'),
        ('search_snapshot', dashboardApi.search_snapshot, (), '/api/dashboard/snapshots'),
    ],
)
def test_search_endpoints(mocker, api_args, func_name, api_func, extra_args, expected_url_fragment):
    mock_get = mocker.patch('grafana_backup.dashboardApi.send_grafana_get', return_value=(200, []))
    api_func(
        *extra_args,
        api_args['grafana_url'],
        api_args['http_get_headers'],
        api_args['verify_ssl'],
        api_args['client_cert'],
        api_args['debug'],
    )
    mock_get.assert_called_once()
    call_url = mock_get.call_args[0][0]
    assert expected_url_fragment in call_url


@pytest.mark.parametrize(
    ('api_func', 'extra_args'),
    [
        (dashboardApi.get_dashboard, ('uid/abc123',)),
        (dashboardApi.get_folder, ('folder-uid-1',)),
        (dashboardApi.get_folder_permissions, ('folder-uid-1',)),
        (dashboardApi.get_org, (1,)),
        (dashboardApi.get_user, (1,)),
        (dashboardApi.get_alert_rule, ('alert-rule-uid-1',)),
        (dashboardApi.get_snapshot, ('snapshot-key-1',)),
        (dashboardApi.get_user_org, (1,)),
        (dashboardApi.search_team_members, (1,)),
        (dashboardApi.get_dashboard_versions, (1,)),
        (dashboardApi.get_version, (1, 1)),
    ],
)
def test_get_endpoints(mocker, api_args, api_func, extra_args):
    mocker.patch('grafana_backup.dashboardApi.send_grafana_get', return_value=(200, {}))
    status, content = api_func(
        *extra_args,
        api_args['grafana_url'],
        api_args['http_get_headers'],
        api_args['verify_ssl'],
        api_args['client_cert'],
        api_args['debug'],
    )
    assert status == 200


@pytest.mark.parametrize(
    ('api_func', 'payload'),
    [
        (dashboardApi.create_dashboard, '{"dashboard": {}}'),
        (dashboardApi.create_datasource, '{"name": "test"}'),
        (dashboardApi.create_folder, '{"title": "New Folder"}'),
        (dashboardApi.create_alert_channel, '{"name": "test"}'),
        (dashboardApi.create_library_element, '{"name": "test"}'),
        (dashboardApi.create_team, '{"name": "test"}'),
        (dashboardApi.create_org, '{"name": "test"}'),
        (dashboardApi.create_user, '{"login": "test"}'),
        (dashboardApi.create_snapshot, '{"dashboard": {}}'),
        (dashboardApi.create_contact_point, '{"name": "test"}'),
        (dashboardApi.create_annotation, '{"text": "test"}'),
    ],
)
def test_create_endpoints(mocker, api_args, api_func, payload):
    mocker.patch('grafana_backup.dashboardApi.send_grafana_post', return_value=(200, {'id': 1}))
    result = api_func(
        payload,
        api_args['grafana_url'],
        api_args['http_post_headers'],
        api_args['verify_ssl'],
        api_args['client_cert'],
        api_args['debug'],
    )
    assert result[0] == 200


@pytest.mark.parametrize(
    ('api_func', 'extra_args'),
    [
        (dashboardApi.delete_dashboard_by_uid, ('abc123',)),
        (dashboardApi.delete_dashboard_by_slug, ('test-slug',)),
        (dashboardApi.delete_datasource_by_uid, ('ds-uid-1',)),
        (dashboardApi.delete_datasource_by_id, (1,)),
        (dashboardApi.delete_folder, ('folder-uid-1',)),
        (dashboardApi.delete_team, (1,)),
        (dashboardApi.delete_library_element, ('lib-uid-1',)),
        (dashboardApi.delete_snapshot, ('snap-key-1',)),
        (dashboardApi.delete_alert_rule, ('alert-uid-1',)),
        (dashboardApi.delete_annotation, (1,)),
        (dashboardApi.delete_team_member, (1, 1)),
    ],
)
def test_delete_endpoints(mocker, api_args, api_func, extra_args):
    mocker.patch('grafana_backup.dashboardApi.send_grafana_delete', return_value=200)
    result = api_func(
        *extra_args,
        api_args['grafana_url'],
        api_args['http_post_headers'],
        api_args['verify_ssl'],
        api_args['client_cert'],
        api_args['debug'],
    )
    assert result == 200


def test_get_folder_id_with_folder_uid(mocker, api_args, sample_dashboard_full):
    mocker.patch('grafana_backup.dashboardApi.get_folder', return_value=(200, {'id': 5, 'uid': 'folder-uid-1'}))
    result = dashboardApi.get_folder_id(
        sample_dashboard_full,
        api_args['grafana_url'],
        api_args['http_post_headers'],
        api_args['verify_ssl'],
        api_args['client_cert'],
        api_args['debug'],
    )
    assert result == 5


def test_get_folder_id_with_folder_url_fallback(mocker, api_args):
    dashboard = {
        'meta': {'folderUrl': '/dashboards/f/fallback-uid/test-folder'},
        'dashboard': {'title': 'Test'},
    }
    mocker.patch('grafana_backup.dashboardApi.get_folder', return_value=(200, {'id': 10, 'uid': 'fallback-uid'}))
    result = dashboardApi.get_folder_id(
        dashboard,
        api_args['grafana_url'],
        api_args['http_post_headers'],
        api_args['verify_ssl'],
        api_args['client_cert'],
        api_args['debug'],
    )
    assert result == 10


def test_get_folder_id_no_folder(mocker, api_args):
    dashboard = {
        'meta': {'folderUrl': ''},
        'dashboard': {'title': 'Test'},
    }
    mocker.patch('grafana_backup.dashboardApi.get_folder', return_value=(200, {'id': 0, 'uid': '0'}))
    result = dashboardApi.get_folder_id(
        dashboard,
        api_args['grafana_url'],
        api_args['http_post_headers'],
        api_args['verify_ssl'],
        api_args['client_cert'],
        api_args['debug'],
    )
    assert result == 0


def test_get_folder_id_key_error_returns_zero(mocker, api_args):
    mocker.patch('grafana_backup.dashboardApi.get_folder', return_value=(200, {'uid': 'folder-uid-1'}))
    dashboard = {
        'meta': {'folderUid': 'folder-uid-1'},
        'dashboard': {'title': 'Test'},
    }
    result = dashboardApi.get_folder_id(
        dashboard,
        api_args['grafana_url'],
        api_args['http_post_headers'],
        api_args['verify_ssl'],
        api_args['client_cert'],
        api_args['debug'],
    )
    assert result == 0


@pytest.mark.parametrize(
    ('search_dashboard_return', 'search_datasource_return', 'expected_dash_uid', 'expected_ds_uid'),
    [
        ((200, [{'uid': 'abc', 'title': 'T'}]), (200, [{'uid': 'ds1', 'name': 'T'}]), True, True),
        ((200, [{'id': 1, 'title': 'T'}]), (200, [{'id': 1, 'name': 'T'}]), False, False),
        ((200, []), (200, [{'uid': 'ds1'}]), False, True),
        ((200, [{'uid': 'abc'}]), (200, []), True, False),
    ],
)
def test_uid_feature_check(
    mocker, api_args, search_dashboard_return, search_datasource_return, expected_dash_uid, expected_ds_uid
):
    mocker.patch('grafana_backup.dashboardApi.search_dashboard', return_value=search_dashboard_return)
    mocker.patch('grafana_backup.dashboardApi.search_datasource', return_value=search_datasource_return)
    dash_uid, ds_uid = dashboardApi.uid_feature_check(
        api_args['grafana_url'],
        api_args['http_get_headers'],
        api_args['verify_ssl'],
        api_args['client_cert'],
        api_args['debug'],
    )
    assert dash_uid is expected_dash_uid
    assert ds_uid is expected_ds_uid


def test_paging_feature_check_supported(mocker, api_args):
    def side_effect(page, limit, *args, **kwargs):
        if page == 1:
            return (200, [{'uid': 'a', 'title': 'Dashboard A'}])
        return (200, [{'uid': 'b', 'title': 'Dashboard B'}])

    mocker.patch('grafana_backup.dashboardApi.search_dashboard', side_effect=side_effect)
    assert (
        dashboardApi.paging_feature_check(
            api_args['grafana_url'],
            api_args['http_get_headers'],
            api_args['verify_ssl'],
            api_args['client_cert'],
            api_args['debug'],
        )
        is True
    )


def test_paging_feature_check_not_supported(mocker, api_args):
    mocker.patch('grafana_backup.dashboardApi.search_dashboard', return_value=(200, []))
    assert (
        dashboardApi.paging_feature_check(
            api_args['grafana_url'],
            api_args['http_get_headers'],
            api_args['verify_ssl'],
            api_args['client_cert'],
            api_args['debug'],
        )
        is False
    )


@pytest.mark.parametrize(
    ('search_return', 'expected'),
    [
        ((200, [{'uid': 'cp-1'}]), True),
        ((404, 'not found'), False),
        ((500, 'error'), False),
    ],
)
def test_contact_point_check(mocker, api_args, search_return, expected):
    mocker.patch('grafana_backup.dashboardApi.search_contact_points', return_value=search_return)
    result = dashboardApi.contact_point_check(
        api_args['grafana_url'],
        api_args['http_get_headers'],
        api_args['verify_ssl'],
        api_args['client_cert'],
        api_args['debug'],
    )
    assert result is expected


@pytest.mark.parametrize(
    ('status', 'response_json', 'expected_version'),
    [
        (200, {'version': '10.2.3'}, '10.2.3'),
        (200, {'version': '9.4.0+security-0'}, '9.4.0'),
    ],
)
def test_get_grafana_version(mocker, api_args, status, response_json, expected_version):
    mock_response = mocker.Mock()
    mock_response.status_code = status
    mock_response.json.return_value = response_json
    mocker.patch('requests.get', return_value=mock_response)
    result = dashboardApi.get_grafana_version(
        api_args['grafana_url'], api_args['verify_ssl'], api_args['http_get_headers']
    )
    assert str(result) == expected_version


def test_get_grafana_version_no_version_key(mocker, api_args):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'commit': 'abc123'}
    mocker.patch('requests.get', return_value=mock_response)
    with pytest.raises(KeyError, match='Unable to get version'):
        dashboardApi.get_grafana_version(api_args['grafana_url'], api_args['verify_ssl'], api_args['http_get_headers'])


def test_get_grafana_version_bad_status(mocker, api_args):
    mock_response = mocker.Mock()
    mock_response.status_code = 500
    mocker.patch('requests.get', return_value=mock_response)
    with pytest.raises(Exception, match='Unable to get version'):
        dashboardApi.get_grafana_version(api_args['grafana_url'], api_args['verify_ssl'], api_args['http_get_headers'])


@pytest.mark.parametrize(
    ('http_func', 'request_func', 'expected_status'),
    [
        (dashboardApi.send_grafana_get, 'requests.get', 200),
        (dashboardApi.send_grafana_delete, 'requests.delete', 200),
    ],
)
def test_send_grafana_http_methods(mocker, api_args, http_func, request_func, expected_status):
    mock_response = mocker.Mock()
    mock_response.status_code = expected_status
    mock_response.json.return_value = {'result': 'ok'}
    mocker.patch(request_func, return_value=mock_response)

    if http_func == dashboardApi.send_grafana_delete:
        result = http_func(
            'http://localhost:3000/api/test',
            api_args['http_get_headers'],
            api_args['verify_ssl'],
            api_args['client_cert'],
            api_args['debug'],
        )
    else:
        result = http_func(
            'http://localhost:3000/api/test',
            api_args['http_get_headers'],
            api_args['verify_ssl'],
            api_args['client_cert'],
            api_args['debug'],
        )
    assert result[0] == expected_status if isinstance(result, tuple) else result == expected_status


def test_send_grafana_post(mocker, api_args):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'id': 1}
    mocker.patch('requests.post', return_value=mock_response)
    status, content = dashboardApi.send_grafana_post(
        'http://localhost:3000/api/dashboards/db',
        '{}',
        api_args['http_post_headers'],
        api_args['verify_ssl'],
        api_args['client_cert'],
        api_args['debug'],
    )
    assert status == 200
    assert content == {'id': 1}


def test_send_grafana_post_non_json_response(mocker, api_args):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError('no json')
    mock_response.text = 'OK'
    mocker.patch('requests.post', return_value=mock_response)
    status, content = dashboardApi.send_grafana_post(
        'http://localhost:3000/api/test',
        '{}',
        api_args['http_post_headers'],
        api_args['verify_ssl'],
        api_args['client_cert'],
        api_args['debug'],
    )
    assert status == 200
    assert content == 'OK'


def test_send_grafana_put(mocker, api_args):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'result': 'updated'}
    mocker.patch('requests.put', return_value=mock_response)
    status, content = dashboardApi.send_grafana_put(
        'http://localhost:3000/api/test',
        '{}',
        api_args['http_post_headers'],
        api_args['verify_ssl'],
        api_args['client_cert'],
        api_args['debug'],
    )
    assert status == 200
    assert content == {'result': 'updated'}


def test_update_folder_permissions(mocker, api_args):
    mocker.patch('grafana_backup.dashboardApi.send_grafana_post', return_value=(200, {'status': 'ok'}))
    result = dashboardApi.update_folder_permissions(
        [{'uid': 'folder-uid-1', 'items': []}],
        api_args['grafana_url'],
        api_args['http_post_headers'],
        api_args['verify_ssl'],
        api_args['client_cert'],
        api_args['debug'],
    )
    assert result[0] == 200


def test_search_notification_policies(mocker, api_args):
    mocker.patch(
        'grafana_backup.dashboardApi.send_grafana_get',
        return_value=(200, {'receiver': 'default', 'group_by': []}),
    )
    status, content = dashboardApi.search_notification_policies(
        api_args['grafana_url'],
        api_args['http_get_headers'],
        api_args['verify_ssl'],
        api_args['client_cert'],
        api_args['debug'],
    )
    assert status == 200
    assert 'receiver' in content


def test_set_user_role(mocker, api_args):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'message': 'role updated'}
    mocker.patch('requests.patch', return_value=mock_response)
    status, content = dashboardApi.set_user_role(
        1,
        'Viewer',
        api_args['grafana_url'],
        api_args['http_post_headers'],
        api_args['verify_ssl'],
        api_args['client_cert'],
        api_args['debug'],
    )
    assert status == 200

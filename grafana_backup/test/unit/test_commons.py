"""Test commons module."""

import json
import os

import pytest

from grafana_backup import commons

pytest_plugins = [
    'grafana_backup.test.fixtures.fixtures',
]


def test_print_horizontal_line(capsys):
    commons.print_horizontal_line()
    captured = capsys.readouterr()
    assert '########################################' in captured.out


def test_to_python2_and_3_compatible_string_py3():
    assert commons.to_python2_and_3_compatible_string('hello') == 'hello'


@pytest.mark.parametrize(
    ('file_name', 'data', 'extension', 'pretty_print', 'expected_in_content'),
    [
        ('test_file', {'key': 'value'}, 'json', False, '{"key": "value"}'),
        ('test_file', {'key': 'value'}, 'json', True, '    '),
        ('test_file', {'a': 1, 'b': 2}, 'json', False, '"a": 1'),
    ],
)
def test_save_json_content(tmp_path, file_name, data, extension, pretty_print, expected_in_content):
    result = commons.save_json(file_name, data, str(tmp_path), extension, pretty_print)
    assert os.path.exists(result)
    with open(result) as f:
        content = f.read()
    assert expected_in_content in content


@pytest.mark.parametrize(
    ('file_name', 'should_strip'),
    [
        ('db/test_file', True),
        ('uid/test_file', True),
        ('plain_file', False),
    ],
)
def test_save_json_prefix_handling(tmp_path, file_name, should_strip):
    result = commons.save_json(file_name, {'key': 'value'}, str(tmp_path), 'json', False)
    basename = os.path.basename(result)
    if should_strip:
        assert not basename.startswith(('db', 'uid'))
    else:
        assert file_name.split('/')[-1] in basename


def test_save_json_returns_file_path(tmp_path):
    result = commons.save_json('test_file', {'key': 'value'}, str(tmp_path), 'json', False)
    assert result.endswith('test_file.json')


def test_load_config_valid(tmp_path):
    config_data = {'grafana': {'url': 'http://localhost:3000'}, 'general': {'debug': True}}
    config_file = os.path.join(str(tmp_path), 'config.json')
    with open(config_file, 'w') as f:
        json.dump(config_data, f)
    assert commons.load_config(config_file) == config_data


def test_load_config_missing_file(capsys):
    with pytest.raises(SystemExit):
        commons.load_config('/nonexistent/path/config.json')


@pytest.mark.parametrize(
    ('status_code', 'json_side_effect', 'text', 'expected_status'),
    [
        (200, {'status': 'ok'}, '', '200'),
        (500, ValueError('no json'), 'Internal Server Error', '500'),
    ],
)
def test_log_response(capsys, mocker, status_code, json_side_effect, text, expected_status):
    mock_resp = mocker.Mock()
    mock_resp.status_code = status_code
    if isinstance(json_side_effect, Exception):
        mock_resp.json.side_effect = json_side_effect
        mock_resp.text = text
    else:
        mock_resp.json.return_value = json_side_effect

    result = commons.log_response(mock_resp)
    assert result == mock_resp
    captured = capsys.readouterr()
    assert expected_status in captured.out

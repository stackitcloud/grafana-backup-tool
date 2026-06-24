"""Test create_library_element module."""

import json
import os

import pytest

from grafana_backup import create_library_element

pytest_plugins = [
    'grafana_backup.test.fixtures.fixtures',
]


@pytest.fixture
def library_element_file(tmp_path, sample_library_element):
    file_path = os.path.join(str(tmp_path), 'library_element.json')
    with open(file_path, 'w') as f:
        json.dump(sample_library_element, f)
    return file_path


def test_create_library_element_resolves_folder_uid_dict_response(
    mocker, default_settings, library_element_file, sample_library_element
):
    mocker.patch(
        'grafana_backup.create_library_element.get_folder',
        return_value=(200, {'uid': 'resolved-uid', 'id': 1})
    )
    mock_create = mocker.patch(
        'grafana_backup.create_library_element.create_library_element',
        return_value=(200, {'id': 1})
    )
    
    create_library_element.main({}, default_settings, library_element_file)
    
    call_args = mock_create.call_args[0]
    element_data = json.loads(call_args[0])
    assert element_data['folderUid'] == 'resolved-uid'


def test_create_library_element_resolves_folder_uid_list_response(
    mocker, default_settings, library_element_file, sample_library_element
):
    mocker.patch(
        'grafana_backup.create_library_element.get_folder',
        return_value=(200, [{'uid': 'resolved-uid', 'id': 1}])
    )
    mock_create = mocker.patch(
        'grafana_backup.create_library_element.create_library_element',
        return_value=(200, {'id': 1})
    )
    
    create_library_element.main({}, default_settings, library_element_file)
    
    call_args = mock_create.call_args[0]
    element_data = json.loads(call_args[0])
    assert element_data['folderUid'] == 'resolved-uid'


def test_create_library_element_calls_get_folder_with_correct_uid(
    mocker, default_settings, library_element_file, sample_library_element
):
    mock_get_folder = mocker.patch(
        'grafana_backup.create_library_element.get_folder',
        return_value=(200, {'uid': 'resolved-uid'})
    )
    mocker.patch('grafana_backup.create_library_element.create_library_element', return_value=(200, {'id': 1}))
    
    create_library_element.main({}, default_settings, library_element_file)
    
    mock_get_folder.assert_called_once()
    call_args = mock_get_folder.call_args[0]
    assert call_args[0] == sample_library_element['meta']['folderUid']


def test_create_library_element_preserves_element_data(
    mocker, default_settings, library_element_file, sample_library_element
):
    mocker.patch(
        'grafana_backup.create_library_element.get_folder',
        return_value=(200, {'uid': 'resolved-uid'})
    )
    mock_create = mocker.patch(
        'grafana_backup.create_library_element.create_library_element',
        return_value=(200, {'id': 1})
    )
    
    create_library_element.main({}, default_settings, library_element_file)
    
    call_args = mock_create.call_args[0]
    element_data = json.loads(call_args[0])
    assert element_data['name'] == sample_library_element['name']
    assert element_data['type'] == sample_library_element['type']
    assert element_data['kind'] == sample_library_element['kind']


def test_create_library_element_empty_folder_response(mocker, default_settings, library_element_file):
    mocker.patch(
        'grafana_backup.create_library_element.get_folder',
        return_value=(200, [])
    )
    mocker.patch(
        'grafana_backup.create_library_element.create_library_element',
        return_value=(200, {'id': 1})
    )
    
    with pytest.raises(IndexError):
        create_library_element.main({}, default_settings, library_element_file)

import os

os.environ['API_TOKEN'] = 'API_TOKEN'
os.environ['GROUP_ID'] = 'GROUP_ID'
os.environ['GROUP_NAME'] = 'test-G_Name'
os.environ['JUPYTERHUB_USER'] = 'JUPYTERHUB_USER'
os.environ['INSTANCE_TYPE'] = 'INSTANCE_TYPE'
os.environ['IMAGE_NAME'] = 'IMAGE_NAME'

import pytest
from unittest.mock import Mock

import primehub_job

def test__check_env_requirements():
    del os.environ['API_TOKEN']
    with pytest.raises(RuntimeError) as excinfo:
        primehub_job.from_jupyter.__check_env_requirements(primehub_job.from_jupyter.REQUIRED_ENVS)
    assert "You must set your API_TOKEN environment variable." in str(excinfo.value)
    os.environ['API_TOKEN'] = 'API_TOKEN'

def test__get_group_volume_name():
    group_volume_name = primehub_job.from_jupyter.__get_group_volume_name()
    assert "test-g-name" == group_volume_name


def test__get_phjob_user_folder_path():
    phjob_user_folder_path = primehub_job.from_jupyter.__get_phjob_user_folder_path()
    assert "/home/jovyan/test-g-name/phjobs/JUPYTERHUB_USER" == phjob_user_folder_path

def test__create_phjob_failed(mocker):
    mocker.patch('primehub_job.from_jupyter.__post_api_graphql', return_value = {
        'data': 'test'
    })
    with pytest.raises(RuntimeError) as excinfo:
        primehub_job.from_jupyter.__create_phjob('name', 'group_id', 'instance_type', 'image', 'command')
    assert "Job creation failed" in str(excinfo.value)

def test__create_phjob_succeeded(mocker):
    mock = Mock()
    mock.json.return_value = {
        'data': {
            'createPhJob': {
                'id': 'test-job-id'
            }
        }
    }
    mocker.patch('primehub_job.from_jupyter.__post_api_graphql', return_value=mock)
    job_id = primehub_job.from_jupyter.__create_phjob('name', 'group_id', 'instance_type', 'image', 'command')
    assert "test-job-id" == job_id

def test_get_phjob_failed(mocker):
    mocker.patch('primehub_job.from_jupyter.__post_api_graphql', return_value = {
        'data': 'test'
    })
    with pytest.raises(RuntimeError) as excinfo:
        primehub_job.from_jupyter.get_phjob('test-job-id')
    assert "Get job info failed" in str(excinfo.value)

def test_get_phjob_succeeded(mocker):
    mock = Mock()
    mock.json.return_value = {
        'data': {
            'phJob': {
                'id': 'test-job-id'
            }
        }
    }
    mocker.patch('primehub_job.from_jupyter.__post_api_graphql', return_value=mock)
    job_info = primehub_job.from_jupyter.get_phjob('test-job-id')
    assert "test-job-id" == job_info['id']

def test_get_phjob_folder_path():
    phjob_folder_path = primehub_job.get_phjob_folder_path("test-job-id")
    assert "/home/jovyan/test-g-name/phjobs/JUPYTERHUB_USER/test-job-id" == phjob_folder_path

def test_get_phjob_result():
    phjob_folder_path = primehub_job.get_phjob_folder_path("test-job-id")
    assert "/home/jovyan/test-g-name/phjobs/JUPYTERHUB_USER/test-job-id" == phjob_folder_path
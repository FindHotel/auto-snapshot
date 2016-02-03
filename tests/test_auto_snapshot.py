"""auto-snapshot tests creating a snapshot."""

import inspect
import os
import sys
lambda_dir = os.path.join(
    os.path.dirname(inspect.getfile(inspect.currentframe())),
    '..',
    'lambda')
sys.path.append(lambda_dir)

try:
    from unittest import mock
except ImportError:
    import mock

import pytest

from auto_snapshot import get_next_version, notify, create_snapshot


def test_get_next_version(snapshot_description):
    """Test get_next_version
    :param snapshot_description: snapshot details defined in fixtures
    :type snapshot_description: dict
    """
    # the first snapshot version should be 1
    assert get_next_version(None) == 1
    # the next snapshot version should be 2
    assert get_next_version(snapshot_description) == 2


@mock.patch('auto_snapshot.boto3.client')
def test_notify(mock_boto3_client, response_meta_data_success, response_meta_data_error):
    """Test notify
    :param mock_boto3_client: mock of aws ec2 client
    :type mock_boto3_client: MagicMock
    :param response_meta_data_success: aws http response meta data defined in fixtures
    :type response_meta_data_success: dict
    """
    arn = 'some-amazon-resource-name'
    topic_name = 'hello'

    mock_boto3_client().create_topic.return_value = dict({'TopicArn': arn}.items(), **response_meta_data_success)
    mock_boto3_client().publish.return_value = response_meta_data_success

    notify(topic_name)
    # make sure it uses the right AWS service
    mock_boto3_client.assert_called_with('sns')
    # make sure it creates the topic
    mock_boto3_client().create_topic.assert_called_once_with(Name=topic_name)
    # make sure it publish the message
    assert mock_boto3_client().publish.called
    args, kwargs = mock_boto3_client().publish.call_args
    assert kwargs['TopicArn'] == arn
    assert kwargs['Subject'] == topic_name

    mock_boto3_client().create_topic.return_value = dict({'TopicArn': arn}.items(), **response_meta_data_error)
    with pytest.raises(Exception) as message:
        notify(topic_name)
    assert 'auto-snapshot error: HTTPStatusCode' in str(message.value)


@mock.patch('auto_snapshot.get_current_snapshot')
def test_create_snapshot(get_current_snapshot_mock, volume, snapshot_description, response_meta_data_success):
    """Test create_snapshot
    :param get_current_snapshot_mock: a mock of the function get_current_snapshot
    :type get_current_snapshot_mock: MagicMock
    :param volume: an ec2 volume defined in fixtures
    :type volume: Volume
    :param snapshot_description: snapshot details defined in fixtures
    :type snapshot_description: dict
    :param response_meta_data_success: aws http response meta data defined in fixtures
    :type response_meta_data_success: dict
    """
    get_current_snapshot_mock.return_value = snapshot_description
    service_resource_mock = mock.Mock()
    service_resource_mock.create_snapshot.return_value.meta.data = response_meta_data_success
    create_snapshot(volume, service_resource_mock)
    assert service_resource_mock.create_snapshot.called
    args, kwargs = service_resource_mock.create_snapshot.call_args
    assert kwargs['VolumeId'] == volume.volume_id
    get_current_snapshot_mock.assert_called_once_with(volume.volume_id)

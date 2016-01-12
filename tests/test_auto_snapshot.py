
from unittest import TestCase, mock

from auto_snapshot import get_next_version, notify, create_snapshot


class VolumeMock:
    volume_id = 'some-vol-id'
    tags = [{'Key': 'Name', 'Value': 'some-vol-name'},
            {'Key': 'auto:snapshots:retention_days', 'Value': '2'},
            {'Key': '', 'Value': ''}]


EXAMPLE_SNAPSHOT_DESCRIPTION = {
    'Tags': [{'Key': 'auto:snapshots:version', 'Value': '1'}],
    'SnapshotId': 'some-snapshot-id'}


class AutoSnapshotTest(TestCase):

    def test_get_next_version(self):
        # the first snapshot version should be 1
        self.assertEqual(get_next_version(None), 1,
                         'The next version should be 1')
        # the next snapshot version should be 2
        self.assertEqual(get_next_version(EXAMPLE_SNAPSHOT_DESCRIPTION), 2,
                         'The next version should be 2')

    @mock.patch('auto_snapshot.boto3.client')
    def test_notify(self, mock_boto3_client):
        arn = 'some-amazon-resource-name'
        mock_boto3_client().create_topic.return_value = {'TopicArn': arn}
        topic_name = 'hello'
        notify(topic_name)
        # make sure it uses the right AWS service
        mock_boto3_client.assert_called_with('sns')
        # make sure it creates the topic
        mock_boto3_client().create_topic.assert_called_once_with(Name=topic_name)
        # make sure it publish the message
        mock_boto3_client().publish.assert_called_once()
        args, kwargs = mock_boto3_client().publish.call_args
        self.assertEqual(kwargs['TopicArn'], arn)
        self.assertEqual(kwargs['Subject'], topic_name)

    @mock.patch('auto_snapshot.get_current_snapshot', return_value=EXAMPLE_SNAPSHOT_DESCRIPTION)
    def test_create_snapshot(self, get_current_snapshot_mock):
        service_resource_mock = mock.Mock()
        volume_mock = VolumeMock()
        create_snapshot(volume_mock, service_resource_mock)
        service_resource_mock.create_snapshot.assert_called_once()
        args, kwargs = service_resource_mock.create_snapshot.call_args
        self.assertEqual(kwargs['VolumeId'], volume_mock.volume_id)
        get_current_snapshot_mock.assert_called_once_with(volume_mock.volume_id)

"""Global conftest."""
import pytest
from collections import namedtuple


Volume = namedtuple('Volume', ['volume_id', 'tags'])


@pytest.fixture
def volume():
    return \
        Volume('some-vol-id',
               [{'Key': 'Name', 'Value': 'some-vol-name'},
                {'Key': 'auto:snapshots:retention_days', 'Value': '2'},
                {'Key': '', 'Value': ''}])


@pytest.fixture
def snapshot_description():
    return {
        'Tags': [{'Key': 'auto:snapshots:version', 'Value': '1'}],
        'SnapshotId': 'some-snapshot-id'}


@pytest.fixture
def response_meta_data_success():
    return {'ResponseMetadata': {'HTTPStatusCode': 200}}


@pytest.fixture
def response_meta_data_error():
    return {'ResponseMetadata': {'HTTPStatusCode': 404}}

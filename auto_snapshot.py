"""Create snapshots for selected EBS volumes in AWS

This module includes the function for creating a snapshot for any volume that implement the tags bellow:

tag key                             tag value
---------------------------------------------------------------------------------------
*Name                                <volume name>
*auto:snapshots                      <any value>
auto:snapshot:topic                 <topic name for SNS event>
auto:snapshots:retention_days       <number of days to keep the snapshot>

*mandatory tags

Example tags:

tag key                             tag value
---------------------------------------------------------------------------------------
Name                                my-super-important-volume
auto:snapshots                      yes
auto:snapshot:topic                 snapshot-was-created-for-my-super-important-volume
auto:snapshots:retention_days       15



Module methods:

    run:
        Start the execution

"""


from __future__ import print_function

import boto3
import datetime

from utils import convert_tags_dict_to_list, convert_tags_list_to_dict
from settings import MAX_RETENTION_DAYS


def get_current_snapshot(volume_id):
    ec = boto3.client('ec2')
    filters = [
        {'Name': 'tag-key', 'Values': ["auto:snapshots:current:{}".format(volume_id)]},
        {'Name': 'tag-value', 'Values': ["true"]},
    ]
    snapshot_response = ec.describe_snapshots(Filters=filters)
    snapshots = snapshot_response.get('Snapshots')
    current_snapshot_description = None
    if snapshots and len(snapshots) == 1:
        current_snapshot_description = snapshots[0]
    elif len(snapshots) > 1:
        # Fail if there is more than one current backup so, need to be tracked via some SNS event
        raise Exception("auto-snpashot error: More than one current backup for volume id: {}".format(volume_id))
    return current_snapshot_description


def get_next_version(current_snapshot_description):
    """

    :param current_snapshot_description: A dict with the key: 'Tags' with list of tags include the version e.g:
        {'Tags': [{'Key': 'auto:snapshots:version', 'Value': '1'}]}
    :return: The version number of the next snapshot
    """
    if not current_snapshot_description:
        current_version = 0
    else:
        current_snapshot_tags = convert_tags_list_to_dict(current_snapshot_description['Tags'])
        current_version = int(current_snapshot_tags['auto:snapshots:version'])
    current_version += 1
    return current_version


def create_snapshot(volume, service_resource):

    volume_tags = convert_tags_list_to_dict(volume.tags)
    volume_id = volume.volume_id
    volume_name = volume_tags.get('Name', '--no-name-specified--')
    topic = volume_tags.get('auto:snapshot:topic')
    retention_days = int(volume_tags.get('auto:snapshots:retention_days', MAX_RETENTION_DAYS))
    now = datetime.datetime.now()
    expiration_date = (now + datetime.timedelta(days=retention_days)).date().isoformat()

    current_snapshot_description = get_current_snapshot(volume_id)

    version = get_next_version(current_snapshot_description)

    snapshot_tags = {
        'Name': "{}:{}".format(volume_name, str(version)),
        'auto:snapshots:expiration_date': expiration_date,
        'auto:snapshots:version': str(version),
        "auto:snapshots:current:{}".format(volume_id): "true"
    }

    print("Creating a snapshot backup of volume: {} id: {} at: {}".
          format(volume_name, volume_id, now.isoformat()))

    created_snapshot_description = service_resource.create_snapshot(
            VolumeId=volume.volume_id,
            Description="auto-snapshot backup of volumeId {} at {}".format(volume_id, now.isoformat()))
    # add the tags for the new snapshot
    service_resource.create_tags(
        Resources=(created_snapshot_description.snapshot_id,),
        Tags=convert_tags_dict_to_list(snapshot_tags)
    )
    # update the tags for the previous snapshot
    if current_snapshot_description:
        current_flag_tag = service_resource.Tag(
                current_snapshot_description['SnapshotId'],
                "auto:snapshots:current:{}".format(volume_id),
                'true')
        current_flag_tag.delete()

    if topic:
        notify(topic)

    print("A snapshot backup of volume: {} is being created with id: {}, tags: {}".
          format(volume_name, created_snapshot_description.snapshot_id, snapshot_tags))


def notify(topic_name):
    client = boto3.client('sns')
    topic_object = client.create_topic(
        Name=topic_name
    )
    response = client.publish(
        TopicArn=topic_object['TopicArn'],
        Message=topic_name,
        Subject=topic_name,
        MessageStructure='string'
    )
    return response


def run(event, context):

    ec2 = boto3.resource('ec2', region_name='eu-west-1')
    filters = [{'Name': 'tag-key', 'Values': ['auto:snapshots']}]
    volumes = list(ec2.volumes.filter(Filters=filters))

    print("{} Volumes are subscribed for auto-snapshot backup".format(len(volumes)))

    for volume in volumes:
        create_snapshot(volume, ec2)

    return event


if __name__ == '__main__':
    run({}, {})

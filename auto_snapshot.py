"""Create snapshots for selected EBS volumes in AWS

Module methods:

    create_snapshots_handler:
        Start iterate over the subscribed volumes, create a snapshot for each one

"""
from __future__ import print_function
import datetime

import boto3

import settings
from utils import convert_tags_dict_to_list, convert_tags_list_to_dict


def get_current_snapshot(volume_id):
    """Find the latest snapshot for the given volume

    :param volume_id: the id of the volume
    :type volume_id: str
    :return: a dict describing the current snapshot
    """
    ec = boto3.client('ec2')
    filters = [
        {'Name': 'tag-key', 'Values': ["auto:snapshots:current:{}".format(volume_id)]},
        {'Name': 'tag-value', 'Values': ["true"]},
    ]
    snapshot_response = ec.describe_snapshots(Filters=filters)
    snapshots = snapshot_response.get('Snapshots')

    if len(snapshots) > 1:
        # Fail if there is more than one current backup so, need to be tracked via some SNS event
        raise Exception("auto-snpashot error: More than one current backup for volume id: {}".
                        format(volume_id))

    if snapshots and len(snapshots) == 1:
        return snapshots[0]


def get_next_version(current_snapshot_description):
    """Get the version for the next snapshot backup

    :param current_snapshot_description: A dict with the key: 'Tags'
        The value of the key is a list of tags including the version e.g:
        {'Tags': [{'Key': 'auto:snapshots:version', 'Value': '1'}]}
    :type current_snapshot_description: dict or None
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
    """

    :param volume: the volume to backup
    :type volume: ec2.Volume object
    :param service_resource: the volume's resource
    :type service_resource: ec2.ServiceResource object
    :return:
    """
    volume_tags = convert_tags_list_to_dict(volume.tags)
    volume_id = volume.volume_id
    volume_name = volume_tags.get('Name', '--no-name-specified--')
    topic = volume_tags.get('auto:snapshot:topic')
    retention_days = int(volume_tags.get('auto:snapshots:retention_days', settings.MAX_RETENTION_DAYS))
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
    """Publish an AWS SNS notification in the given topic
    :param topic_name: the name of the notification topic
    :type topic_name: str
    """
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


def create_snapshots_handler(event, context):
    """The entry point for the execution.
        Starts the process of taking snapshots of volumes.
        Can be triggered by different events in AWS.
    :param event: event data
    :type event: usually of the Python dict type.
        It can also be list, str, int, float, or NoneType type.
    :param context: AWS Lambda service uses this parameter to provide runtime information to the handler
    :type context: LambdaContext
    :return: None
    """
    ec2 = boto3.resource('ec2', region_name='eu-west-1')
    filters = [{'Name': 'tag-key', 'Values': ['auto:snapshots']}]
    volumes = list(ec2.volumes.filter(Filters=filters))

    print("{} Volumes are subscribed for auto-snapshot backup".format(len(volumes)))

    for volume in volumes:
        create_snapshot(volume, ec2)


if __name__ == '__main__':
    create_snapshots_handler({}, {})

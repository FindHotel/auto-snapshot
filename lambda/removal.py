"""Delete snapshots for selected EBS volumes in AWS


Module methods:

    remove_snapshots_handler:
        Start iterate over the snapshots, remove the expired ones

"""

import datetime
import dateutil.parser

import boto3

from utils import convert_tags_list_to_dict


def remove_snapshots_handler(event, context):
    """The entry point for the execution.
        Starts the process of removing expired snapshots of volumes.
        Can be triggered by different events in AWS.
    :param event: event data
    :type event: usually of the Python dict type.
        It can also be list, str, int, float, or NoneType type.
    :param context: AWS Lambda service uses this parameter to provide runtime information to the handler
    :type context: LambdaContext
    :return: None
    """
    ec2 = boto3.resource('ec2', region_name='eu-west-1')
    today = datetime.datetime.now().date()

    filters = [{'Name': 'tag-key', 'Values': ['auto:snapshots:expiration_date']}]

    snapshots = list(ec2.snapshots.filter(Filters=filters))
    print("{} Snapshots exist".format(len(snapshots)))

    for snapshot in snapshots:

        tags = convert_tags_list_to_dict(snapshot.tags)
        expiration_date = dateutil.parser.parse(tags['auto:snapshots:expiration_date']).date()
        if expiration_date <= today:
            print("Deleting snapshot {}, id: {}, expiration_date: {}".
                  format(tags['Name'], snapshot.snapshot_id, expiration_date))
            snapshot.delete()


if __name__ == '__main__':
    remove_snapshots_handler({}, {})

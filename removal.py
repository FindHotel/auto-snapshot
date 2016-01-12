"""Delete snapshots for selected EBS volumes in AWS

This module includes the function for deleting any expired snapshot that implement the tags bellow:

tag key                             tag value
---------------------------------------------------------------------------------------
*Name                               <snapshot name>
*auto:snapshots:expiration_date     <expiration_date>

*mandatory tags

Example tags:

tag key                             tag value
---------------------------------------------------------------------------------------
Name                               volume-for-autoSnapshot:1
auto:snapshots:expiration_date     2016-01-22


Module methods:

    run:
        Start the execution

"""


import datetime
import boto3
import dateutil.parser

from utils import convert_tags_list_to_dict


def run(event, context):

    ec2 = boto3.resource('ec2', region_name='eu-west-1')
    today = datetime.datetime.now().date()

    filters = [{'Name': 'tag-key', 'Values': ['auto:snapshots:expiration_date']}]

    snapshots = list(ec2.snapshots.filter(Filters=filters))
    print("{} Snapshots exist".format(len(snapshots)))

    for snapshot in snapshots:

        tags = convert_tags_list_to_dict(snapshot.tags)
        expiration_date = dateutil.parser.parse(tags['auto:snapshots:expiration_date']).date()
        if expiration_date == today:
            print("Deleting snapshot {}, id: {}, expiration_date: {}".
                  format(tags['Name'], snapshot.snapshot_id, expiration_date))
            snapshot.delete()

    return event


if __name__ == '__main__':
    run({}, {})

"""
Utils for working with AWS
"""


def convert_tags_list_to_dict(tags_list):
    """Convert tags list as provided by boto3 library to a dict
    :param tags_list: list of dicts each one represent a tag e.g:
        [{'Key': 'auto:snapshots:version', 'Value': '1'}]}
    :return: dict of tags.
        each key is the tag name, each value is the tag value
    """
    return {tag['Key']: tag['Value'] for (tag) in tags_list}


def convert_tags_dict_to_list(tags_dict):
    """Convert tags dict to a list as boto3 library is expecting
    :param tags_dict: dict of tags e.g:
        {'auto:snapshots:version': '1'}
    :return: list of dicts.
        each one represent a tag
    """
    return [{'Key': tag[0], 'Value': tag[1]} for tag in tags_dict.items()]

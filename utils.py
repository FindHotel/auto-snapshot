

def convert_tags_list_to_dict(tags_list):
    return {tag['Key']: tag['Value'] for (tag) in tags_list}


def convert_tags_dict_to_list(tags_dict):
    return [{'Key': tag[0], 'Value': tag[1]} for tag in tags_dict.items()]


def get_group_volume_name(group_name):
    group_name = group_name
    return group_name.lower().replace('_', '-')


def get_group_volume_path(group_name):
    group_volume_name = get_group_volume_name(group_name)
    return '/home/jovyan/' + group_volume_name
import enum


@enum.unique
class Feature(enum.Enum):
    about = 1


def make_feature_checker(requested_names, error_callback):
    requested = set()
    for name in requested_names:
        try:
            feature = Feature[name]
        except KeyError:
            error_callback("{!r} feature does not exist!".format(name))
        else:
            requested.add(feature)
    return lambda feature: feature in requested

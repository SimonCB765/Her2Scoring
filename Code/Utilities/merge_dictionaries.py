"""Function to merge an arbitrary number of dictionaries."""


def main(*dictionaries):
    """Merge an arbitrary number of dictionaries into one dictionary.

    If multiple dictionaries have the same key, then precedence goes to the dictionary later in the argument list.
    For example, main({'a': 1, 'b': 2}, {'c': 3}, {'a': 100}) will result in the dictionary {'a': 100, 'b': 2, 'c': 3}.

    This function is equivalent to z = {**x, **y, **z ...} in Python 3.5+.

    :param dictionaries:    Dictionaries to be merged.
    :type dictionaries:     dict(s)
    :return :               Merged dictionary.
    :rtype :                dict

    """

    result = {}
    for i in dictionaries:
        result.update(i)
    return result
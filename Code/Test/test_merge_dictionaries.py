"""Test the merging of multiple dictionaries.

To run this unittest run the command "python -m unittest Test.test_merge_dictionaries" from the Code directory.

"""

# Python imports.
import unittest

# User imports.
import Utilities.merge_dictionaries


class MergeTest(unittest.TestCase):
    """Test whether the merging works."""

    def test_empty(self):
        self.assertEqual({}, Utilities.merge_dictionaries.main({}))
        self.assertEqual({}, Utilities.merge_dictionaries.main({}, {}))
        self.assertEqual({}, Utilities.merge_dictionaries.main({}, {}, {}))
        self.assertEqual({}, Utilities.merge_dictionaries.main({}, {}, {}, {}))

    def test_nonempty(self):
        self.assertEqual({'a': 1, 'b': 2}, Utilities.merge_dictionaries.main({'a': 1}, {'b': 2}))
        self.assertEqual({'a': 100, 'b': 2, 'c': 3},
                         Utilities.merge_dictionaries.main({'a': 1, 'b': 1, 'c': 3}, {'b': 2}, {'a': 100}))

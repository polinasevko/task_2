from itertools import zip_longest
from functools import total_ordering
import re


@total_ordering
class Version:
    letter_matching = {
        ('a', 'alpha'): 0,
        ('b', 'beta'): 1,
        ('c', 'rc'): 2,
    }

    def __init__(self, version: str):
        self.main_version, self.pre_release = Version.parse_version(version)

    def __eq__(self, other):
        return self._comparison(other) == 0

    def __lt__(self, other):
        return self._comparison(other) == -1

    def _comparison(self, other):
        if isinstance(other, str):
            other = Version(other)
        elif not isinstance(other, Version):
            raise TypeError()

        # comparison of main version
        for first, second in zip_longest(self.main_version, other.main_version, fillvalue=0):
            if first < second:
                return -1
            elif first > second:
                return 1

        # comparison of pre-release version
        for first, second in zip_longest(self.pre_release, other.pre_release, fillvalue=100):
            if first < second:
                return -1
            elif first > second:
                return 1
        return 0

    @staticmethod
    def parse_version(version: str):
        # parse main version
        main_version_piece = (re.match(r'\d+(\.\d+)?(\.\d+)?', version)).group()
        main_version = list(map(int, main_version_piece.split('.')))

        # parse pre-release version
        pre_release_piece = re.sub(f'{main_version_piece}-?', '', version)
        raw_pre_release = re.split(r'([a-z]+)(\d+)|\.', pre_release_piece.lower())

        pre_release = []
        is_letter = False
        for elem in raw_pre_release:
            if not elem:
                continue
            elif elem.isnumeric():  # add number element to pre_release
                pre_release.append(int(elem))
                is_letter = False
                continue
            elif is_letter:  # explicit assignment of the 1st version
                pre_release.append(1)
                is_letter = False

            # convert letter to number
            tuple_key = next((tuple_key for tuple_key in Version.letter_matching.keys() if elem in tuple_key), None)
            if tuple_key:
                pre_release.append(Version.letter_matching[tuple_key])
                is_letter = True
            else:
                raise ValueError("The letter doesn't match.")

        if is_letter:
            pre_release.append(1)

        return main_version, pre_release


def main():
    to_test = [
        ("1.0.0", "2.0.0"),
        ("1.0.0", "1.42.0"),
        ("1.2.0", "1.2.42"),
        ("1.1.0-alpha", "1.2.0-alpha.1"),
        ("1.0.1b77.6", "1.0.10-alpha.beta"),
        ("1.0.0-rc.1", "1.0.0"),
    ]

    for version_1, version_2 in to_test:
        assert Version(version_1) < Version(version_2), "le failed"
        assert Version(version_2) > Version(version_1), "ge failed"
        assert Version(version_2) != Version(version_1), "neq failed"


if __name__ == "__main__":
    main()

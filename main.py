from functools import total_ordering


@total_ordering
class Version:
    def __init__(self, version: str):
        self.original = version.strip()

        if '+' in self.original:
            main_and_pre, self.build = self.original.split('+', 1)
        else:
            main_and_pre, self.build = self.original, None

        if '-' in main_and_pre:
            main, prerelease_str = main_and_pre.split('-', 1)
            self.prerelease = self._parse_prerelease(prerelease_str)
        else:
            main, self.prerelease = main_and_pre, ()

        parts = main.split('.')
        if len(parts) != 3:
            raise ValueError(f"Invalid version: {main}. Must be X.Y.Z")

        try:
            self.major = self._extract_number(parts[0])
            self.minor = self._extract_number(parts[1])
            self.patch = self._extract_number(parts[2])
        except ValueError:
            raise ValueError(f"Invalid numeric part in version: {main}")

    def _extract_number(self, text: str) -> int:
        num = ""
        for ch in text:
            if ch.isdigit():
                num += ch
            else:
                break
        if not num:
            raise ValueError(f"No numeric prefix in '{text}'")
        return int(num)

    def _parse_prerelease(self, s: str):
        parts = s.replace("-", ".").split(".")
        result = []
        for p in parts:
            if p.isdigit():
                result.append((0, int(p)))
            else:
                result.append((1, p))
        return tuple(result)

    def _cmp_tuple(self):
        prerelease_key = self.prerelease or ((2, ""),)
        return (self.major, self.minor, self.patch, prerelease_key)

    def __eq__(self, other):
        if isinstance(other, str):
            other = Version(other)
        return self._cmp_tuple() == other._cmp_tuple()

    def __lt__(self, other):
        if isinstance(other, str):
            other = Version(other)
        return self._cmp_tuple() < other._cmp_tuple()

    def __repr__(self):
        return f"Version('{self.original}')"


def main():
    to_test = [
        ("1.0.0", "2.0.0"),
        ("1.0.0", "1.42.0"),
        ("1.2.0", "1.2.42"),
        ("1.1.0-alpha", "1.2.0-alpha.1"),
        ("1.0.1b", "1.0.10-alpha.beta"),
        ("1.0.0-rc.1", "1.0.0"),
    ]

    for left, right in to_test:
        assert Version(left) < Version(right), "le failed"
        assert Version(right) > Version(left), "ge failed"
        assert Version(right) != Version(left), "neq failed"

    print("All tests passed!")


if __name__ == "__main__":
    main()

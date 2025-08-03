from functools import total_ordering


@total_ordering
class Version:
    def __init__(self, version: str):
        self.original = version

        version = version.split("+")[0]

        if "-" in version:
            main, prerelease = version.split("-", 1)
            self.prerelease = self._parse_prerelease(prerelease)
        else:
            main = version
            self.prerelease = ()

        parts = main.split(".")
        while len(parts) < 3:
            parts.append("0")

        self.major = self._extract_number(parts[0])
        self.minor = self._extract_number(parts[1])
        self.patch = self._extract_number(parts[2])

    def _extract_number(self, text: str) -> int:
        num = ""
        for ch in text:
            if ch.isdigit():
                num += ch
            else:
                break
        return int(num) if num else 0

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
        return self._cmp_tuple() == other._cmp_tuple()

    def __lt__(self, other):
        return self._cmp_tuple() < other._cmp_tuple()


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

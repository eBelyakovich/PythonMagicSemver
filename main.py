import unittest
from functools import total_ordering


@total_ordering
class Version:
    def __init__(self, version: str):
        self.original = version.strip()
        self.major = self.minor = self.patch = 0
        self.prerelease = ()
        self.build = None

        self._parse(self.original)

    def _parse(self, version: str):
        if '+' in version:
            main_and_pre, self.build = version.split('+', 1)
        else:
            main_and_pre, self.build = version, None

        if '-' in main_and_pre:
            main, prerelease_str = main_and_pre.split('-', 1)
            self.prerelease = self._parse_prerelease(prerelease_str)
        else:
            main = main_and_pre

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

    @property
    def _cmp_tuple(self):
        prerelease_key = self.prerelease or ((2, ""),)
        return (self.major, self.minor, self.patch, prerelease_key)

    def __eq__(self, other):
        if isinstance(other, str):
            other = Version(other)
        return self._cmp_tuple == other._cmp_tuple

    def __lt__(self, other):
        if isinstance(other, str):
            other = Version(other)
        return self._cmp_tuple < other._cmp_tuple

    def __repr__(self):
        return f"Version('{self.original}')"



class TestVersion(unittest.TestCase):
    def test_basic_order(self):
        self.assertLess(Version("1.0.0"), Version("2.0.0"))
        self.assertLess(Version("1.0.0"), Version("1.42.0"))
        self.assertLess(Version("1.2.0"), Version("1.2.42"))

    def test_prerelease_order(self):
        self.assertLess(Version("1.1.0-alpha"), Version("1.2.0-alpha.1"))
        self.assertLess(Version("1.0.1b"), Version("1.0.10-alpha.beta"))
        self.assertLess(Version("1.0.0-rc.1"), Version("1.0.0"))

    def test_build_metadata_ignored(self):
        self.assertEqual(Version("1.0.0+build1"), Version("1.0.0+build2"))
        self.assertFalse(Version("1.0.0+build1") < Version("1.0.0+build2"))

    def test_equal_versions(self):
        self.assertEqual(Version("1.2.3"), Version("1.2.3"))
        self.assertNotEqual(Version("1.2.3"), Version("1.2.4"))

    def test_invalid_versions(self):
        with self.assertRaises(ValueError):
            Version("1.2")
        with self.assertRaises(ValueError):
            Version("a.b.c")
        with self.assertRaises(ValueError):
            Version("1.2.x")
        with self.assertRaises(ValueError):
            Version("..")

    def test_str_comparison(self):
        self.assertTrue(Version("1.2.3") == "1.2.3")
        self.assertTrue(Version("1.2.3") < "1.2.4")
        self.assertTrue(Version("1.2.3-alpha") < "1.2.3")

if __name__ == "__main__":
    unittest.main()

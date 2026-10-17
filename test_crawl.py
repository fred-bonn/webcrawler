import unittest
import dataclasses
from crawl import normalize_url, get_heading_from_html, get_first_paragraph_from_html, get_urls_from_html, get_images_from_html

class TestCrawl(unittest.TestCase):
    def test_normalize_url(self) -> None:
        @dataclasses.dataclass
        class TestCase:
            name: str
            input_url: str
            expected: str

        cases = [
            TestCase(name="strips HTTPS scheme", input_url="https://www.test.com/blog/path", expected="www.test.com/blog/path"),
            TestCase(name="strips HTTP scheme", input_url="http://www.test.com/blog/path", expected="www.test.com/blog/path"),
            TestCase(name="trims trailing slash from HTTPS URL", input_url="https://test.com/blog/path/", expected="test.com/blog/path"),
            TestCase(name="trims trailing slash from HTTP URL", input_url="http://test.com/blog/path/", expected="test.com/blog/path"),
            TestCase(name="preserves URL without scheme", input_url="www.test.com/blog/path", expected="www.test.com/blog/path"),
            TestCase(name="handles empty URL", input_url="", expected=""),
        ]

        for case in cases:
            with self.subTest(case=case.name):
                actual = normalize_url(case.input_url)
                self.assertEqual(actual, case.expected)

    def test_get_heading_from_html(self) -> None:
        @dataclasses.dataclass
        class TestCase:
            name: str
            input_html: str
            expected: str

        cases = [
            TestCase(name="extracts h1 text", input_html="<h1>h1 Title</h1>", expected="h1 Title"),
            TestCase(name="extracts alternate h1 text", input_html="<h1>Another h1 Title</h1>", expected="Another h1 Title"),
            TestCase(name="trims h2 text whitespace", input_html="<h2>   h2 Title</h2>", expected="h2 Title"),
            TestCase(name="prefers h1 over h2", input_html="<h1>h1 Title</h1><h2>h2 Title</h2>", expected="h1 Title"),
            TestCase(name="handles empty HTML", input_html="", expected=""),
            TestCase(name="ignores h3 headings", input_html="<h3>h3 Title</h3>", expected=""),
        ]

        for case in cases:
            with self.subTest(case=case.name):
                actual = get_heading_from_html(case.input_html)
                self.assertEqual(actual, case.expected)

    def test_get_first_paragraph_from_html(self) -> None:
        @dataclasses.dataclass
        class TestCase:
            name: str
            input_html: str
            expected: str

        cases = [
            TestCase(name="extracts first paragraph", input_html="<p>First paragraph.</p>", expected="First paragraph."),
            TestCase(name="finds paragraph after headings", input_html="<h1>h1 Title</h1><h2>h2 Title</h2><p>First paragraph.</p>", expected="First paragraph."),
            TestCase(name="trims paragraph whitespace", input_html="<p>First paragraph.   </p><p>Second paragraph.</p>", expected="First paragraph."),
            TestCase(name="handles empty HTML", input_html="", expected=""),
            TestCase(name="returns empty when there is no paragraph", input_html="<div>No paragraph here.</div>", expected=""),
        ]

        for case in cases:
            with self.subTest(case=case.name):
                actual = get_first_paragraph_from_html(case.input_html)
                self.assertEqual(actual, case.expected)

    def test_get_urls_from_html(self) -> None:
        @dataclasses.dataclass
        class TestCase:
            name: str
            input_html: str
            base_url: str
            expected: list[str]

        cases = [
            TestCase(name="extracts absolute anchor URL",
                     input_html='<a href="https://www.test.com">Link</a>',
                     base_url="https://www.test.com",
                     expected=["https://www.test.com"]),
            TestCase(name="extracts multiple absolute anchor URLs",
                     input_html='<a href="https://www.test.com">Link</a><a href="https://www.example.com">Another Link</a>',
                     base_url="https://www.test.com",
                     expected=["https://www.test.com", "https://www.example.com"]),
            TestCase(name="ignores anchors without href",
                     input_html='<a href="https://www.test.com">Link</a><a>Missing href</a>',
                     base_url="https://www.test.com",
                     expected=["https://www.test.com"]),
            TestCase(name="resolves relative anchor URL",
                     input_html='<a href="/relative/path">Relative Link</a>',
                     base_url="https://www.test.com",
                     expected=["https://www.test.com/relative/path"]),
            TestCase(name="ignores absolute image URL without anchors",
                     input_html="<img src='https://www.test.com/image.jpg'>",
                     base_url="https://www.test.com",
                     expected=[]),
            TestCase(name="ignores relative image URL without anchors",
                     input_html='<img src="/relative/path/image.jpg">',
                     base_url="https://www.test.com",
                     expected=[]),
            TestCase(name="extracts anchor URL but ignores image URL",
                     input_html="<img src='https://www.test.com/image.jpg'><a href=\"https://www.test.com\">Link</a>",
                     base_url="https://www.test.com",
                     expected=["https://www.test.com"]),
            TestCase(name="handles empty HTML",
                     input_html="",
                     base_url="https://www.test.com",
                     expected=[]),
            TestCase(name="returns empty when there are no anchors",
                     input_html="<div>No links here.</div>",
                     base_url="https://www.test.com",
                     expected=[]),
        ]

        for case in cases:
            with self.subTest(case=case.name):
                actual = get_urls_from_html(case.input_html, case.base_url)
                self.assertEqual(actual, case.expected)

    def test_get_images_from_html(self) -> None:
        @dataclasses.dataclass
        class TestCase:
            name: str
            input_html: str
            base_url: str
            expected: list[str]

        cases = [
            TestCase(name="extracts absolute image URL",
                     input_html="<img src='https://www.test.com/image.jpg'>",
                     base_url="https://www.test.com",
                     expected=["https://www.test.com/image.jpg"]),
            TestCase(name="resolves relative image URL",
                     input_html='<img src="/relative/path/image.jpg">',
                     base_url="https://www.test.com",
                     expected=["https://www.test.com/relative/path/image.jpg"]),
            TestCase(name="handles empty HTML",
                     input_html="",
                     base_url="https://www.test.com",
                     expected=[]),
            TestCase(name="returns empty when there are no images",
                     input_html="<div>No images here.</div>",
                     base_url="https://www.test.com",
                     expected=[]),
        ]

        for case in cases:
            with self.subTest(case=case.name):
                actual = get_images_from_html(case.input_html, case.base_url)
                self.assertEqual(actual, case.expected)

    def test_filler(self) -> None:
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
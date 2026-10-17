import unittest
import dataclasses
from crawl import normalize_url, get_heading_from_html, get_first_paragraph_from_html, get_urls_from_html, get_images_from_html

class TestCrawl(unittest.TestCase):
    def test_normalize_url(self) -> None:
        @dataclasses.dataclass
        class TestCase:
            input_url: str
            expected: str

        cases = [
            TestCase(input_url="https://www.test.com/blog/path", expected="www.test.com/blog/path"),
            TestCase(input_url="http://www.test.com/blog/path", expected="www.test.com/blog/path"),
            TestCase(input_url="https://test.com/blog/path/", expected="test.com/blog/path"),
            TestCase(input_url="http://test.com/blog/path/", expected="test.com/blog/path"),
            TestCase(input_url="www.test.com/blog/path", expected="www.test.com/blog/path"),
            TestCase(input_url="", expected=""),
        ]

        for case in cases:
            actual = normalize_url(case.input_url)
            self.assertEqual(actual, case.expected)

    def test_get_heading_from_html(self) -> None:
        @dataclasses.dataclass
        class TestCase:
            input_html: str
            expected: str

        cases = [
            TestCase(input_html="<h1>h1 Title</h1>", expected="h1 Title"),
            TestCase(input_html="<h1>Another h1 Title</h1>", expected="Another h1 Title"),
            TestCase(input_html="<h2>   h2 Title</h2>", expected="h2 Title"),
            TestCase(input_html="<h1>h1 Title</h1><h2>h2 Title</h2>", expected="h1 Title"),
            TestCase(input_html="", expected=""),
            TestCase(input_html="<h3>h3 Title</h3>", expected=""),
        ]

        for case in cases:
            actual = get_heading_from_html(case.input_html)
            self.assertEqual(actual, case.expected)

    def test_get_first_paragraph_from_html(self) -> None:
        @dataclasses.dataclass
        class TestCase:
            input_html: str
            expected: str

        cases = [
            TestCase(input_html="<p>First paragraph.</p>", expected="First paragraph."),
            TestCase(input_html="<h1>h1 Title</h1><h2>h2 Title</h2><p>First paragraph.</p>", expected="First paragraph."),
            TestCase(input_html="<p>First paragraph.   </p><p>Second paragraph.</p>", expected="First paragraph."),
            TestCase(input_html="", expected=""),
            TestCase(input_html="<div>No paragraph here.</div>", expected=""),
        ]

        for case in cases:
            actual = get_first_paragraph_from_html(case.input_html)
            self.assertEqual(actual, case.expected)

    def test_get_urls_from_html(self) -> None:
        @dataclasses.dataclass
        class TestCase:
            input_html: str
            base_url: str
            expected: list[str]

        cases = [
            TestCase(input_html='<a href="https://www.test.com">Link</a>',
                     base_url="https://www.test.com",
                     expected=["https://www.test.com"]),
            TestCase(input_html='<a href="https://www.test.com">Link</a><a href="https://www.example.com">Another Link</a>',
                     base_url="https://www.test.com",
                     expected=["https://www.test.com", "https://www.example.com"]),
            TestCase(input_html='<a href="https://www.test.com">Link</a><a>Missing href</a>',
                     base_url="https://www.test.com",
                     expected=["https://www.test.com"]),
            TestCase(input_html='<a href="/relative/path">Relative Link</a>',
                     base_url="https://www.test.com",
                     expected=["https://www.test.com/relative/path"]),
            TestCase(input_html="<img src='https://www.test.com/image.jpg'>",
                     base_url="https://www.test.com",
                     expected=["https://www.test.com/image.jpg"]),
            TestCase(input_html='<img src="/relative/path/image.jpg">',
                     base_url="https://www.test.com",
                     expected=["https://www.test.com/relative/path/image.jpg"]),
            TestCase(input_html="<img src='https://www.test.com/image.jpg'><a href=\"https://www.test.com\">Link</a>",
                     base_url="https://www.test.com",
                     expected=["https://www.test.com", "https://www.test.com/image.jpg"]),
            TestCase(input_html="",
                     base_url="https://www.test.com",
                     expected=[]),
            TestCase(input_html="<div>No links here.</div>",
                     base_url="https://www.test.com",
                     expected=[]),
        ]

        for case in cases:
            actual = get_urls_from_html(case.input_html, case.base_url)
            self.assertEqual(actual, case.expected)

    def test_get_images_from_html(self) -> None:
        @dataclasses.dataclass
        class TestCase:
            input_html: str
            base_url: str
            expected: list[str]

        cases = [
            TestCase(input_html="<img src='https://www.test.com/image.jpg'>",
                     base_url="https://www.test.com",
                     expected=["https://www.test.com/image.jpg"]),
            TestCase(input_html='<img src="/relative/path/image.jpg">',
                     base_url="https://www.test.com",
                     expected=["https://www.test.com/relative/path/image.jpg"]),
            TestCase(input_html="",
                     base_url="https://www.test.com",
                     expected=[]),
            TestCase(input_html="<div>No images here.</div>",
                     base_url="https://www.test.com",
                     expected=[]),
        ]

        for case in cases:
            actual = get_images_from_html(case.input_html, case.base_url)
            self.assertEqual(actual, case.expected)

    def test_filler(self) -> None:
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
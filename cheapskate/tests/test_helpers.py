from django.test import TestCase

from ..helpers import add_url_parameter


class AddUrlParametersTestCase(TestCase):

    def test_add_first_get_param(self):
        expected = "https://example.com?foo=1"
        result = add_url_parameter("https://example.com", "foo", 1)
        self.assertEqual(result, expected)

    def test_add_additional_get_param(self):
        expected = "https://example.com?foo=1&coffee=yes"
        result = add_url_parameter("https://example.com?foo=1", "coffee", "yes")
        self.assertEqual(result, expected)

    def test_replace_existing_get_param(self):
        expected = "https://example.com?foo=2"
        result = add_url_parameter("https://example.com?foo=1", "foo", "2")
        self.assertEqual(result, expected)

    def test_add_key_only_param(self):
        expected = "https://example.com?foo=1&debug"
        result = add_url_parameter("https://example.com?foo=1", "debug", None)
        self.assertEqual(result, expected)

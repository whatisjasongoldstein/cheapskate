import json
from django.test import TestCase

from ..templatetags.helpers import jsonify, to_int

class TemplateTagsTestCase(TestCase):

    def test_jsonify(self):
        data = {"foo": [1, 2, 3]}
        result = jsonify(data)
        self.assertIsInstance(result, str)
        self.assertEqual(json.loads(result), data)        

    def test_to_int(self):
        data = "120"
        self.assertEqual(to_int(data), 120)

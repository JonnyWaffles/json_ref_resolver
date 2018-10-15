import unittest
import json
from pathlib import Path
from jsonschema import RefResolver

from json_ref_depth import ResolverDepth


class DepthResolverTest(unittest.TestCase):
    def get_file_resolver(self):
        base_url = f'file:///{Path(__file__).parent.absolute()}'
        return RefResolver(base_url, self.get_schema())

    @staticmethod
    def get_schema():
        p = Path('test_schema.json')
        return json.loads(p.read_text())

    def test_depth(self):
        resolver = self.get_file_resolver()
        schema = self.get_schema()
        level_zero = ResolverDepth(schema, resolver, 0).resolve()
        level_one = ResolverDepth(schema, resolver, 1).resolve()
        level_two = ResolverDepth(schema, resolver, 2).resolve()

        self.assertEqual(schema, level_zero)
        # level one contains an address reference
        self.check_result(level_one, 'level_one.json')
        # All the references are resolved for level 2
        self.check_result(level_two, 'level_two.json')

    def check_result(self, data, name):
        p = Path(__file__).parent / Path(name)
        expected = json.loads(p.read_text())
        self.assertEqual(expected, data)


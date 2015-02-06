from unittest import TestCase


class GetSettingsValueTest(TestCase):
    def _callFUT(self, name):
        from django_ftpserver.utils import get_settings_value
        return get_settings_value(name)

    def test_exists_attribute(self):
        self.assertTrue(self._callFUT('DEBUG'))

    def test_not_exists_attribute(self):
        self.assertEqual(self._callFUT('SPAM'), None)


class ParsePortsTest(TestCase):
    def _callFUT(self, ports_text):
        from django_ftpserver.utils import parse_ports
        return parse_ports(ports_text)

    def test_single_port(self):
        self.assertEqual(self._callFUT('12345'), [12345])

    def test_range(self):
        self.assertEqual(self._callFUT('5-10'), list(range(5, 11)))

    def test_multi_value(self):
        self.assertEqual(self._callFUT('1-3,7,10'), [1, 2, 3, 7, 10])

class TestGetSettingsValue:
    def _callFUT(self, name):
        from django_ftpserver.utils import get_settings_value
        return get_settings_value(name)

    def test_exists_attribute(self):
        assert self._callFUT('SECRET_KEY') == 'secret'

    def test_not_exists_attribute(self):
        assert self._callFUT('SPAM') == None


class TestParsePorts:
    def _callFUT(self, ports_text):
        from django_ftpserver.utils import parse_ports
        return parse_ports(ports_text)

    def test_single_port(self):
        assert self._callFUT('12345') == [12345]

    def test_range(self):
        assert self._callFUT('5-10') == list(range(5, 11))

    def test_multi_value(self):
        assert self._callFUT('1-3,7,10') == [1, 2, 3, 7, 10]

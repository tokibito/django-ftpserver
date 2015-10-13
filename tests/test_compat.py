from unittest import TestCase


class StringTypeTest(TestCase):
    def test(self):
        from django_ftpserver.compat import string_type
        self.assertIsNotNone(string_type)

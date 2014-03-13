from unittest import TestCase


def setUpModule():
    from . import testing
    testing.setup_django()


class FTPAccountAuthorizerTestBase(TestCase):
    def _getUser(self, **kwargs):
        from django.contrib.auth import models
        return models.User(**kwargs)

    def _getGroup(self, **kwargs):
        from django_ftpserver import models
        return models.FTPUserGroup(**kwargs)

    def _getAccount(self, **kwargs):
        from django_ftpserver import models
        return models.FTPUserAccount(**kwargs)

    def _getOne(self):
        from django_ftpserver import authorizers
        return authorizers.FTPAccountAuthorizer()


class FTPAccountAuthorizerHasUserTest(FTPAccountAuthorizerTestBase):
    """Test for FTPAccountAuthorizer.has_user
    """

    def setUp(self):
        self.user = self._getUser(username='user1')
        self.user.save()
        self.group = self._getGroup(name='group1')
        self.group.save()
        self.account = self._getAccount(user=self.user, group=self.group)
        self.account.save()

    def tearDown(self):
        self.user.delete()

    def test_has_user(self):
        authorizer = self._getOne()
        self.assertTrue(authorizer.has_user('user1'))

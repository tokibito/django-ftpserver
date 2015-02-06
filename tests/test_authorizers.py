from unittest import TestCase


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
        self.account.delete()
        self.group.delete()
        self.user.delete()

    def test_has_user(self):
        authorizer = self._getOne()
        self.assertTrue(authorizer.has_user('user1'))


class FTPAccountAuthorizerGetAccountTest(FTPAccountAuthorizerTestBase):
    """Test for FTPAccountAuthorizer.get_account
    """

    def setUp(self):
        self.user = self._getUser(username='user1')
        self.user.save()
        self.group = self._getGroup(name='group1')
        self.group.save()
        self.account = self._getAccount(user=self.user, group=self.group)
        self.account.save()

    def tearDown(self):
        self.account.delete()
        self.group.delete()
        self.user.delete()

    def test_get_account(self):
        authorizer = self._getOne()
        target = authorizer.get_account('user1')
        self.assertEqual(target.user.username, 'user1')


class FTPAccountAuthorizerValidateAuthenticationTest(
        FTPAccountAuthorizerTestBase):
    """Test for FTPAccountAuthorizer.validate_authentication
    """

    def setUp(self):
        self.user = self._getUser(username='user1')
        self.user.set_password('password1')
        self.user.save()
        self.group = self._getGroup(name='group1')
        self.group.save()
        self.account = self._getAccount(user=self.user, group=self.group)
        self.account.save()

    def tearDown(self):
        self.account.delete()
        self.group.delete()
        self.user.delete()

    def test_validate_authentication(self):
        authorizer = self._getOne()
        self.assertEqual(
            authorizer.validate_authentication('user1', 'password1', None),
            None)


class FTPAccountAuthorizerGetHomeDirTest(FTPAccountAuthorizerTestBase):
    """Test for FTPAccountAuthorizer.get_home_dir
    """

    def setUp(self):
        self.user = self._getUser(username='user1')
        self.user.save()
        self.group = self._getGroup(name='group1')
        self.group.save()
        self.account = self._getAccount(
            user=self.user, group=self.group, home_dir='/tmp/user1/')
        self.account.save()

    def tearDown(self):
        self.account.delete()
        self.group.delete()
        self.user.delete()

    def test_get_home_dir(self):
        authorizer = self._getOne()
        self.assertEqual(authorizer.get_home_dir('user1'), '/tmp/user1/')

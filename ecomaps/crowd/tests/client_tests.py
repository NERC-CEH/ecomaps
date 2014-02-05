from ecomaps.crowd.client import CrowdClient, SessionNotFoundException, ClientException, AuthenticationFailedException

__author__ = 'Phil Jenkins (Tessella)'

import unittest

class CrowdClientTests(unittest.TestCase):

    client = None

    def setUp(self):

        # self.client = CrowdClient(api_url="http://localhost:8095/crowd/rest/usermanagement/latest/",
        #                          app_name="ecomaps",
        #                          app_pwd="ecomaps")

        self.client = CrowdClient(api_url="http://crowd.ceh.ac.uk:8095/crowd/rest/usermanagement/latest/",
                                  app_name="ecomaps-dev",
                                  app_pwd="3WY7i1eIhl8Lzy2tr77f")

    def test_client_can_be_instantiated(self):

        self.assertNotEqual(self.client, None)

    def test_authentication_with_valid_credentials(self):

        # g = self.client.check_authenticated("crowd-admin", "pa55word")
        self.client.check_authenticated("philip.jenkins@tessella.com", "DrJ1jZlT62VQUg49]8ez")

    def test_user_session_request_with_valid_credentials(self):

        # self.client.create_user_session("crowd-admin", "pa55word", "127.0.0.1")
        self.client.create_user_session("philip.jenkins@tessella.com", "DrJ1jZlT62VQUg49]8ez", "80.252.78.170")

    def test_user_session_request_with_invalid_credentials(self):

        self.assertRaises(AuthenticationFailedException, lambda:self.client.create_user_session("crowd-admin", "sddfghfh", "127.0.0.1"))

    def test_duff_token(self):

        self.assertRaises(SessionNotFoundException, lambda: self.client.verify_user_session("abc123"))

    def test_proper_token(self):

        # response = self.client.create_user_session("crowd-admin", "pa55word", "127.0.0.1")
        response = self.client.create_user_session("philip.jenkins@tessella.com", "DrJ1jZlT62VQUg49]8ez", "80.252.78.170")
        obj = self.client.verify_user_session(response['token'])

        self.assertNotEqual(obj, None)

    def test_delete_session_invalidates_as_expected(self):

        # response = self.client.create_user_session("crowd-admin", "pa55word", "127.0.0.1")
        response = self.client.create_user_session("philip.jenkins@tessella.com", "DrJ1jZlT62VQUg49]8ez", "80.252.78.170")
        obj = self.client.verify_user_session(response['token'])

        # Delete the session
        self.client.delete_session(response['token'])

        self.assertRaises(SessionNotFoundException, lambda: self.client.verify_user_session(response['token']))

    def test_get_user_info_returns_populated_object(self):

        username = "philip.jenkins@tessella.com"

        user = self.client.get_user_info(username)

        self.assertEqual(username, user['name'])


def main():
    unittest.main()

if __name__ == '__main__':
    main()

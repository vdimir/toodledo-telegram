from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.parameters import MissingTokenError


def init_toodledo_client_app(client_id, client_secret):
    ToodledoSession.client = {"client_id": client_id, "client_secret": client_secret}


class ToodledoSession:
    auth_base_url = "https://api.toodledo.com/3/account/authorize.php"
    token_url = "https://api.toodledo.com/3/account/token.php"
    client = None

    def __init__(self, token=None, token_saver=None):
        self.token_saver = token_saver
        self._oauth = OAuth2Session(client_id=self.client['client_id'],
                                    token=token,
                                    scope=['basic', 'tasks', 'write', 'folders'],
                                    auto_refresh_url=self.token_url,
                                    auto_refresh_kwargs=self.client,
                                    token_updater=self.token_saver)

    @property
    def auth_url(self):
        url, _ = self._oauth.authorization_url(self.auth_base_url)
        return url

    def authorize(self, redirect_resp):
        redirect_resp = redirect_resp.replace("http://", "https://")
        token = self._oauth.fetch_token(self.token_url,
                                        client_secret=self.client['client_secret'],
                                        authorization_response=redirect_resp)
        self.token_saver(token)

    @property
    def oauth(self):
        return self._oauth


class NotAuthorizingError(Exception):
    pass


class ApiUrl:
    api_url = "https://api.toodledo.com/3/{}/{}.php"
    method = {'get': 'GET',
              'add': 'POST',
              }

    def __init__(self, path):
        self.path = path

    def build(self, item):
        url = self.api_url.format(self.path, item)
        return url, self.method[item]


class ToodledoRequest:
    def __init__(self, toodledo_session: ToodledoSession, path: str):
        self.session = toodledo_session
        self.url_builder = ApiUrl(path)

    def _request(self, method, url, params=None):
        try:
            resp = self.session.oauth.request(method, url, params=params)
        except MissingTokenError:
            raise NotAuthorizingError

        result = resp.json()
        if 'errorCode' in result and result['errorCode'] == 2:
            raise NotAuthorizingError

        resp.raise_for_status()
        return result

    def get(self, params=None):
        url, m = self.url_builder.build('get')
        return self._request(m, url, params)

    def add(self, params=None):
        url, m = self.url_builder.build('add')
        return self._request(m, url, params)

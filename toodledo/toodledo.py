from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.parameters import MissingTokenError, MissingCodeError

from .schemas import result_processor, params_processor


def init_toodledo_client_app(client_id, client_secret):
    ToodledoSession.client = {"client_id": client_id, "client_secret": client_secret}


class NotAuthorizingError(Exception):
    pass


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
        try:
            token = self._oauth.fetch_token(self.token_url,
                                            client_secret=self.client['client_secret'],
                                            authorization_response=redirect_resp)
            self.token_saver(token)
        except MissingCodeError:
            return False
        return True

    def request(self, method, url, **kwargs):
        try:
            resp = self._oauth.request(method, url, **kwargs)
        except MissingTokenError:
            raise NotAuthorizingError

        result = resp.json()
        if 'errorCode' in result and result['errorCode'] in [1,2]:
            raise NotAuthorizingError

        resp.raise_for_status()
        return result


class ApiUrl:
    api_url = "https://api.toodledo.com/3/{}/{}.php"
    method = {'get': 'GET',
              'add': 'POST',
              'edit': 'POST'
              }

    def __init__(self, path):
        self.path = path

    def build(self, item):
        url = self.api_url.format(self.path, item)
        return self.method[item], url


class ToodledoRequest:
    def __init__(self, session: ToodledoSession, path: str, action: str, postproc=None, preproc=None):
        self.url = ApiUrl(path).build(action)
        self.session = session
        self.postproc = postproc or (lambda x: x)
        self.preproc = preproc or (lambda x: x)

    def __call__(self, params=None, **kwargs):
        p = params and self.preproc(params)
        res = self.session.request(*self.url, params=p, **kwargs)
        return self.postproc(res)


class ToodledoApi:
    __attrs__ = ['get', 'add', 'edit']

    def __init__(self, session: ToodledoSession, path: str):
        self.session = session
        self.path = path

    def __getattr__(self, item) -> ToodledoRequest:
        if item not in self.__attrs__:
            raise Exception("Unknown action call!")
        pre = params_processor(self.path, item)
        post = result_processor(self.path, item)
        return ToodledoRequest(self.session, self.path, item, preproc=pre, postproc=post)

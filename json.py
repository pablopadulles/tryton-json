import requests
import simplejson as json
import base64

HOST = 'localhost'
PORT = '1606'
CREDENTIALS = ('admin', 'admin') # login, password


class HttpClient:
    """HTTP Client to make JSON RPC requests to Tryton server.
    User is logged in when an object is created.
    """

    def __init__(self, url, database_name, user, passwd):
        self._url = '{}/{}/'.format(url, database_name)
        self._user = user
        self._passwd = passwd
        self._login()
        self._id = 0

    def get_id(self):
        self._id += 1
        return self._id

    def _login(self):
        """
        Returns list, where
        0 - user id
        1 - session token
        """
        payload = json.dumps({
            'params': [self._user, {'password': self._passwd}],
            'jsonrpc': "2.0",
            'method': 'common.db.login',
            'id': 1,
        })
        headers = {'content-type': 'application/json'}
        result = requests.post(self._url, data=payload, headers=headers)
        r = result._content.replace('[', '').replace(']', '').replace('"', '').split(',')
        self._session = [r[0], unicode(r[1])]
        return self._session

    def call(self, prefix, method, params=[[], {}]):
        """RPC Call
        """
        method = '{}.{}'.format(prefix, method)
        payload = json.dumps({
            'params': params,
            'method': method,
            'id': self.get_id(),
        })

        auth = '{0}:{1}:{2}'.format(
            self._user, self._session[0], self._session[1])
        auth = 'Session  {}'.format(base64.b64encode(auth))

        headers = {'content-type': 'application/json', 'authorization': auth}
        import pdb;pdb.set_trace()
        response = requests.post(self._url, data=payload, headers=headers)
        return response.json()

    def model(self, model, method, args=[], kwargs={}):

        args.append(self._session)
        return self.call('model.%s' % model, method, [args, kwargs])

    def system(self, method):
        return self.call('system', method, params=[])


def main():
    url = "http://%s:%s" % (HOST, PORT)
    headers = {'content-type': 'application/json'}
    client = HttpClient(url, "aceite", CREDENTIALS[0], CREDENTIALS[1])

    """
    Examples:
    resp = client.system('listMethods')
    resp = client.model('res.user', 'get_preferences')
    resp = client.model('product.product', 'search_count')
    products_amount = resp['result']
    resp = client.model('account.move', 'search', kwargs={
        'domain': [('state', '=', 'draft')],
    })
    """
    
    resp = client.model('res.user', 'get_preferences')
    print resp


if __name__ == "__main__":
    main()

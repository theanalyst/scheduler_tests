import asyncio
from aiohttp import ClientSession, TCPConnector

from botocore.auth import S3SigV4Auth
from botocore.credentials import Credentials
from botocore.awsrequest import AWSRequest

def get_s3_auth_headers(creds, url, method, body=""):
    req = AWSRequest(method = method,
                     url = url)
    sig = S3SigV4Auth(Credentials(access_key='access1',secret_key='secret1'),
                      's3','us-east-1')
    sig.headers_to_sign(req)
    sig.add_auth(req)
    return dict(req.headers.items())

class AsyncClient():
    def __init__(self, url, req_count, handler,
                 auth_type=None, auth_creds=None, limit=None):
        self.url = url
        self.req_count = req_count
        self.session = ClientSession(connector=TCPConnector(limit=limit))
        self.handler = handler
        self.auth_type = auth_type
        self.auth_creds = auth_creds

    def get_auth_headers(self, auth_type, *args):
        if auth_type is None:
            return dict()
        elif auth_type == 's3':
            return get_s3_auth_headers(*args)
        else:
            raise NotImplementedError("the selected auth_type isn't implemented")

    async def get_request(self, headers={}, *params):
        auth_headers = self.get_auth_headers(self.auth_type,
                                             self.auth_creds, self.url, "GET")
        headers.update(auth_headers)
        async with self.session.get(self.url, headers=headers, *params) as resp:
            pass # We don't want to read the output payload yet, we just process the status for now
        self.handler.handle_response(resp)

    def make_request(self, req_type, *params):
        if req_type == "GET":
            return self.get_request(*params)


    async def run(self, req_type, *args):
        reqs = []
        async with self.session as s:
            for i in range(int(self.req_count)):
                print('making request!')
                reqs.append(asyncio.ensure_future(
                    self.get_request(*args)
                ))

            responses = await asyncio.gather(*reqs)

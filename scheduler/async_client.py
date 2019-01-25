import asyncio
from aiohttp import ClientSession, TCPConnector

from botocore.auth import S3SigV4Auth
from botocore.credentials import Credentials
from botocore.awsrequest import AWSRequest

def get_s3_auth_headers(creds, url, method, body=""):
    req = AWSRequest(method = method,
                     url = url)
    sig = S3SigV4Auth(Credentials(**creds),
                      's3','us-east-1')
    sig.headers_to_sign(req)
    sig.add_auth(req)
    return dict(req.headers.items())

class AsyncClient():
    def __init__(self, response_handler,
                 auth_type=None, auth_creds=None, limit=None):
        self.handler = response_handler
        self.auth_type = auth_type
        self.auth_creds = auth_creds

    def get_auth_headers(self, auth_type, *args):
        if auth_type is None:
            return dict()
        elif auth_type == 's3':
            return get_s3_auth_headers(*args)
        else:
            raise NotImplementedError("the selected auth_type isn't implemented")

    async def get_request(self, url, session, headers={}, *params):
        auth_headers = self.get_auth_headers(self.auth_type,
                                             self.auth_creds, url, "GET")
        headers.update(auth_headers)
        resp_data = None
        async with session.get(url, headers=headers, *params) as resp:
            if self.handler.needs_data():
                resp_data = await resp.read()

        return self.handler.handle_response(resp, resp_data)

    def make_request(self, req_type, req_url, *params):
        if req_type == "GET":
            return self.get_request(req_url, *params)


    async def run(self, req_type, req_url, req_count=100, *req_params):
        reqs = []
        async with ClientSession(connector=TCPConnector(limit=None, keepalive_timeout=300)) as s:
            for i in range(int(req_count)):
                #print('making request!')
                reqs.append(asyncio.ensure_future(
                    self.make_request(req_type, req_url, s, *req_params)
                ))

            responses = await asyncio.gather(*reqs)

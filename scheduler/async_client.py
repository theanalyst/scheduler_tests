import asyncio
import logging
from aiohttp import ClientSession, TCPConnector, ClientTimeout

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
        self.logger = logging.getLogger('async-client')
        self.logger.setLevel(logging.INFO)

    def get_auth_headers(self, auth_type, *args):
        if auth_type is None:
            return dict()
        elif auth_type == 's3':
            return get_s3_auth_headers(*args)
        else:
            raise NotImplementedError("the selected auth_type isn't implemented")

    async def get_request(self, url, session, headers={}, req_count=1, *params):
        auth_headers = self.get_auth_headers(self.auth_type,
                                             self.auth_creds, url, "GET")
        headers.update(auth_headers)
        resp_data = None
        async with session.get(url, headers=headers, *params) as resp:
            if self.handler.needs_data():
                resp_data = await resp.read()

        self.logger.debug('Finished reading data for req: %d' % req_count)
        self.handler.handle_response(resp, resp_data)

    def make_request(self, req_type, req_url, *params, **kwargs):
        if req_type == "GET":
            return self.get_request(req_url, *params, **kwargs)

    async def run(self, req_type, req_url, req_count=100, *req_params):
        reqs = []
        timeout = ClientTimeout(total=600)
        async with ClientSession(connector=TCPConnector(limit=None, keepalive_timeout=300),timeout=timeout) as s:
            for i in range(int(req_count)):
                self.logger.debug('making request: %d' % i)
                reqs.append(asyncio.ensure_future(
                    self.make_request(req_type, req_url, s, req_count=i, *req_params)
                ))

            responses = await asyncio.gather(*reqs)

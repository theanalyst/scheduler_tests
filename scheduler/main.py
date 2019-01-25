import utils
import sys
import asyncio
import logging

from async_client import AsyncClient
from response_handler import CounterHandler

DEBUG = True

if __name__ == "__main__":
    utils.assert_py_version()
    count_handler = CounterHandler()
    client = AsyncClient(
                         response_handler = count_handler,
                         auth_type = 's3',
                         auth_creds = {'access_key': 'access1', 'secret_key': 'secret1'}
    )

    req_map = {"GET": "http://localhost:8001/",
               "GET": "http://localhost:8001/versiontest/"}

    logging.basicConfig(level=logging.INFO)
    logging.getLogger("asyncio").setLevel(logging.DEBUG)
    ev_loop = asyncio.get_event_loop()
    if DEBUG:
        ev_loop.set_debug(True)
    futures = [
        asyncio.ensure_future(client.run('GET',"http://localhost:8001/",sys.argv[1])),
        asyncio.ensure_future(client.run('GET',"http://localhost:8001/versiontest",sys.argv[1]))
        ]
    ev_loop.run_until_complete(asyncio.gather(*futures))
    count_handler.print_stats()

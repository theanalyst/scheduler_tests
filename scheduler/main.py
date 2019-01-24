import utils
import sys
import asyncio

from async_client import AsyncClient
from response_handler import CounterHandler

if __name__ == "__main__":
    utils.assert_py_version()
    count_handler = CounterHandler()
    print(sys.argv[2])
    client = AsyncClient(sys.argv[1],
                         sys.argv[2],
                         handler = count_handler,
                         auth_type = 's3',
                         auth_creds = {'access_key': 'access1', 'secret_key': 'secret1'}
    )

    ev_loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(client.run('GET'))
    ev_loop.run_until_complete(future)
    count_handler.print_stats()

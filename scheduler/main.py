import sys
import asyncio

import utils
import ctx
from async_client import AsyncClient
from response_handler import CounterHandler

if __name__ == "__main__":
    utils.assert_py_version()
    count_handler = CounterHandler()
    client_ctx = ctx.make_ctx(sys.argv[1])
    client_ctx.set_up_logging()
    client = AsyncClient(response_handler = count_handler,
                         auth_type = client_ctx.auth_type,
                         auth_creds = client_ctx.auth_creds
    )

    ev_loop = asyncio.get_event_loop()
    futures = [ asyncio.ensure_future(client.run(**kwargs)) for kwargs in client_ctx.arg_list ]
    ev_loop.run_until_complete(asyncio.gather(*futures))
    count_handler.print_stats()

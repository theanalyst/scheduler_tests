import sys
import asyncio
import json

import utils
import ctx
import admin_socket
from async_client import AsyncClient
from response_handler import make_response_handler

if __name__ == "__main__":
    utils.assert_py_version()
    client_ctx = ctx.make_ctx(sys.argv[1])
    resp_handler = make_response_handler(client_ctx)
    client_ctx.set_up_logging()
    client = AsyncClient(response_handler = resp_handler,
                         auth_type = client_ctx.auth_type,
                         auth_creds = client_ctx.auth_creds
    )
    # Ensure that buckets are created before running other args
    utils.create_buckets(client_ctx.buckets, client_ctx.base_url,
                         client_ctx.auth_creds)

    #perf_init = admin_socket.perf_dump(client_ctx.admin_sock_path)
    #print(perf_init)
    ev_loop = asyncio.get_event_loop()
    #ev_loop.set_debug(True)
    ev_loop.run_until_complete(admin_socket.async_perf_dump(client_ctx.admin_sock_path))
    futures = [ asyncio.ensure_future(client.run(**kwargs)) for kwargs in client_ctx.arg_list ]

    ev_loop.run_until_complete(asyncio.gather(*futures))
    ev_loop.run_until_complete(admin_socket.async_perf_dump(client_ctx.admin_sock_path))

    #perf_final = admin_socket.perf_dump(client_ctx.admin_sock_path)
    #print(perf_final)
    resp_handler.print_stats()

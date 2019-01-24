#!/usr/local/bin/python3.5
import sys
import asyncio
from aiohttp import ClientSession, TCPConnector
from collections import Counter

import logging
import errno

def assert_py_version():
    import platform
    major, minor, _ = platform.python_version_tuple()
    assert int(major) >= 3 and int(minor) >=5

async def fetch(url, session):
    async with session.get(url) as response:
        return response

async def count_requests(url, session, counter):
    ret = await fetch(url, session)
    counter[ret.status] += 1

async def run(r):
    url = "http://localhost:8001"
    tasks = []

    # default connector limits to 100 connections to a single endpoint, we
    # don't want any client throttles
    c = Counter()
    async with ClientSession(connector=TCPConnector(limit=None)) as session:
        for i in range(r):
            task = asyncio.ensure_future(count_requests(url, session,c))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        # you now have all response bodies in this variable
        print(c)

def print_responses(result):
    print(result)

if __name__ == "__main__":
    assert_py_version()
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run(int(sys.argv[1])))
    loop.run_until_complete(future)

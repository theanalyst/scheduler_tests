import asyncio
import json
import socket
import struct
import logging

async def async_perf_dump(sock_path):
    reader, writer = await asyncio.open_unix_connection(path=sock_path)
    d = {"prefix": "perf dump"}
    bstr = json.dumps(d).encode() + b'\0'
    writer.write(bstr)
    await writer.drain()

    data_len_b = await reader.read(n=4)
    data_len = int.from_bytes(data_len_b, byteorder='big')

    perf_dump_b = await reader.read(data_len)
    perf_dump = json.loads(perf_dump_b)
    print(perf_dump['simple-throttler'])
    writer.close()

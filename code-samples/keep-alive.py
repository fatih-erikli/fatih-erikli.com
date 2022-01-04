import asyncio

async def redis_client():
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 6379)
    message = 'ping\n'
    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()
    await writer.wait_closed()

async def pubsub():
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 6379)
    message = 'subscribe messages\n'
    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    while True:
        data = await reader.read(100)
        print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()
    await writer.wait_closed()

asyncio.run(pubsub())
# asyncio.run(redis_client())

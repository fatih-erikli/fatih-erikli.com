import asyncio

async def handle_echo(reader, writer):
    data = await reader.read(65537)
    message = data.decode()
    writer.write(b'pong')
    await writer.drain()
    writer.close()

async def main():
    server = await asyncio.start_server(handle_echo, '127.0.0.1', 8888)
    async with server:
        await server.serve_forever()

asyncio.run(main())

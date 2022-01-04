import asyncio
import aioredis
import json

redis = aioredis.from_url("redis://localhost")

def http_document(content, status):
    return '\n'.join((
        f'HTTP/1.1 {status} OK',
        f'Content-Length: {len(content)}',
        'Content-Type: text/html',
        'Server: almost-an-nginx',
        '\r',
        content
    ))

def json_response(payload, status=200):
    return http_document(json.dumps(payload), status)

async def get_somethings():
    ...

async def post_somethings(body):
    await redis.incr(body['key'])
    hits = int(await redis.get(body['key']))
    return {
        'hits': hits,
    }

ROUTES = [
    ('get', '/somethings', get_somethings),
    ('post', '/somethings', post_somethings)
]

class Whirlwind:
    """
    Very simple http server works with AsyncIO.
    Todos:
        - Process the request headers
        - Parse querystrings
    """
    def __init__(self) -> None:
        self.routes = []
    
    def add_route(self, method, path, dispatcher):
        self.routes.append((method, path, dispatcher))
    
    def resolve_route(self, request_body):
        [first_line, *headers, request_body] = (request_body.split('\n'))
        [requested_method, requested_path, _] = first_line.split()
        for (method, path, dispatcher) in self.routes:
            if '?' in requested_path:
                [requested_path, *_] = requested_path.split('?')
            if method == requested_method.lower() and path == requested_path:
                return dispatcher, request_body

    async def serve(self, reader, writer):
        data = await reader.read(65537)
        body = data.decode()
        route = self.resolve_route(body)
        if route is None:
            writer.write(str.encode(json_response({'error': 'Not found.'}, 404)))
        else:
            dispatcher, request_body = route
            if request_body:
                result = await dispatcher(json.loads(request_body))    
            else:
                result = await dispatcher(request_body)
            writer.write(str.encode(json_response(result, 200)))

        await writer.drain()
        writer.close()

async def main():
    application = Whirlwind()
    application.add_route('get', '/somethings', get_somethings)
    application.add_route('post', '/somethings', post_somethings)
    server = await asyncio.start_server(application.serve, '127.0.0.1', 8888)
    async with server:
        await server.serve_forever()

asyncio.run(main())

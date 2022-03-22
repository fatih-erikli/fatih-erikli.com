AsyncIO is a built-in python library to write concurrent
code with a new language keywords "async" and "await'. AsyncIO landed
into python in 3.3 version. Since the Python2 is no longer supported,
AsyncIO will be our swiss army knife to handle:

 - Network operations
 - Subprocesses
 - Distributed tasks

And many more.

### What does concurrent mean?
In computer science, concurrency means the ability to execute different parts of the 
program simulatanoeusly. In concurrent programming, we write our functions as partial units
that can be executed as parallel (each of them working at the same time), or synchronously
(each of them working in a following order, not at the same time), without affecting the
final result.

Concurency tools helps us to make an abstraction to write functions can be worked in a
parallel way or in a sync way. The piece of function or code will not be aware that 
it is working in a parallel or in a synchronous order.

<figure>
<img src="public/concurrent-task-execution.svg" style="width: 100%" />
<figcaption>Parallel vs Synchronous execution</figcaption>
</figure>

In the figure above, we see the same tasks set (could be a whole function)
running as concurrent (in parallel) and synchronously. As the time moves,
the tasks in synchronous order moves in parallel to the time. Only one
task is running at a moment; it other words, a one task needs to be ran
in order to execute the next function.

In concurrent version of the implementation, all the tasks starts to run
at the same moment, and some tasks are finished before some others tasks.

The syncronous way of programming is the way of we program the things from the
very beginning. What we have learned until this time was synchronous way of programming.
There is no something special to be done in order to achieve this style programming.

In concurrent functions, we need special data types and structure to check if a task
is running, failed, or completed. Also we need to be able to wait until a specific task
or a task set to be completed. In Python programming language, with 3.3. version,
`async` and `await` was keywords introduced for handling concurrent operations.

### How does the HTTP protocol work
We are going to create an HTTP server to play with `AsyncIO` library. Network operations
are the most popular use case for concurrent operations. Because we want to serve our
functions to as many as users possible at a time. One long lasting process should not
block the execution of functions for other users. This is a perfect use case for examples.

<figure>
<img src="public/http-diagram.svg" style="width: 100%" />
<figcaption>Very simple HTTP workflow</figcaption>
</figure>

### Streams
Streams are data structures to work with network connections. An http server 
and an http request basically corresponds the two pairs of an socket operation;
one pair is sending an information, the other pair is receiving the information.

HTTP server is a TCP server running on a specific port. The default HTTP port is `:80`.
When you connect to a web-site, you connect to the server is running on `:80` port 
on a machine. You don't see the `:80` port, because it is default. If you try to connect
to a different port, you need to specificy the port you want to connect with a double-colon;
as an example: `https://python.org:8888`, even though this is not a correct use-case in practice, because
the default port for an HTTPS connection is `443`.

Let's go step by step and create a TCP server first.

```python
import asyncio

async def pong(reader, writer):
    data = await reader.read(100)
    writer.write(b'pong')
    await writer.drain()
    writer.close()

async def main():
    server = await asyncio.start_server(pong, '127.0.0.1', 8888)
    async with server:
        await server.serve_forever()

asyncio.run(main())
```

We have created a ping pong application. When a client send a message to our server,
we will respond with `pong`. It's a simple application.

### How do we connect to a TCP server?

Let's go with telnet application first; we don't
serve with an http response yet.

```
$ my-blog % telnet 127.0.0.1 8888
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
```
Telnet has it's own way of communication as you can notice in response.
We will write "ping" here.

```
ping
pong
Connection closed by foreign host.
```

We received a pong response. This is how we communicate with servers. What happens when we
open this URL with a browser? The answer is; most of the modern browsers will show an error
message to the user indicating the http response is not valid.

We need to prepare a well-formatted http response to the user.

```python
def http_document(content, status_code):
    return '\n'.join((
        f'HTTP/1.1 {status_code} OK',
        f'Content-Length: {len(content)}',
        'Content-Type: text/html',
        'Server: almost-an-nginx',
        '\r',
        content
    ))

def prepare_html(content, status_code=200):
    html = f'<!DOCTYPE html>{content}'
    return http_document(html, status_code)
```
We will respond in that way. We need to update our server function accordingly:

```python
async def serve(reader, writer):
    data = await reader.read(100)
    writer.write(str.encode(prepare_html())) # this is where we prepare the response
    await writer.drain()
    writer.close()
```

We respond with the same http response does not matter where the current user landed.
The browser sends us a message which is formatted as same as http response. This
message is defined by HTTP protocol.

So the HTTP protocol has two pairs; one is Request and the other one is Response.
We prepared the http response. Now we need to process the http request.
We have not opened the message package in our server yet. Let's go further.

```python
async def serve(reader, writer):
    data = await reader.read(100)
    message = data.decode()
```
The message is the http request itself. Lets dive into it.

```
GET /favicon.ico HTTP/1.1
Host: 127.0.0.1:8888
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X
```
It will be something like that. Did you notice something? The User-agent
is cropped. Why is that happening? Answer is, we read only 100 bytes of the
message.

There is an http server implementation in Python's builtin library. It reads
`65537` bytes of the incoming message, which is the max limit that the server
can interpret. There is no limit; it is defined by your needs;
although the http request will not be greather than that specified number in practice.
The server respond's with `REQUEST_URI_TOO_LONG` http response if the 
receive message is greather than that number.

I trust Python's code so I will use the same size. I updated the server
accordingly and received the full http request message.

```
GET / HTTP/1.1
Host: 127.0.0.1:8888
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0)
Accept: text/html,application/xhtml+xml,application/xml;
Accept-Language: en-US,en;
```
The http request starts with the http method performed by user. Browser makes
the request always with `GET` method when you visit a URL. Other methods has
different use cases; such as form submissions. When the user makes a form
submission; it's sent as `POST` method. It does not have to be `POST` necessarily;
although it is practical and convenient handle the form submissions with `POST` method,
because the browser is informing the user like "Do you really submit the form again?"
when they refresh the page after clicking submit button.

The second parameter after the method is the path; which is the most important
parameter in our case; it specifies the path which the user wants to land on.
We can simply assume that `/` means the user is on the home-page. The third parameter after the path is the HTTP version. Currently browsers
send HTTP/1.1 version.

It's not hard to parse that document; most of the cases we only do need to know the method
of request, the path, and the request body depending on the request method.

```python
def handle_post(method, request_body):
    import json
    input_json = json.loads(request_body)
    message = input_json['message']
    return prepare_html(f'<h3>{message}</h3>')

ROUTES = {
    '/post-something': handle_post,
    '/':
        lambda method, request_body:
            prepare_html('<h3>Home page</h3>'),
    '/about':
        lambda method, request_body:
            prepare_html('<h3>About page</h3>')
}

async def serve(reader, writer):
    data = await reader.read(65537)
    message = data.decode()
    [first_line, *headers, request_body] = (message.split('\n'))
    [method, path, version] = first_line.split()

    handler = ROUTES.get(path)

    if handler is None:
        writer.write(str.encode(prepare_html('Not found', 404)))
    else:
        writer.write(str.encode(handler(method, request_body)))

    await writer.drain()
    writer.close()
```

Simply we created a router. Our web server is able to handle the request methods
and requested paths by the user. The last line of the http request is the request body;
which is the payload submitted by the client.

In REST APIs, usually the request body is sent as a stringified JSON document.
We can use python's json module to parse that JSON document.

When the user calles the `/post-something` with a valid json body; we respond
an html document with the message specified in that json package.

I use `httpie` package to send http commands via command lines. Here's how
I am testing my `/post-something` endpoint.

```
$ http post "127.0.0.1:8888/post-something" message="lorem ipsum dolor sit amet"
HTTP/1.1 200 OK
Content-Length: 50
Content-Type: text/html
Server: almost-an-nginx

<!DOCTYPE html><h3>lorem ipsum dolor sit amet</h3>
```

In practice, we need to respond with a JSON for an endpoint which is expecting
a json body to process.

It is simple. We will create a different function instead of `prepare_html`.

```python
def json_response(payload):
    return http_document(json.dumps(payload), 200)
```

We call the same endpoint; as you will notice we respond with stringified json
instead of an html document.
```
$ http post "127.0.0.1:8888/post-something" message="lorem ipsum dolor sit amet"
HTTP/1.1 200 OK
Content-Length: 41
Content-Type: text/html
Server: almost-an-nginx

{
    "message": "lorem ipsum dolor sit amet"
}
```

Happy hacking.

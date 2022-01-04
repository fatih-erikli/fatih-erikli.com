In my previous blog-post, I created a simple http server that calls a
redis method; increases the specified key with request body
in the redis store.

 - <a href="whirlwind.html">Whirlwind: HTTP server boilerplate for AsyncIO</a>
 - <a href="creating-a-web-server-in-asyncio.html">Creating a web-server in AsyncIO</a>

In this article, I will share how the communication between our python
process and redis happens.

Lets dive into it.

 - Our HTTP Server is a TCP server which is running on 80 port.
 - Redis is a TCP server which is running on 6379 port.

We are able to create a server and client with built-in AsyncIO library.
In practice, we are sending a TCP package to the redis-server
and waiting a response for the message that we have sent. This is all.

Using a third party library is a trade-off. Each package that you install
separately increases the tech-debt of your project. I think, instead of
increasing the tech-debt and using an extra module to interact with a
database or key-value store such as redis; we can try to talk to it
as same as how we talk to other TCP clients.

Let's try. We will use telnet. Redis is running on 6379 port.
```
$ telnet 127.0.0.1 6379
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
ping
+PONG
```
Wow it works. It seems like a magic :) But it is not a magic.
This is how the database drivers work under the hood.

Lets try to send a message and listen for a response in AsyncIO.

```python
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

asyncio.run(redis_client())
```

Let's run it.

```
python3 my-redis-client.py
Send: 'ping\n'
Received: '+PONG\r\n'
Close the connection
```

It worked!

Okay, now lets go further. There are some commands in redis; which just responds
to you and closes the connection; and there are others; keeps the stream alive.

What are they?
```
INCR my-key
1

INCR my-key
2

INCR my-key
3
```

Each time you call the INCR method; redis increases the number that you specified
with your key and responds with the current value and you forget about the rest.

```
subsribe messages
... some time have passed
hello
... some time have passed
... some time have passed
... some time have passed
hello
```

Redis support pub-sub which is a functionality that allows you to listen to
a specific key; and prompts you when there is a message left to that specific
key. Lets create another connection with telnet and play with it.

```
$ telnet 127.0.0.1 6379
Connected to localhost.
Escape character is '^]'.
publish messages hey
```

You will notice that in the connection when you subscribe, you will
receive the message "hey" which is sent by the other connection.

```
subsribe messages
... some time have passed
hello
... some time have passed
... some time have passed
... some time have passed
hello
... some time have passed
hey <- WATCH IT OUT :)
```

This functionaliy allows us to create

 - Chat servers
 - Message queues
 - Many more

As you can see with just a simple set of commands we were able to interact
with redis and get our job done.

Here's how I connect to redis-pubsub with AsyncIO.


```python
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
```

Lets run the script.

```
$ python message-queue.py
Send: 'subscribe messages\n'
Received: '*3\r\n$9\r\nsubscribe\r\n$8\r\nmessages\r\n:1\r\n'
Received: '*3\r\n$7\r\nmessage\r\n$8\r\nmessages\r\n$3\r\nhey\r\n'
```

Lets send a message to "messages" channel.
```
$ telnet 127.0.0.1 6379
Connected to localhost.
Escape character is '^]'.
publish messages "can you hear me"
```

Watch it out!
```
$ python message-queue.py
Send: 'subscribe messages\n'
Received: '*3\r\n$9\r\nsubscribe\r\n$8\r\nmessages\r\n:1\r\n'
Received: '*3\r\n$7\r\nmessage\r\n$8\r\nmessages\r\n$3\r\nhey\r\n'
Received: '*3\r\n$7\r\nmessage\r\n$8\r\nmessages\r\n$15\r\ncan you hear me\r\n'
```
We have received the message :)

Happy hacking!

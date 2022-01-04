I have been trying serverless computing platforms in last years. Basically these platforms allows you
to publish functions and execute them periodically, or by triggering it
with an HTTP request.

What I have tried so far:

 - Amazon Lambda
 - CloudFlare
 - Serverless Framework (This is not a platform; but a framework that helps you to publish your architecture in
 any platform)

 In this blog post I will share an example in CloudFlare. Why so?

  - It's free
  - I find the control panel more user and developer friendly
  - They have a strong development community

We will create a user authentication by using Cloudflare workers.

Let's write down what we are going to build first. We will have three API endpoints.

  - Registration
  - Login
  - Auth

Registration and login is obvious. Auth endpoint will help us to authenticate user
after the login process. We will store the `auth_token` provided us from the login or
registration endpoint; and reuse them later (when the user refresh the page) to reauthenticate
them again.

### Persistance layer

First of all; we need to create a KV store; which is the database (or key-value store) of CloudFlare.

<https://developers.cloudflare.com/workers/runtime-apis/kv>

You can create a KV store on cloudflare panel; or you can create it with <a href="https://developers.cloudflare.com/workers/cli-wrangler">wrangler</a>
command line tool.

Let's start with Registration endpoint.

```javascript
const sha256 = require('crypto-js/sha256')
const cryptoJs = require('crypto-js')
const jwt = require('jsonwebtoken')

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

/**
 * Simple authentication
 * @param {Request} request
 */
async function handleRequest(request) {
  const url = new URL(request.url)
  const { pathname } = url
  let response = { pathname }
  switch (pathname) {
    case '/register': {
      const { username, password } = await request.json()

      const user = await YOURKVSTORE.get(`user:${username}`)
      if (user) {
        response = {
          error: 'User exists.',
        }
        break
      }

      const hashedPassword = sha256(password).toString(cryptoJs.enc.Hex)
      // this is important
      await YOURKVSTORE.put(`user:${username}`, hashedPassword)

      const token = jwt.sign({ username }, TOKEN_KEY, {
        expiresIn: '2h',
      })

      await YOURKVSTORE.put(`user_token:${token}`, username)

      response = {
        token,
      }
      break
    }
  }
  return new Response(JSON.stringify(response), {
    headers: {
      'content-type': 'text/json'
    },
  })
}
```

This is how an event-driven computing-ready function looks like in any platform.
It is not so different than creating a controller in a http or Rest API framework;
we have a request body and we create a response with that.

### Most important thing
You cannot store the user's password in your database. You need to hash them with a
hashing algorithm; such as sha256, and save them.

When the user types username and password in login page; we need to hash the
password provided by user; and match the hashed pairs, instead of raw password.
This is very important.

After the hashing algorithm; we use JWT (JSON Web Token) to create a token
that we can authenticate the user without username and password.

```javascript
/**
 * Simple authentication
 * @param {Request} request
 */
async function handleRequest(request) {
  const url = new URL(request.url)
  const { pathname } = url
  let response = { pathname }
  switch (pathname) {
    case '/login': {
      const { username, password } = await request.json()
      const hashedPassword = sha256(password).toString(cryptoJs.enc.Hex)
      const storedPassword = await VECTORIAL.get(`user:${username}`)
      if (storedPassword === hashedPassword) {
        const token = jwt.sign({ username }, TOKEN_KEY, {
          expiresIn: '2h',
        })

        await VECTORIAL.put(`user_token:${token}`, username)

        response = {
          token,
        }
      } else {
        response = {
          error: 'Invalid credientials.',
        }
      }
      break
    }
    case '/auth': {
      const { token } = await request.json()

      let user

      try {
        user = jwt.verify(token, TOKEN_KEY)
      } catch (e) {
        response = {
          error: 'Invalid signature.',
        }
      }

      if (user) {
        const username = await VECTORIAL.get(`user_token:${token}`);
        if (!username) {
          response = {
            error: 'Invalid signature.',
          }
        } else {
          response = {
            username,
          }
        }
      }
      break
    }
    case '/register': {
      const { username, password } = await request.json()

      const user = await VECTORIAL.get(`user:${username}`)
      if (user) {
        response = {
          error: 'User exists.',
        }
        break
      }

      const hashedPassword = sha256(password).toString(cryptoJs.enc.Hex)
      await VECTORIAL.put(`user:${username}`, hashedPassword)

      const token = jwt.sign({ username }, TOKEN_KEY, {
        expiresIn: '2h',
      })

      await VECTORIAL.put(`user_token:${token}`, username)

      response = {
        token,
      }
      break
    }
  }
  return new Response(JSON.stringify(response), {
    headers: {
      'content-type': 'text/plain',
    },
  })
}
```

I wrote the code as clean as possible to not complicate things by explaining
them with my English :)

### CORS settings

We have created the API with workers. There's one thing needs to be done in the code
in order to connect them via a browser; CORS (Cross Origin Resource Sharing) settings.
Basically we need to whitelist a domain or url that we are going to connect to
the API we have created.

```
async function handleRequest(request) {
  // ...
  return new Response(JSON.stringify(response), {
    headers: {
      'content-type': 'text/plain',
      'Access-Control-Allow-Origin': '*', // Whildcard allows all domains
      'Access-Control-Allow-Methods': 'GET,HEAD,POST,OPTIONS',
      'Access-Control-Max-Age': '86400',
    },
  })
}
```

Yon can type the domain instead of the asteriks whildcard.

### Deployment

I use <a href="https://developers.cloudflare.com/workers/cli-wrangler">wrangler</a> to manage
my workers. You can write and publish them on cloudflare dashboard as well. I find command-line
tool more useful when you develop something more complicated.

```
$ my-cloudflare-worker % wrangler publish
✨  Built successfully, built project size is 213 KiB.
✨  Successfully published your script to
https://vectorial-cloudflare-worker.fatih-erikli.workers.dev

```

Let's try our endpoints.

I am going to register myself.

```
$ http post "https://1.fatih-erikli.workers.dev/register" username=benfatih password=hello
HTTP/1.1 200 OK
Access-Control-Allow-Methods: GET,HEAD,POST,OPTIONS
Access-Control-Allow-Origin: *
Access-Control-Max-Age: 86400
CF-RAY: 6b77697eab936b36-AMS
Connection: keep-alive
Content-Encoding: gzip
Content-Type: text/plain
Date: Thu, 02 Dec 2021 20:47:45 GMT
NEL: {"success_fraction":0,"report_to":"cf-nel","max_age":604800}
Server: cloudflare
Transfer-Encoding: chunked
Vary: Accept-Encoding

{
    "token": "Wohoo yay, it worked. Of course I cropped my auth token. Its mine"
}
```

It worked :) We are going to authenticate ourselves with the token returned by our endpoint.

```
$ http post "https://1.fatih-erikli.workers.dev/auth" token=mytoken
HTTP/1.1 200 OK
Access-Control-Allow-Methods: GET,HEAD,POST,OPTIONS
Access-Control-Allow-Origin: *
Access-Control-Max-Age: 86400
CF-RAY: 6b776bd4edcb1ead-AMS
Connection: keep-alive
Content-Length: 23
Content-Type: text/plain
Date: Thu, 02 Dec 2021 20:49:20 GMT
NEL: {"success_fraction":0,"report_to":"cf-nel","max_age":604800}
Server: cloudflare
Vary: Accept-Encoding

{
    "username": "benfatih"
}

```

Yay. We are able to authenticate with an authentication token instead of username and password.

That's all :)

Happy hacking!
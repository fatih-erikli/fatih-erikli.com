Test driven development is the way of developing a software based
on the tests you have initially written. In traditional way of 
development, we create the application, test them manually,
and create tests or ignore them. In test-driven approach,
you create the tests and run them first, see them failing,
and start implementing the application by seeing the
tests results are passing one by one incrementally.

I think worker-based web applications are perfect use cases
for test driven software development. Because we are actually
not creating a web-application, but we are developing functions
which is taking a Request parameter which holds some information
about the client (user) who is visiting your web page.

In order to test worker-based web applications, we need to mock (mimic)
a Request object. Basically the request is originally a plain text;
so there is not so much things needs to be done, but of course it needs
to be developed based on standards.

In Cloudflare, I use `service-worker-mock`, which is an npm package
developed by Cloudflare.

It helps me to develop my application locally, without even
running them with a local development server. So it speeds
up the development process drastically.

```javascript
import { handleRequest } from '../src/server'
import makeServiceWorkerEnv from 'service-worker-mock'

declare var global: any

describe('server side rendering', () => {
  beforeEach(() => {
    Object.assign(global, makeServiceWorkerEnv())
    jest.resetModules()
  })
}
```

This is how the test case looks like. We mock the cloudflare
workers with makeServiceWorkerEnv function.

So I continue writing the tests.

```javascript
describe('server side rendering', () => {
  beforeEach(() => {
    Object.assign(global, makeServiceWorkerEnv())
    jest.resetModules()
  })

  test('server side routing homepage', async () => {
    const result = await handleRequest(new Request('/', { method: 'GET' }))
    expect(result.status).toEqual(200)
    const text = await result.text()
    expect(text).toContain('<div id=\"root\"><div>1</div></div>')
  })

  test('server side routing about page', async () => {
    const result = await handleRequest(new Request('/about', { method: 'GET' }))
    expect(result.status).toEqual(200)
    const text = await result.text()
    expect(text).toContain('<div id=\"root\"><div>about</div></div>')
  })
})
```

I see them failing when I run the test suite by npm run test.

```
Test Suites: 1 failed, 1 total
Tests:       2 failed, 2 total
Snapshots:   0 total
Time:        0.91 s, estimated 1 s
Ran all test suites.
```

This is totally okay. We need to start with the failing
test cases first. It's always good idea to start 
thinking about the errors first. That's why test
driven development provides us to more solid
development environment.

I implement my application.

```typescript
type ServerSideRenderingProps = {
  pathname: string;
};

const ServerSideRendering = ({ pathname }: ServerSideRenderingProps) => {
  const router = useUniversalRouter(pathname, getRoutes());
  return (
    <html>
      <head>
        <title>Server Rendered App</title>
      </head>
      <body>
        <div id="root">
        {router.match === 'home' && (<Home />)}
        {router.match === 'about' && (<About />)}
        </div>
        <script src="client.js" />
      </body>
    </html>
  );
}

export async function handleRequest(request: Request): Promise<Response> {
  const url = new URL(request.url)
  const { pathname } = url
  let html = ReactDOMServer.renderToString(
    <ServerSideRendering pathname={pathname} />
  );
  return new Response('<!DOCTYPE html>' + html, {
    headers: {
      "content-type": "text/html;charset=utf-8",
    },
  })
}
```

And run the tests.

```
 PASS  test/server.test.ts
  server side rendering
    ✓ server side routing homepage (4 ms)
    ✓ server side routing about page (2 ms)

Test Suites: 1 passed, 1 total
Tests:       2 passed, 2 total
Snapshots:   0 total
Time:        0.929 s, estimated 1 s
Ran all test suites.
```

And they are working.

Happy hacking!
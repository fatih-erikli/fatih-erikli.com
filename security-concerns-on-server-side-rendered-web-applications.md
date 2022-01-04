In the current state of web development, the line between backend and frontend
development has become almost invisible. The reason of that is we started to use
Javascript for both client-side and server-side after NodeJS. And furthermore,
we started to render the same components for both client-side and server side.

I think creating the html output of a React component before the javascript execution
is a great idea for:

- SEO (Search engines can read Javascript, but html always has a priority by nature)
- Performance (The page is rendered as a static web page)
- Semantics (HTTP is a hyper-text transfer protocol. We should serve human-and-machine readable content)

I believe it is going to be the way that we build we applications in nearest future.

I have tried creating server-side rendering applications with frameworks such as
Next and Nuxt, and I also created them manually by using ReactDOMServer. Using a
framework is the easiest option, but when it comes to the production-ready web
applications, you face with issues such as

- FOUC (Flush of unstyled content)
- Routing. Unfortunately, React-router is the most fragile library of our ecosystem
- Security concerns

For that reason, I chose to create server side applications from the scratch; to make
draw a stronger line between frontend and backend.

When you create a build with Webpack, you are creating a compressed bundle of all the Javascript
or Typescript modules and the environment variables of you have imported in your entry point. When
you bundle a Javascript module that you are connecting to your database, you are also exporting
your database location, username, and password to those minified javascript files. This is why
drawing a strong line between frontend and backend is **important**.

It is important to know which module should be exported to client-side and which one should 
be internal. When you do a check as isServerSide(), it is more likely that you are going
to forget that you are using and exporting a function should be kept on the server-side.

### You should create a separate bundle for client.

Here's how I am creating a different bundle for client and a server (worker).

```javascript
const path = require('path')
const { CleanWebpackPlugin } = require('clean-webpack-plugin')
const { WebpackManifestPlugin } = require('webpack-manifest-plugin')


module.exports = {
  entry: {
      'worker': './src/index.ts', // this is backend
      'client': './src/client'    // this is frontend
  },
  output: {
    filename: '[name].js',
    path: path.join(__dirname, 'dist'),   // you should not serve "dist" directory.
  },
  // ...
}
```

Important. You should not serve the `dist` directory. It also includes your worker
file (which is backend in our case) and all the environment variables and confidential
information. You should only server "client" bundle.

I already shared a blog post about it. I use Cloudflare for creating my web applications.
Here's how I share the client file:

```javascript
import { getAssetFromKV } from "@cloudflare/kv-asset-handler"
import { handleRequest } from "./handler"

addEventListener("fetch", (event: any) => {
  event.respondWith(handleEvent(event))
})

async function handleEvent(event:any) {
  const url = new URL(event.request.url)
  const { pathname } = url;

  switch (pathname) {
    // this is the endpoint that I handle static files
    case "/client.js":
    case "/client.js.map":
      return await getAssetFromKV(event)

    // this is all. rest of it is server-side rendered application.
    default:
      return handleRequest(event.request)
  }
}
```

Here's a super-simple server side rendered application example.

### Client-side
There's two methods in React's DOM lifecycle.

- render (Create the html structure from scratch)
- hyrdate (Applies the React components into plain html)

We will use `hyrdate` instead of rendering the react application from scratch.

```javascript
import React from 'react';
import ReactDOM from "react-dom";
import { BrowserRouter } from "react-router-dom";
import { Home } from "./handler";

ReactDOM.hydrate(
  <Home />,
  document.getElementById('root')
);
```

### Server-side
And this is how the server side rendering is going to be like

```javascript

import React, { useState } from 'react';
import ReactDOMServer from "react-dom/server";
import { StaticRouter } from "react-router-dom/server";

export async function handleRequest(request: Request): Promise<Response> {
  const html = ReactDOMServer.renderToString(
    <Base />
  );
  return new Response('<!DOCTYPE html>' + html, {
    headers: {
      "content-type": "text/html;charset=utf-8",
    },
  })
}
```
Base component is the component that you render plain page. You can
use your presentational components, which is responsible for
presenting your data.

Here's a blog post you can read more about presentational and container components:

<a target="_blank" href="https://medium.com/@dan_abramov/smart-and-dumb-components-7ca2f9a7c7d0">Presentational and Container Components</a>

So, you should not expose your Container components.

This is all.
Happy hacking :)
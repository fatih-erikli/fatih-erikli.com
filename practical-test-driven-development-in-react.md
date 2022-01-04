Previously I wrote a blog post about creating a worker-based http api
with test-driven approach. In this blog post, I will share my experiences
about going test-driven development for for building user interfaces.
**Edit: I was wrong. Dispatching all the events from a single place sounds
good at the beginning but it makes the development cycle a total mess
after awhile.**

It is not so easy to go test-driven development for user interfaces for many factors.

 - It is not easy to mock user interactions such as Mouse or Touch events
 - It's hard to define the test cases and implement them

For that reason I tried to implement the test cases in a semi-automated way.
I like Test-driven approach not for the test cases, but the way of developing
the applications by seeing them failing first and implementing it. I develop one
of my side project with that approach and I find it very useful.

I'm going to share some code pieces.

### Testability

<s>First of all, we need to abstract all the user interactions and events in the application
in order to make them testable. This is not a mandatory step, you can also use `dispatchEvent`
function to trigger an event, but I find creating a mediator layer between the user 
and your application very useful. 

<a href="https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/dispatchEvent" target="_blank" rel="nofollow">*dispatchEvent function on MozillaDev.</a>

We need an EventEmitter class. There's one in NodeJS library but you can't use it on your browser.
You need a browserify or something like that, or you can do it in hand-written way and keep it
integrated with your coding style.

```javascript

import { Event, EventCallback, EventListener, IEventEmitter } from "../types/Events";
import { neg } from "../utils/functional";

export class EventEmitter implements IEventEmitter {
  listeners: [key: string, callback: (message: any) => void][];

  constructor() {
    this.listeners = [];
  }

  addEventListener(key: string, callback: (message: any) => void): (() => void) {
    const eventKeys = key.split(String.fromCharCode(32));
    for (const key of eventKeys) {
      this.listeners.push([key, callback]);
    }
    return () => {
      for (const key of eventKeys) {
        this.removeEventListener(key, callback);
      }
    };
  }

  removeEventListener(key: string, callback: EventCallback): void {
    const predicate = (listener: EventListener) => listener[0] === key && listener[1] === callback;
    const index = this.listeners.findIndex(predicate);
    if (index !== -1) {
      this.listeners = this.listeners.filter(neg(predicate));
    }
  }

  emit(event: Event) {
    for (const [listenerKey, listenerCallback] of this.listeners) {
      if (listenerKey === event.name) {
        listenerCallback(event);
      }
    }
  }
}

```

We are going to send the browser events via that class. I use React. I created
a hook for that. I am going to share that one as well.

```javascript
import { useEffect } from "react";
import { EventEmitter } from "../classes/EventEmitter";
import { Vector } from "../classes/Vector";
import { EventHandler } from "../types/Events";

export const useMediatedEventsHandler = (eventEmitter?: EventEmitter) => {
  useEffect(() => {
    const interactionHandler = (type: string) => (event: any) => {
      if (!eventEmitter) return;
      switch (type) {
        case "click":
        case "mousedown":
        case "mouseup":
        case "mousemove":
          eventEmitter.emit({
            name: type,
            position: Vector.fromEvent(event),
            target: event.target.getAttribute("id"),
          });
          break;
        case "touchstart":
        case "touchmove":
          eventEmitter.emit({
            name: type,
            position: Vector.fromEvent(event.touches[0]),
            target: event.target.getAttribute("id"),
          });
          break;
        case "touchend":
          eventEmitter.emit({
            name: type,
            position: Vector.Invisible(),
            target: event.target.getAttribute("id"),
          });
          break;
      }
    };

    const events = ["mousedown", "mouseup", "mousemove", "touchstart", "touchmove", "touchend", "click"];
    const handlers: EventHandler[] = [];

    for (const event of events) {
      const handler = interactionHandler(event);
      document.body.addEventListener(event, handler);
      handlers.push(handler);
    }
    
    return () => {
      for (let index = 0; index < events.length; index++) {
        const eventName = events[index];
        const handler = handlers[index];
        document.body.removeEventListener(eventName, handler);
      }
    };
  });
};
```

As you can see in the hook function, I normalize the touch and mouse events
and firing them in a payload that I struct.
</s>
Let's start defining our test cases.

```
const testCases: TestCase[] = [
  [
    "should-start-with-empty-canvas",
    (result: TestState, eventEmitter: EventEmitter) => (
      <Application
        eventEmitter={eventEmitter}
        title={`Test case: Start (${result})`}
      />
    ),
    (document) => document.querySelectorAll(".Canvas").length === 1,
  ],
  [
    "move-button-should-be-disabled-first",
    (result: TestState, eventEmitter: EventEmitter) => (
      <Application
        eventEmitter={eventEmitter}
        title={`Test case: Start (${result})`}
      />
    ),
    (document) => document.querySelectorAll("#move-button:disabled").length === 1,
  ],
  [
    "should-switch-to-drawing-mode-when-click-draw",
    (result: TestState, eventEmitter: EventEmitter) => (
      <Application
        eventEmitter={eventEmitter}
        title={`Test case: Start (${result})`}
      />
    ),
    (document, eventEmitter) =>
      new Promise((resolve) => {
        setTimeout(() => {
          eventEmitter.emit({
            name: "click",
            position: Vector.Invisible(),
            target: "draw-button",
          });
        }, 200);
        setTimeout(() => {
          resolve(!!document.querySelector("#draw-button:disabled"));
        }, 300);
      }),
  ],
]
```

First two test cases are pretty simple. In the third test case,
we have a complex user interaction for testing. This is
pretty much the same as Jest's (testing framework) async
test cases. We resolve a Promise when the test is running,
and rejecting it if the test case is failing.

The test case interface looks like that

```javascript
import { ReactElement } from "react";
import { IEventEmitter } from "./Events";

export type TestState = "init" | "pending" | "failed" | "success";

export type TestCase = [
  name: string,
  test: (result: TestState, eventEmitter: IEventEmitter) => ReactElement,
  testCase: (document: HTMLDivElement, eventEmitter: IEventEmitter) => boolean | Promise<boolean>
];
```

And here's how do I run them.

```javascript
function App() {
  const router = useUniversalRouter(window.location.hash, [
    ["", "application"],
    ["/test-case/:testCase", "test-case"],
  ]);

  let testComponent: any;
  let testRuntime: any;

  if (router.match === "test-case") {
    const testCase = testCases.find(
      (testCase) => testCase[0] === router.arguments[1]
    );
    if (testCase) {
      testComponent = testCase[1];
      testRuntime = testCase[2];
    }
  }

  const [testResult, setTestResult] = useState<TestState>("init");

  const eventEmitter = useRef<EventEmitter>();
  const domRef = useRef<HTMLDivElement>(null);

  useMediatedEventsHandler(eventEmitter.current);

  useEffect(() => {
    if (testResult === "init") {
      setTestResult("pending");
    }

    if (!eventEmitter.current) {
      eventEmitter.current = new EventEmitter();
    }

    if (testRuntime && domRef.current) {
      const result = testRuntime(domRef.current, eventEmitter.current);
      
      if (result instanceof Promise) {
        result
          .then((result) => {
            setTestResult(result ? "success" : "failed");
          })
          .catch(() => {
            setTestResult("failed");
          });
      } else {
        setTestResult(result ? "success" : "failed");
      }
    }
  });

  return (
    <div className="Container" ref={domRef}>
      {router.match === "application" && eventEmitter.current && (
        <Application eventEmitter={eventEmitter.current} title="Empty canvas" />
      )}
      {router.match === "test-case" &&
        eventEmitter.current &&
        testComponent &&
        testComponent(testResult, eventEmitter.current)}
    </div>
  );
}
```

I use a simple router that I call <a target="_blank" href="https://github.com/fatih-erikli/universal-router">universal-router</a>. 
Application starts as usual in home page. I have a different route for test cases
and I check them by going in URL.

```
http://localhost:3001/#/test-case/move-button-should-be-disabled-first
```

This is all.
Happy hacking!

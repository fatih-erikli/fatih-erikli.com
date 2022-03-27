Pattern matching is a functional programming concept
to handle conditional code branches based on the
structured the date you are processing 
in a declarative way. Pure functional languages such as
Haskell and Erlang supports pattern matching and
most of the times it is the only way of writing a
conditional code. <s>We don't have pattern matching
in Javascript or Python, but with some syntactic sugar
and precompilers such as Typescript, we can use
pattern matching.</s> Edit: It's not a good idea. I don't recommend to implement a pattern matching in Typescript. We need to be
patient until the time pattern matching will be possible with Javascript. 

I found a library called "ts-pattern". I tried, and it
works like a charm. By desing, pattern matching runs
on run-time, but it is also taking some advantages
of Typescript to check your types before compiling them.

It also warns you when you have a missing case
in your pattern matching structure and I think it is
super useful when you have to deal with complex
user interactions and multiple application modes.

I am going to share a code piece and I think it will worth
a thousand words to explain it.

```javascript
useEffect(() =>
    eventEmitter.addEventListener("all", (event) => {
      match<[EventName, EventTarget, DrawingMode]>([event.name, event.target, canvasState.mode])
        .with(["click", "canvas-area", "move"], () => {
          setCanvasState("mode", "start");
        })  
        .with(["click", "draw-button", "move"], () => {
          setCanvasState("mode", "start");
        })
        .with(["click", "move-button", "start"], () => {
          setCanvasState("mode", "move");
        })
        .with(["click", "canvas-area", "start"], () => {
          console.log("create a shape")
        })
        .with(["mousedown", __, __], (match) => {})
        .with(["mouseup", __, __], (match) => {})
        .with(["canvasmove", __, __], (match) => {})
        .with([__, __, __], (match) => {
          console.log('no matching pattern', match);
        })
        .run();
    })
  );
```

This is a useEffect example in React. We listen to all the
user events, combining them with the related part of the application,
and the application mode (it is very contextual for a vectoral drawing library, but I think it is understandable)
and creating some conditional branches.

We also use `__` whildcard pattern to fulfill missing parts of our patterns.

Here's the github repository of `ts-pattern`.

<a target="_blank" rel="nofollow" href="https://github.com/gvergnaud/ts-pattern">https://github.com/gvergnaud/ts-pattern</a>

### Edit: I implemented a minimal pattern matching library for Typescript

I noticed that the runtime was a bit expensive to match all the cases with ts-pattern
and I worked a little bit to make it faster and I managed to optimize.

I published the library on github and npm called "pattern-select":

That's it.
Happy hacking!
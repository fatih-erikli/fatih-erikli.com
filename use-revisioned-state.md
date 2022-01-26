I tried to implement a revisionable state container for the UI state
in order to provide a functionality to undo and redo an action on an application.
There's a lot of ways to do that, I tried to implement the simplest one.
I created a React hook that diffs the previous state and create a change log for it.
That change log includes the added, updated, and removed keys of objects and arrays. I keep 
the updated values with the previous one, so I can easily invert a change and revert it back. 

Here's how does the Change log type looks like.

```typescript
export type ChangeLog<S> = {
  hasChange: boolean;
  added: [path: string, value: any][];
  removed: [path: string, value: any][];
  changed: [path: string, value: any, previousValue?: any][];
  updated?: [value: S, previousValue: S];
};
```

The path of the changed value is separated by "." dot. `users.0.name` corresponds
to the `users[0].name`.

### Reverting the history

useRevisionedState hooks returns with the `history` collection and `revert` function.

You can undo the last change by reverting the last change. It will create
an another change log. If you want to revert the whole state, you need to reverse the history and pass
it to the revert function.

```typescript
<button
  onClick={() =>
    const back = [...history];
    back.reverse();
    revert(back);
  }
>
  Revert all changes
</button>
```

### Implementing an Undo-Redo

If you want to do the redo, you can count the `undo` click of user,
and slice the history with that number and pass it to the revert function.

For each Undo and Redo action, you need to go to the history twice as 
user clicked to the back or redo button, because `revert` function
also writes to the history.

```typescript

import useRevisionedState from "use-revisioned-state";
import { useState } from "react";

function App() {
  const [appState, setAppState, history, revert] = useRevisionedState({
    users: [],
    viewCount: 1,
  });

  const [clickedUndoCount, setClickedUndoCount] = useState(0);
  const [clickedRedoCount, setClickedRedoCount] = useState(0);

  return (
    <div className="App">
      {appState.viewCount}
      <br />
      <button
        onClick={() => {
          setClickedUndoCount(0);
          setAppState({ ...appState, viewCount: appState.viewCount + 1 });
        }}
      >
        Increase
      </button>
      <button
        onClick={() => {
          setClickedUndoCount(clickedUndoCount + 1);
          revert([
            history[history.length - 1 - clickedUndoCount * 2],
          ]);
        }}
      >
        Undo
      </button>
      <button
        disabled={clickedUndoCount === 0 || clickedUndoCount === clickedRedoCount}
        onClick={() => {
          const back = history[history.length - 1 - clickedRedoCount * 2];
          revert([back]);
          setClickedRedoCount(clickedRedoCount + 1);
        }}
      >
        Redo
      </button>
      <button
        onClick={() => {
          setClickedRedoCount(0);
          setClickedUndoCount(0);
          const back = [...history];
          back.reverse();
          revert(back);
        }}
      >
        Revert all history
      </button>
      <br />
      <h3>The change log</h3>
      {history.map((item) => (
        <pre>{JSON.stringify(item, null, 4)}</pre>
      ))}
    </div>
  );
}
```

I published the hook in NPM. So you can just use it by installing the package "use-revisioned-state".

Source codes are available on github.

<a href="https://github.com/fatih-erikli/use-revisioned-state">https://github.com/fatih-erikli/use-revisioned-state</a>

Happy hacking!

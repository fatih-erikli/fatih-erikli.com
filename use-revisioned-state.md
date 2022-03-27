Edit: I don't recommend implement this method method unless you're
implementing an undo-redo for something it's not possible to make a deep copy
after each action. Initially I published this as an NPM package and published to code on github but I deleted it. I think it's
better if you go for a case driven according your application and without using
any framework or a library, by taking all the state transitions of your application into the account, and implement.


I tried to implement a revisionable state container for the UI state
in order to provide a functionality to undo and redo an action on an application.
There's a lot of ways to do that, I tried to implement the simplest one.
I created a React hook that diffs the previous state and create a change log for it.
That change log includes the added, updated, and removed keys of objects and arrays. I keep 
the updated values with the previous one, so I can easily invert a change and revert it back. 

I deleted this blog post.

Happy hacking!

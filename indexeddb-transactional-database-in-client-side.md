As you may already know, HTTP is a stateless protocol. The communication
between the client and server happens with some flags sent by client and server mutually.
It means, we actually don't really know which user is authenticated. User
is sending their session id via HTTP cookies and we (server) retrieve the related record
from the database, and prepare the page response with the information of
authenticated user.

- <a href="creating-a-web-server-in-asyncio.html">Creating a web-server in AsyncIO</a>
- <a href="whirlwind.html">Whirlwind: HTTP server boilerplate for AsyncIO</a>

To persist a data (storing data in client-side), we have the following options currently.

- Cookies
- LocalStorage
- SessionStorage
- IndexedDB

Each of them is important and has specific use cases in current state of web architecture.

### Cookies

The oldest way to store a data in client side. We write the http cookies in server side
with an HTTP HEADER (SET_COOKIES) and prepare the http response with them. The information is
readable both in server side and client side.

### LocalStorage and SessionStorage

Both of them has the same API to interact. The difference between them is, the information
is deleted when you close the page in SessionStorage. The LocalStorage stores the data
permanently until you delete them manually.

It is a key-value store and stores only Strings.

### IndexedDB

IndexebDB is a database as same as relational databases such as PostgreSQL and MySQL.

It is a transactional database. You basically create a transaction in order to
write something to the database, and commit the transaction after your operations.
It makes it safer.

It is a key-value store and stores all Javascript types such as:

- Arrays
- Objects
- Booleans
- Blob
- And others.

### Lets go with an example

We are going to store a work-log entries. Lets imagine an application, the user is logging
the time of their work on a specific task, and creating a report
of them.

IndexedDB has a low-level database API. You have to create the database
instance when it is needed, and create a transaction when you manipulate your data,
and specify the transactions mode manually. In my opinion, it is important to
know all of that information when you deal with a database in order to keep
the integrity of your data safe.

```javascript
const STORE_NAME_WORK_LOG = "work-log";

async function getIndexedDbInstance() {
  return new Promise(async (resolve) => {
    const DB_NAME = "time-tracker";
    const DB_VERSION = 1;
    const indexedDbRequest = indexedDB.open(DB_NAME, DB_VERSION);

    indexedDbRequest.onupgradeneeded = function () {
      const documentObjectsStore = indexedDbRequest.result.createObjectStore(
        STORE_NAME_WORK_LOG,
        {
          autoIncrement: false,
        }
      );
      documentObjectsStore.createIndex("dateCreation", "dateCreation", {
        unique: false,
      });
    };
    indexedDbRequest.onsuccess = function () {
      resolve(indexedDbRequest.result);
    };
  });
}
```

As you may noticed, we are able to version the database scheme. The number we indicate
is not the version of the database (which is IndexedDB 3.0), but the schema that
you are currently creating. When you update your database schema (such as indexes and
store), you need to increase this number, and the client will request an upgrade
to update their database schemas.

The request of upgrade is an event that we can listen to. In case of an upgrade
request, we are creating our database schema and indexes.

```javascript
function promisifyOnSuccess(request) {
  // This is not so much needed, probably there is
  // a better way to handle it, but I keep it for now :)
  return new Promise((resolve) => {
    request.onsuccess = (event) => {
      resolve(event.target.result);
    };
  });
}

export async function fetchWorkLogEntries() {
  const promise = new Promise(async (resolve) => {
    const db = await getIndexedDbInstance();
    const transaction = db.transaction(STORE_NAME_WORK_LOG, "readonly");
    const objectStore = transaction.objectStore(STORE_NAME_WORK_LOG);
    const dateIndex = objectStore.index("dateCreation");
    const keys = await promisifyOnSuccess(dateIndex.getAllKeys());
    const promises = keys.map((key) =>
      promisifyOnSuccess(objectStore.get(key))
    );
    const results = await Promise.all(promises);
    const resultsWithKeys = keys.map((key, index) => ({
      key,
      ...results[index],
    }));
    resolve(resultsWithKeys);
  });

  return promise;
}
```

This is a ready-only query. We retrieve all the work log items with the index of
`dateCreation`. This is how the indexes work. We created that index when the user
is asked for an upgrade.

The `dateCreation` index gives your data sorted by chronologically. Without
this index, you will receive your records in a random order (of course it is not random,
but you will not get them in a chronological order).

This is why IndexedDB is called as IndexedDB. If you try to implement the same
structure with LocalStorage, you will need to store them with basic array sorting
function in Javascript, and obviously it is going to be crashed when you have
more than thousand numbers of records.

If you have noticed, I also keep the object's own ID inside the stored value. It
eases the development when you list and print those records with ReactJS.

```javascript
export async function createWorkLogEntry(payload, uniqueId) {
  const promise = new Promise(async (resolve) => {
    const db = await getIndexedDbInstance();
    const transaction = db.transaction(STORE_NAME_WORK_LOG, "readwrite");
    const objectStore = transaction.objectStore(STORE_NAME_WORK_LOG);
    const key = uniqueId || generateUniqueID();
    objectStore.put(
      {
        ...payload,
        dateCreation: payload.dateCreation || new Date().toJSON(),
        key,
      },
      key
    ).onsuccess = resolve;
  });
  return promise;
}
```

This is a readwrite transaction. I keep the unique IDs as UUID (Universally Unique Identifier)
instead of an increasing number. If you don't specify a key, IndexedDB will increment
a number as a PrimaryKey. I don't find it useful in real world applications, basically
the user can increment the number and find other irrelevant records and confuse us :)

<a href="https://datatracker.ietf.org/doc/html/rfc4122">A Universally Unique Identifier (UUID) URN Namespace</a>

This is all. I wanted to share my experiences with IndexedDB. I created two different
projects with IndexedDB and published them on github.

- <a href="https://fatih-erikli.github.io/time-tracker">Time tracker</a>
- <a href="https://vectorial-project.github.io">Vectorial: In-browser vector graphics editor</a>

Happy hacking! :)

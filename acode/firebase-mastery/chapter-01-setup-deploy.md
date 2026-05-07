# Chapter 1: Project Setup & First Deploy

[← Overview](chapter-00-overview.md) | [Chapter 2: Authentication →](chapter-02-authentication.md)

---

## The Task

Lena: "I need to see *something* live. A URL I can share. Today."

Marco: "And I need the local emulator running so I don't burn through our free tier while developing."

Fair enough. Let's get SnapTask from zero to deployed in one chapter.

---

## Create the Firebase Project

1. Go to [console.firebase.google.com](https://console.firebase.google.com)
2. Click **Add project**
3. Name it `snaptask-dev`
4. Disable Google Analytics (you don't need it yet)
5. Click **Create project**

30 seconds later, you have a project. No servers provisioned. No billing configured. Just a project ID and a dashboard.

---

## Install the CLI

```bash
npm install -g firebase-tools
firebase login
```

`firebase login` opens a browser window. Authenticate with the Google account that owns the project.

```bash
firebase projects:list
```

```
┌──────────────────────┬───────────────────┬──────────────────────┐
│ Project Display Name │ Project ID        │ Resource Location ID │
├──────────────────────┼───────────────────┼──────────────────────┤
│ snaptask-dev         │ snaptask-dev-abc  │ us-central           │
└──────────────────────┴───────────────────┴──────────────────────┘
```

You're authenticated.

---

## Scaffold the Frontend

```bash
mkdir snaptask && cd snaptask
npm create vite@latest . -- --template react-ts
npm install
npm install firebase
```

That gives you a React + TypeScript app with the Firebase SDK installed.

---

## Initialize Firebase

```bash
firebase init
```

Select these services (spacebar to toggle, enter to confirm):

```
◉ Firestore: Configure security rules and indexes files
◉ Functions: Configure a Cloud Functions directory
◉ Hosting: Configure files for Firebase Hosting
◉ Storage: Configure a default Storage bucket
◉ Emulators: Set up local emulators
```

Answer the prompts:

| Prompt | Answer |
|--------|--------|
| Use an existing project? | Yes → `snaptask-dev-abc` |
| Firestore rules file? | `firestore.rules` |
| Firestore indexes file? | `firestore.indexes.json` |
| Functions language? | TypeScript |
| Use ESLint? | Yes |
| Install dependencies? | Yes |
| Hosting public directory? | `dist` |
| Single-page app? | Yes |
| Storage rules file? | `storage.rules` |
| Which emulators? | Auth, Firestore, Functions, Storage, Hosting |

Your project now looks like:

```
snaptask/
├── dist/                    ← Vite build output (Hosting serves this)
├── functions/               ← Cloud Functions (TypeScript)
│   ├── src/
│   │   └── index.ts
│   ├── package.json
│   └── tsconfig.json
├── src/                     ← React app
│   ├── App.tsx
│   └── main.tsx
├── firebase.json            ← Firebase configuration
├── firestore.rules          ← Security rules
├── firestore.indexes.json   ← Composite indexes
├── storage.rules            ← Storage security rules
├── .firebaserc              ← Project alias
├── package.json
└── vite.config.ts
```

---

## The Firebase Config

Go to the Firebase console → Project Settings → Your apps → Add app → Web.

Register the app (name it "SnapTask Web"). You'll get a config object:

```typescript
// src/firebase.ts
import { initializeApp } from "firebase/app";
import { getFirestore, connectFirestoreEmulator } from "firebase/firestore";
import { getAuth, connectAuthEmulator } from "firebase/auth";
import { getStorage, connectStorageEmulator } from "firebase/storage";

const firebaseConfig = {
  apiKey: "AIzaSy...",
  authDomain: "snaptask-dev-abc.firebaseapp.com",
  projectId: "snaptask-dev-abc",
  storageBucket: "snaptask-dev-abc.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abc123",
};

const app = initializeApp(firebaseConfig);

export const db = getFirestore(app);
export const auth = getAuth(app);
export const storage = getStorage(app);

// Connect to emulators in development
if (import.meta.env.DEV) {
  connectFirestoreEmulator(db, "localhost", 8080);
  connectAuthEmulator(auth, "http://localhost:9099");
  connectStorageEmulator(storage, "localhost", 9199);
}
```

> **Note:** The `apiKey` is not a secret. It identifies your project to Firebase's servers. Security comes from Security Rules, not from hiding this key.

---

## Start the Emulators

```bash
firebase emulators:start
```

```
┌─────────────────────────────────────────────────────────┐
│  ✔  All emulators ready!                                 │
│                                                          │
│  Auth Emulator      → http://localhost:9099              │
│  Firestore Emulator → http://localhost:8080              │
│  Storage Emulator   → http://localhost:9199              │
│  Functions Emulator → http://localhost:5001              │
│  Hosting Emulator   → http://localhost:5000              │
│  Emulator UI        → http://localhost:4000              │
└─────────────────────────────────────────────────────────┘
```

Open `http://localhost:4000`. You'll see the Emulator Suite UI — a dashboard showing all running services, with tabs for Firestore data, Auth users, and function logs.

This is your development environment. No billing. No risk. Everything resets when you stop the emulators (unless you export data).

---

## A Quick Smoke Test

Let's verify the SDK connects to the emulator. Update `App.tsx`:

```tsx
// src/App.tsx
import { useEffect, useState } from "react";
import { db } from "./firebase";
import { collection, addDoc, getDocs } from "firebase/firestore";

function App() {
  const [status, setStatus] = useState("Connecting...");

  useEffect(() => {
    async function test() {
      try {
        // Write a test document
        await addDoc(collection(db, "test"), {
          message: "Hello from SnapTask!",
          timestamp: new Date(),
        });

        // Read it back
        const snapshot = await getDocs(collection(db, "test"));
        setStatus(`Connected! ${snapshot.size} document(s) in 'test' collection.`);
      } catch (error) {
        setStatus(`Error: ${error}`);
      }
    }
    test();
  }, []);

  return (
    <div style={{ padding: "2rem", fontFamily: "monospace" }}>
      <h1>SnapTask</h1>
      <p>{status}</p>
    </div>
  );
}

export default App;
```

Run the dev server:

```bash
npm run dev
```

Open `http://localhost:5173`. You should see:

```
SnapTask
Connected! 1 document(s) in 'test' collection.
```

Check the Emulator UI at `localhost:4000` → Firestore tab. You'll see the `test` collection with your document. It worked. The SDK talks to the local emulator, not production.

---

## Deploy to Firebase Hosting

Build the app:

```bash
npm run build
```

This creates the `dist/` folder with your production bundle.

Deploy:

```bash
firebase deploy --only hosting
```

```
✔  Deploy complete!

Project Console: https://console.firebase.google.com/project/snaptask-dev-abc/overview
Hosting URL: https://snaptask-dev-abc.web.app
```

That URL is live. HTTPS. CDN-backed. Global. Free (within limits).

Lena: "Wait, that's it? It's live?"

Yes. `firebase deploy --only hosting`. That's the entire deployment pipeline.

---

## The firebase.json File

This is the configuration that ties everything together:

```json
{
  "firestore": {
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  },
  "functions": {
    "source": "functions",
    "runtime": "nodejs18"
  },
  "hosting": {
    "public": "dist",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  },
  "storage": {
    "rules": "storage.rules"
  },
  "emulators": {
    "auth": { "port": 9099 },
    "firestore": { "port": 8080 },
    "functions": { "port": 5001 },
    "storage": { "port": 9199 },
    "hosting": { "port": 5000 },
    "ui": { "enabled": true, "port": 4000 }
  }
}
```

The `rewrites` rule sends all routes to `index.html` — essential for a single-page app with client-side routing.

---

## Deploy Everything

When you're ready to deploy all services at once:

```bash
firebase deploy
```

This deploys:
- Hosting (your built React app)
- Firestore rules
- Firestore indexes
- Storage rules
- Cloud Functions

For now, deploy only hosting. We'll deploy rules and functions as we build them.

---

## Common Mistakes

### 1. Deploying `src/` instead of `dist/`

If your hosting URL shows a blank page or raw source files, check that `firebase.json` has `"public": "dist"` and that you ran `npm run build` first.

### 2. Forgetting emulator connections in dev

If you see real data appearing in the Firebase console during development, your app is hitting production. Check that the emulator connection code runs in dev mode.

### 3. The `apiKey` panic

New developers see the API key in client code and panic. It's fine. The key identifies your project — it doesn't grant access. Security Rules control access. (Chapter 5 covers this in depth.)

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Command                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
firebase login                  │ Authenticate with Google
firebase init                   │ Initialize project services
firebase emulators:start        │ Run all services locally
firebase deploy --only hosting  │ Deploy frontend only
firebase deploy                 │ Deploy everything
firebase serve                  │ Preview hosting locally
firebase projects:list          │ List your projects
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Lena: "Great, it's live. But there's no login. Anyone can use it. We need accounts."

Authentication. The first real Firebase service.

---

[← Overview](chapter-00-overview.md) | [Chapter 2: Authentication →](chapter-02-authentication.md)

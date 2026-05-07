# Chapter 6: Storage — "Attach Files to Tasks"

[← Chapter 5: Security Rules](chapter-05-security-rules.md) | [Chapter 7: Queries →](chapter-07-queries.md)

---

## The Task

Marco: "Users want to attach screenshots, PDFs, and design files to tasks. Where do those go? Not in Firestore — it has a 1MB document limit."

Lena: "And I need to preview images inline. Not just download links."

---

## Firebase Storage

Firebase Storage (backed by Google Cloud Storage) handles file uploads. It's a separate service from Firestore with its own security rules.

```
Firestore = structured data (JSON documents)
Storage   = binary files (images, PDFs, videos)
```

---

## Upload a File

```typescript
import { ref, uploadBytes, getDownloadURL } from "firebase/storage";
import { storage, auth } from "./firebase";

export async function uploadTaskAttachment(
  teamId: string,
  taskId: string,
  file: File
) {
  const user = auth.currentUser;
  if (!user) throw new Error("Not authenticated");

  // Create a reference to the file location
  const fileRef = ref(
    storage,
    `teams/${teamId}/tasks/${taskId}/${Date.now()}_${file.name}`
  );

  // Upload the file
  const snapshot = await uploadBytes(fileRef, file);

  // Get the public download URL
  const downloadURL = await getDownloadURL(snapshot.ref);

  return {
    name: file.name,
    size: file.size,
    type: file.type,
    url: downloadURL,
    path: snapshot.ref.fullPath,
    uploadedBy: user.uid,
    uploadedAt: new Date().toISOString(),
  };
}
```

The path `teams/{teamId}/tasks/{taskId}/{timestamp}_{filename}` organizes files by team and task. The timestamp prevents name collisions.

---

## Upload with Progress

```typescript
import { ref, uploadBytesResumable, getDownloadURL } from "firebase/storage";

export function uploadWithProgress(
  teamId: string,
  taskId: string,
  file: File,
  onProgress: (percent: number) => void
): Promise<string> {
  return new Promise((resolve, reject) => {
    const fileRef = ref(
      storage,
      `teams/${teamId}/tasks/${taskId}/${Date.now()}_${file.name}`
    );

    const uploadTask = uploadBytesResumable(fileRef, file);

    uploadTask.on(
      "state_changed",
      (snapshot) => {
        const percent = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
        onProgress(percent);
      },
      (error) => {
        reject(error);
      },
      async () => {
        const url = await getDownloadURL(uploadTask.snapshot.ref);
        resolve(url);
      }
    );
  });
}
```

`uploadBytesResumable` gives you progress events and the ability to pause/resume uploads.

---

## React Upload Component

```tsx
// src/components/FileUpload.tsx
import { useState } from "react";
import { uploadWithProgress } from "../services/storage";
import { updateTask } from "../services/tasks";
import { arrayUnion } from "firebase/firestore";

interface Props {
  teamId: string;
  taskId: string;
}

export function FileUpload({ teamId, taskId }: Props) {
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
      alert("File too large. Max 10MB.");
      return;
    }

    setUploading(true);
    try {
      const url = await uploadWithProgress(teamId, taskId, file, setProgress);

      // Store the attachment reference in Firestore
      await updateTask(teamId, taskId, {
        attachments: arrayUnion({
          name: file.name,
          url,
          type: file.type,
          size: file.size,
        }),
      });
    } catch (err) {
      console.error("Upload failed:", err);
    } finally {
      setUploading(false);
      setProgress(0);
    }
  }

  return (
    <div>
      <input
        type="file"
        onChange={handleFileChange}
        disabled={uploading}
        accept="image/*,.pdf,.doc,.docx"
      />
      {uploading && <progress value={progress} max={100} />}
    </div>
  );
}
```

---

## Download / Display Files

The `downloadURL` from `getDownloadURL()` is a public HTTPS URL with a token. You can use it directly in `<img>` tags or `<a>` links:

```tsx
function AttachmentList({ attachments }: { attachments: any[] }) {
  return (
    <ul>
      {attachments.map((att, i) => (
        <li key={i}>
          {att.type.startsWith("image/") ? (
            <img src={att.url} alt={att.name} style={{ maxWidth: 200 }} />
          ) : (
            <a href={att.url} target="_blank" rel="noopener noreferrer">
              {att.name} ({(att.size / 1024).toFixed(1)} KB)
            </a>
          )}
        </li>
      ))}
    </ul>
  );
}
```

---

## Delete a File

```typescript
import { ref, deleteObject } from "firebase/storage";

export async function deleteAttachment(filePath: string) {
  const fileRef = ref(storage, filePath);
  await deleteObject(fileRef);
}
```

Remember to also remove the attachment reference from the Firestore document.

---

## Storage Security Rules

Storage has its own rules file (`storage.rules`):

```
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {

    // Team files: only team members can read/write
    match /teams/{teamId}/{allPaths=**} {
      allow read: if request.auth != null
        && request.auth.uid in firestore.get(
          /databases/(default)/documents/teams/$(teamId)
        ).data.members;

      allow write: if request.auth != null
        && request.auth.uid in firestore.get(
          /databases/(default)/documents/teams/$(teamId)
        ).data.members
        // Max file size: 10MB
        && request.resource.size < 10 * 1024 * 1024
        // Only allow certain content types
        && request.resource.contentType.matches('image/.*|application/pdf|application/msword.*');
    }

    // User avatars: only the user can write their own
    match /users/{userId}/avatar {
      allow read: if request.auth != null;
      allow write: if request.auth.uid == userId
        && request.resource.size < 2 * 1024 * 1024
        && request.resource.contentType.matches('image/.*');
    }
  }
}
```

Key differences from Firestore rules:
- `request.resource.size` — file size in bytes
- `request.resource.contentType` — MIME type
- `firestore.get()` — cross-service read (read Firestore from Storage rules)
- `{allPaths=**}` — matches all nested paths

---

## Storage Path Design

```
storage/
├── teams/
│   └── {teamId}/
│       └── tasks/
│           └── {taskId}/
│               ├── 1699000000_screenshot.png
│               └── 1699000001_design.pdf
├── users/
│   └── {userId}/
│       └── avatar
└── exports/
    └── {teamId}/
        └── report-2024-01.csv
```

Organize by access pattern. Files under `teams/{teamId}/` share the same security rule — team members can access them.

---

## File Metadata

```typescript
import { ref, getMetadata, updateMetadata } from "firebase/storage";

// Read metadata
const fileRef = ref(storage, "teams/team1/tasks/task1/photo.png");
const metadata = await getMetadata(fileRef);
console.log(metadata.size);        // bytes
console.log(metadata.contentType); // "image/png"
console.log(metadata.timeCreated); // ISO string

// Update metadata
await updateMetadata(fileRef, {
  customMetadata: {
    uploadedBy: "user123",
    taskId: "task1",
  },
});
```

---

## Common Mistakes

### 1. Storing download URLs without the path

```typescript
// ❌ Only storing the URL — can't delete the file later
attachments: [{ url: "https://firebasestorage.googleapis.com/..." }]

// ✅ Store both URL and path
attachments: [{
  url: "https://firebasestorage.googleapis.com/...",
  path: "teams/team1/tasks/task1/1699000000_photo.png"
}]
```

You need the path to delete or update the file.

### 2. No file size validation

Without size limits in rules, users can upload 5GB files and blow up your storage costs. Always set `request.resource.size < maxBytes` in rules.

### 3. No content type validation

Without type checks, users can upload executables or scripts. Validate `request.resource.contentType` in rules.

### 4. Forgetting that download URLs are public

The URL contains an access token. Anyone with the URL can access the file — even without being authenticated. If you need truly private files, use signed URLs with expiration (via Cloud Functions).

---

## Deploy Storage Rules

```bash
firebase deploy --only storage
```

---

## Quick Reference

```
────────────────────────────────────────┬──────────────────────────────────────
Function                                │ What It Does
────────────────────────────────────────┼──────────────────────────────────────
ref(storage, path)                      │ Create a reference to a file
uploadBytes(ref, file)                  │ Upload (simple)
uploadBytesResumable(ref, file)         │ Upload with progress/pause/resume
getDownloadURL(ref)                     │ Get public download URL
deleteObject(ref)                       │ Delete a file
getMetadata(ref)                        │ Read file metadata
listAll(ref)                            │ List all files in a path
────────────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Lena: "We have 200 tasks now. I need to filter by status, by assignee, by priority. The task list is useless without filters."

Firestore queries. More powerful than you'd expect from a NoSQL database — but with sharp edges.

---

[← Chapter 5: Security Rules](chapter-05-security-rules.md) | [Chapter 7: Queries →](chapter-07-queries.md)

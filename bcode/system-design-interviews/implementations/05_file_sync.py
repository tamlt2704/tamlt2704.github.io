"""
File Sync — Core Implementation
=================================
Demonstrates: Content-based chunking (rolling hash), SHA256 dedup,
sync protocol, conflict detection (LWW vs vector clocks).

In a real system:
- Chunks stored in S3/GCS with content-addressable keys (SHA256)
- Metadata in PostgreSQL (file → chunk list mapping)
- Sync via delta protocol (rsync-like): client sends hashes, server diffs
- Conflict resolution: Dropbox uses LWW + conflict copies, Google Drive uses OT
- CDC (content-defined chunking) uses Rabin fingerprint for variable-size chunks
"""

import hashlib
import time
from dataclasses import dataclass, field


# ─── Content-Based Chunking ──────────────────────────────────────────────────

CHUNK_SIZE = 64  # Small for demo; production uses 4-8 MB
WINDOW_SIZE = 16  # Rolling hash window
CHUNK_BOUNDARY_MASK = 0x0F  # Triggers boundary when hash & mask == 0


def fixed_size_chunk(data: bytes, chunk_size: int = CHUNK_SIZE) -> list[bytes]:
    """Simple fixed-size chunking. Fast but poor dedup across edits."""
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]


def content_defined_chunk(data: bytes, min_size: int = 32, max_size: int = 128) -> list[bytes]:
    """
    Content-defined chunking using rolling hash.
    Chunk boundaries are determined by content, not position.
    This means inserting bytes only affects nearby chunks, not all subsequent ones.

    Production uses Rabin fingerprint; we use a simple polynomial hash.
    """
    chunks = []
    start = 0
    i = min_size  # Don't check boundary before min_size

    while start < len(data):
        if i >= len(data) or (i - start) >= max_size:
            chunks.append(data[start:i])
            start = i
            i = start + min_size
            continue

        # Simple rolling hash (Buzhash in production)
        window = data[max(start, i - WINDOW_SIZE):i]
        h = sum(b * (31 ** idx) for idx, b in enumerate(window)) & 0xFFFFFFFF

        if h & CHUNK_BOUNDARY_MASK == 0:
            chunks.append(data[start:i])
            start = i
            i = start + min_size
        else:
            i += 1

    if start < len(data):
        chunks.append(data[start:])
    return chunks


# ─── SHA256 Dedup ─────────────────────────────────────────────────────────────

def chunk_hash(data: bytes) -> str:
    """Content-addressable hash for dedup."""
    return hashlib.sha256(data).hexdigest()[:16]  # Truncated for readability


# ─── Chunk Store (simulates S3/blob storage) ─────────────────────────────────

class ChunkStore:
    """Content-addressable store. Same content → same key → automatic dedup."""

    def __init__(self):
        self.chunks: dict[str, bytes] = {}  # hash → data
        self.total_stored = 0
        self.dedup_savings = 0

    def put(self, data: bytes) -> str:
        h = chunk_hash(data)
        if h in self.chunks:
            self.dedup_savings += len(data)
        else:
            self.chunks[h] = data
            self.total_stored += len(data)
        return h

    def get(self, h: str) -> bytes | None:
        return self.chunks.get(h)

    def has(self, h: str) -> bool:
        return h in self.chunks


# ─── File Metadata ────────────────────────────────────────────────────────────

@dataclass
class FileVersion:
    path: str
    chunk_hashes: list[str]
    timestamp: float = field(default_factory=time.time)
    vector_clock: dict[str, int] = field(default_factory=dict)

    @property
    def content_hash(self) -> str:
        """Hash of the chunk list — identifies unique file content."""
        return hashlib.sha256(",".join(self.chunk_hashes).encode()).hexdigest()[:16]


# ─── Sync Protocol ───────────────────────────────────────────────────────────

class SyncServer:
    """
    Sync protocol: client sends chunk hashes, server responds with missing ones.
    Similar to rsync's rolling checksum approach.
    """

    def __init__(self):
        self.store = ChunkStore()
        self.files: dict[str, FileVersion] = {}  # path → latest version

    def upload_file(self, path: str, data: bytes, client_id: str) -> FileVersion:
        """Chunk, dedup, and store a file."""
        chunks = content_defined_chunk(data)
        hashes = [self.store.put(chunk) for chunk in chunks]
        version = FileVersion(path=path, chunk_hashes=hashes)
        version.vector_clock[client_id] = version.vector_clock.get(client_id, 0) + 1
        self.files[path] = version
        return version

    def sync_check(self, path: str, client_hashes: list[str]) -> dict:
        """
        Client sends its chunk hashes. Server responds with:
        - missing: chunks the server needs (client has new data)
        - extra: chunks the client needs (server has newer data)
        """
        server_version = self.files.get(path)
        if server_version is None:
            return {"status": "new_file", "missing_on_server": client_hashes}

        server_hashes = set(server_version.chunk_hashes)
        client_hash_set = set(client_hashes)

        return {
            "status": "sync_needed",
            "missing_on_server": list(client_hash_set - server_hashes),
            "missing_on_client": list(server_hashes - client_hash_set),
            "common": len(server_hashes & client_hash_set),
        }

    def download_file(self, path: str) -> bytes | None:
        """Reconstruct file from chunks."""
        version = self.files.get(path)
        if not version:
            return None
        chunks = [self.store.get(h) for h in version.chunk_hashes]
        return b"".join(c for c in chunks if c)


# ─── Conflict Detection ──────────────────────────────────────────────────────

def last_write_wins(v1: FileVersion, v2: FileVersion) -> FileVersion:
    """Simple LWW conflict resolution. Latest timestamp wins."""
    return v1 if v1.timestamp >= v2.timestamp else v2


def vector_clock_compare(vc1: dict[str, int], vc2: dict[str, int]) -> str:
    """
    Compare two vector clocks:
    - "v1_dominates": v1 happened after v2
    - "v2_dominates": v2 happened after v1
    - "concurrent": neither dominates (CONFLICT!)
    """
    all_keys = set(vc1.keys()) | set(vc2.keys())
    v1_gte = all(vc1.get(k, 0) >= vc2.get(k, 0) for k in all_keys)
    v2_gte = all(vc2.get(k, 0) >= vc1.get(k, 0) for k in all_keys)

    if v1_gte and not v2_gte:
        return "v1_dominates"
    elif v2_gte and not v1_gte:
        return "v2_dominates"
    elif v1_gte and v2_gte:
        return "equal"
    else:
        return "concurrent"  # CONFLICT


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== File Sync Demo ===\n")

    server = SyncServer()

    # --- Chunking comparison ---
    print("--- Chunking Strategies ---")
    original = b"The quick brown fox jumps over the lazy dog. " * 5
    modified = b"The quick brown fox LEAPS over the lazy dog. " * 5  # Small edit

    fixed_orig = fixed_size_chunk(original)
    fixed_mod = fixed_size_chunk(modified)
    cdc_orig = content_defined_chunk(original)
    cdc_mod = content_defined_chunk(modified)

    # Compare dedup efficiency
    fixed_common = len(set(chunk_hash(c) for c in fixed_orig) &
                       set(chunk_hash(c) for c in fixed_mod))
    cdc_common = len(set(chunk_hash(c) for c in cdc_orig) &
                     set(chunk_hash(c) for c in cdc_mod))

    print(f"  Original: {len(original)} bytes")
    print(f"  Fixed chunks: {len(fixed_orig)} chunks, {fixed_common} shared after edit")
    print(f"  CDC chunks:   {len(cdc_orig)} chunks, {cdc_common} shared after edit")
    print(f"  → CDC preserves more chunks across edits (better dedup)")

    # --- Sync protocol ---
    print("\n--- Sync Protocol ---")
    file_data = b"Hello world! This is a file that will be synced across devices."
    version = server.upload_file("notes.txt", file_data, "laptop")
    print(f"  Uploaded notes.txt: {len(version.chunk_hashes)} chunks")
    print(f"  Store: {server.store.total_stored} bytes, dedup savings: {server.store.dedup_savings}")

    # Client modifies file
    modified_data = b"Hello world! This is a MODIFIED file that will be synced across devices."
    mod_chunks = content_defined_chunk(modified_data)
    mod_hashes = [chunk_hash(c) for c in mod_chunks]

    sync_result = server.sync_check("notes.txt", mod_hashes)
    print(f"\n  Sync check result:")
    print(f"    Common chunks: {sync_result['common']}")
    print(f"    Client needs to upload: {len(sync_result['missing_on_server'])} chunks")
    print(f"    Client needs to download: {len(sync_result['missing_on_client'])} chunks")
    print(f"    → Only transfer the diff, not the whole file!")

    # --- Conflict detection ---
    print("\n--- Conflict Detection ---")
    v1 = FileVersion("doc.txt", ["a", "b"], vector_clock={"laptop": 2, "phone": 1})
    v2 = FileVersion("doc.txt", ["a", "c"], vector_clock={"laptop": 1, "phone": 2})
    v3 = FileVersion("doc.txt", ["a", "d"], vector_clock={"laptop": 3, "phone": 1})

    print(f"  v1 clock: {v1.vector_clock}")
    print(f"  v2 clock: {v2.vector_clock}")
    print(f"  v1 vs v2: {vector_clock_compare(v1.vector_clock, v2.vector_clock)}")
    print(f"  v1 vs v3: {vector_clock_compare(v1.vector_clock, v3.vector_clock)}")
    print(f"  → 'concurrent' means CONFLICT — both edited independently")

    # LWW resolution
    v1.timestamp = time.time() - 10
    v2.timestamp = time.time()
    winner = last_write_wins(v1, v2)
    print(f"\n  LWW resolution: v2 wins (more recent)")
    print(f"  → Dropbox creates 'doc (conflicted copy).txt' for the loser")

    # --- Dedup savings ---
    print("\n--- Dedup Savings ---")
    server2 = SyncServer()
    # Upload same content from two "devices"
    data = b"Shared document content that appears on multiple devices" * 3
    server2.upload_file("file_laptop.txt", data, "laptop")
    server2.upload_file("file_phone.txt", data, "phone")
    print(f"  Two identical files uploaded")
    print(f"  Stored once: {server2.store.total_stored} bytes")
    print(f"  Dedup savings: {server2.store.dedup_savings} bytes")

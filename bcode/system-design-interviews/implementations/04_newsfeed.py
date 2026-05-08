"""
News Feed — Core Implementation
=================================
Demonstrates: Fan-out on write (push), fan-out on read (pull),
timeline merge, ranking by recency + engagement.

In a real system:
- Fan-out on write: Kafka consumers push to Redis sorted sets per user
- Fan-out on read: Query follows list, fetch posts, merge in app server
- Hybrid: Push for normal users, pull for celebrities (>1M followers)
- Ranking: ML model with features (engagement, recency, affinity)
- Storage: Posts in Cassandra, feeds in Redis, social graph in Neo4j/TAO
"""

import time
import heapq
from collections import defaultdict
from dataclasses import dataclass, field


# ─── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class Post:
    id: str
    author: str
    content: str
    timestamp: float = field(default_factory=time.time)
    likes: int = 0
    comments: int = 0
    shares: int = 0

    @property
    def engagement_score(self) -> float:
        """Simple engagement metric — production uses ML models."""
        return self.likes * 1.0 + self.comments * 2.0 + self.shares * 3.0

    def rank_score(self, now: float = None) -> float:
        """Combine recency and engagement for ranking."""
        now = now or time.time()
        age_hours = max(0.1, (now - self.timestamp) / 3600)
        # Engagement decays with time (similar to HackerNews formula)
        return self.engagement_score / (age_hours ** 1.5)


# ─── Social Graph ─────────────────────────────────────────────────────────────

class SocialGraph:
    """Adjacency list for follow relationships."""

    def __init__(self):
        self.followers: dict[str, set[str]] = defaultdict(set)  # user → who follows them
        self.following: dict[str, set[str]] = defaultdict(set)  # user → who they follow

    def follow(self, follower: str, followee: str):
        self.followers[followee].add(follower)
        self.following[follower].add(followee)

    def get_followers(self, user: str) -> set[str]:
        return self.followers[user]

    def get_following(self, user: str) -> set[str]:
        return self.following[user]


# ─── Fan-Out on Write (Push Model) ───────────────────────────────────────────

class PushFeedService:
    """
    Fan-out on write: When a user posts, push to all followers' feeds.

    Pros: Read is fast (pre-computed feed), low read latency
    Cons: Write amplification for popular users, stale for inactive users
    Production: Kafka → fan-out workers → Redis ZADD per follower
    """

    def __init__(self, graph: SocialGraph):
        self.graph = graph
        self.feeds: dict[str, list[Post]] = defaultdict(list)  # user → their feed
        self.feed_limit = 100  # Max posts in feed cache
        self.write_ops = 0

    def publish(self, post: Post):
        """Fan-out: push post to every follower's feed."""
        followers = self.graph.get_followers(post.author)
        for follower in followers:
            self.feeds[follower].append(post)
            # Trim to limit (in Redis: ZREMRANGEBYRANK)
            if len(self.feeds[follower]) > self.feed_limit:
                self.feeds[follower] = self.feeds[follower][-self.feed_limit:]
            self.write_ops += 1

    def get_feed(self, user: str, limit: int = 10) -> list[Post]:
        """Read is simple — feed is pre-computed."""
        feed = self.feeds.get(user, [])
        # Sort by rank score
        now = time.time()
        return sorted(feed, key=lambda p: p.rank_score(now), reverse=True)[:limit]


# ─── Fan-Out on Read (Pull Model) ────────────────────────────────────────────

class PullFeedService:
    """
    Fan-out on read: When user opens feed, fetch posts from all followed users.

    Pros: No write amplification, always fresh
    Cons: Slow reads (must query N users), high read latency
    Production: Parallel queries to post tables, merge in app server
    """

    def __init__(self, graph: SocialGraph):
        self.graph = graph
        self.user_posts: dict[str, list[Post]] = defaultdict(list)  # user → their posts
        self.read_ops = 0

    def publish(self, post: Post):
        """Just store in author's post list — no fan-out."""
        self.user_posts[post.author].append(post)

    def get_feed(self, user: str, limit: int = 10) -> list[Post]:
        """Merge posts from all followed users at read time."""
        following = self.graph.get_following(user)
        # K-way merge using heap (merge K sorted lists)
        heap: list[tuple[float, int, Post]] = []
        now = time.time()

        for followee in following:
            posts = self.user_posts.get(followee, [])
            for i, post in enumerate(posts[-20:]):  # Last 20 per user
                heapq.heappush(heap, (-post.rank_score(now), i, post))
                self.read_ops += 1

        # Extract top-K
        result = []
        while heap and len(result) < limit:
            _, _, post = heapq.heappop(heap)
            result.append(post)
        return result


# ─── Timeline Merge (K-way merge) ────────────────────────────────────────────

def merge_timelines(timelines: list[list[Post]], limit: int = 10) -> list[Post]:
    """
    Merge K sorted timelines into one ranked feed.
    Uses a min-heap for O(N log K) merge where K = number of sources.
    """
    heap: list[tuple[float, int, int, Post]] = []

    for i, timeline in enumerate(timelines):
        if timeline:
            post = timeline[0]
            heapq.heappush(heap, (-post.timestamp, i, 0, post))

    result = []
    while heap and len(result) < limit:
        _, timeline_idx, post_idx, post = heapq.heappop(heap)
        result.append(post)
        # Push next post from same timeline
        next_idx = post_idx + 1
        if next_idx < len(timelines[timeline_idx]):
            next_post = timelines[timeline_idx][next_idx]
            heapq.heappush(heap, (-next_post.timestamp, timeline_idx, next_idx, next_post))

    return result


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== News Feed Demo ===\n")

    # Setup social graph
    graph = SocialGraph()
    graph.follow("alice", "bob")      # alice follows bob
    graph.follow("alice", "charlie")  # alice follows charlie
    graph.follow("alice", "dave")     # alice follows dave
    # Simulate celebrity: 1000 followers
    for i in range(1000):
        graph.follow(f"user_{i}", "celebrity")

    # Create posts with varying engagement
    base_time = time.time()
    posts = [
        Post("p1", "bob", "Just shipped a new feature!", base_time - 3600, likes=50, comments=10),
        Post("p2", "charlie", "Great coffee today", base_time - 1800, likes=5, comments=1),
        Post("p3", "dave", "System design tip: use consistent hashing", base_time - 900, likes=200, comments=45, shares=30),
        Post("p4", "bob", "Lunch break", base_time - 600, likes=3),
        Post("p5", "charlie", "New blog post on distributed systems", base_time - 300, likes=80, comments=20, shares=15),
    ]

    # --- Push Model ---
    print("--- Fan-Out on Write (Push) ---")
    push_service = PushFeedService(graph)
    t0 = time.time()
    for post in posts:
        push_service.publish(post)
    push_time = time.time() - t0

    t0 = time.time()
    feed = push_service.get_feed("alice", limit=5)
    read_time = time.time() - t0

    print(f"  Write ops (fan-out): {push_service.write_ops}")
    print(f"  Write time: {push_time*1000:.2f}ms")
    print(f"  Read time:  {read_time*1000:.2f}ms")
    print(f"  Alice's feed:")
    for p in feed:
        print(f"    [{p.author}] {p.content[:40]} (score: {p.rank_score():.1f})")

    # --- Pull Model ---
    print("\n--- Fan-Out on Read (Pull) ---")
    pull_service = PullFeedService(graph)
    t0 = time.time()
    for post in posts:
        pull_service.publish(post)
    write_time = time.time() - t0

    t0 = time.time()
    feed = pull_service.get_feed("alice", limit=5)
    read_time = time.time() - t0

    print(f"  Read ops (merge): {pull_service.read_ops}")
    print(f"  Write time: {write_time*1000:.2f}ms")
    print(f"  Read time:  {read_time*1000:.2f}ms")
    print(f"  Alice's feed:")
    for p in feed:
        print(f"    [{p.author}] {p.content[:40]} (score: {p.rank_score():.1f})")

    # --- Celebrity Problem ---
    print("\n--- Celebrity Problem (1000 followers) ---")
    celebrity_post = Post("p6", "celebrity", "Big announcement!", likes=10000, comments=500, shares=200)
    t0 = time.time()
    push_service.publish(celebrity_post)
    celeb_push_time = time.time() - t0
    print(f"  Push fan-out to 1000 followers: {celeb_push_time*1000:.2f}ms")
    print(f"  Total write ops: {push_service.write_ops}")
    print(f"  → This is why Twitter uses hybrid: pull for celebrities, push for normal users")

    # --- Ranking comparison ---
    print("\n--- Ranking: Recency vs Engagement ---")
    print(f"  {'Post':<45} {'Age':<8} {'Engagement':<12} {'Rank Score'}")
    now = time.time()
    for p in sorted(posts, key=lambda x: x.rank_score(now), reverse=True):
        age = (now - p.timestamp) / 60
        print(f"  {p.content[:43]:<45} {age:.0f}m    {p.engagement_score:<12.0f} {p.rank_score(now):.1f}")

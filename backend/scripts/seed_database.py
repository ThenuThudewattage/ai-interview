"""Seed database with initial skill areas and sample interview questions."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db.database import AsyncSessionLocal, create_all_tables
from app.models.skill import SkillArea
from app.models.interview import Question


SKILL_AREAS = [
    {"name": "system_design", "description": "System design principles and architecture", "category": "advanced"},
    {"name": "distributed_systems", "description": "Distributed computing concepts", "category": "advanced"},
    {"name": "algorithms", "description": "Algorithm design and analysis", "category": "fundamentals"},
    {"name": "data_structures", "description": "Core data structures", "category": "fundamentals"},
    {"name": "databases", "description": "SQL, NoSQL, and database design", "category": "fundamentals"},
    {"name": "scalability", "description": "Horizontal and vertical scaling", "category": "advanced"},
    {"name": "caching", "description": "Caching strategies and implementations", "category": "advanced"},
    {"name": "networking", "description": "HTTP, TCP/IP, DNS, load balancing", "category": "fundamentals"},
    {"name": "security", "description": "Authentication, authorization, encryption", "category": "advanced"},
    {"name": "machine_learning", "description": "ML algorithms and model design", "category": "specialized"},
    {"name": "behavioral", "description": "Leadership, communication, teamwork", "category": "soft_skills"},
    {"name": "coding", "description": "Clean code and implementation skills", "category": "fundamentals"},
    {"name": "complexity_analysis", "description": "Time and space complexity", "category": "fundamentals"},
    {"name": "cloud_platforms", "description": "AWS, Azure, GCP", "category": "specialized"},
    {"name": "microservices", "description": "Microservices architecture", "category": "advanced"},
]

SAMPLE_QUESTIONS = [
    # System Design - Hard
    {
        "title": "Design a URL Shortener",
        "content": "Design a URL shortening service like bit.ly. The system should be able to handle 100 million URL shortening requests per day and redirect users in under 10ms. Walk me through your architecture decisions, data model, and how you'd handle scale.",
        "question_type": "system_design",
        "skill_areas": ["system_design", "databases", "caching", "scalability"],
        "difficulty_level": "hard",
        "estimated_time_minutes": 45,
        "expected_answer_summary": "Key points: hash function (MD5/SHA/custom base62), database choice (NoSQL for reads), CDN for redirects, cache layer for hot URLs, rate limiting for abuse prevention",
        "key_points": ["base62 encoding", "hash collision handling", "read-heavy workload", "cache-first strategy", "analytics tracking"],
        "followup_hints": ["How would you handle custom aliases?", "What's your cache eviction strategy?", "How do you prevent abuse?"],
    },
    {
        "title": "Design a Distributed Message Queue",
        "content": "Design a distributed message queue system similar to Apache Kafka. The system needs to handle 10 million messages per second, guarantee message delivery, support multiple consumers, and retain messages for 7 days.",
        "question_type": "system_design",
        "skill_areas": ["system_design", "distributed_systems", "scalability"],
        "difficulty_level": "expert",
        "estimated_time_minutes": 60,
        "expected_answer_summary": "Key points: log-based storage, partitioning strategy, consumer groups, replication factor, offset management, message retention policy",
        "key_points": ["append-only log", "partition/shard strategy", "at-least-once delivery", "consumer group offsets", "replication"],
        "followup_hints": ["How do you handle message ordering?", "How do you handle consumer lag?", "What happens during partition leader failure?"],
    },
    {
        "title": "Design a Real-time Chat System",
        "content": "Design WhatsApp-scale messaging: 2 billion users, 100 billion messages per day. Support 1-1 and group chats, message delivery receipts, offline message storage, and end-to-end encryption.",
        "question_type": "system_design",
        "skill_areas": ["system_design", "distributed_systems", "networking"],
        "difficulty_level": "expert",
        "estimated_time_minutes": 60,
        "expected_answer_summary": "WebSocket connections, connection service, message routing, fan-out for groups, offline storage, push notifications, E2E encryption with Signal protocol",
        "key_points": ["WebSocket/long polling", "message fanout", "read receipts", "push notifications", "encryption"],
        "followup_hints": ["How do you handle group chats with 1000+ members?", "What about message ordering in poor network conditions?"],
    },
    # Algorithms - Medium
    {
        "title": "LRU Cache Implementation",
        "content": "Design and implement a data structure for a Least Recently Used (LRU) cache. It should support get and put operations in O(1) time. Explain your approach before coding.",
        "question_type": "algorithm",
        "skill_areas": ["algorithms", "data_structures"],
        "difficulty_level": "medium",
        "estimated_time_minutes": 30,
        "expected_answer_summary": "HashMap + Doubly Linked List: HashMap for O(1) lookup, DLL for O(1) insertion/deletion to track access order",
        "key_points": ["doubly linked list", "hashmap", "O(1) operations", "eviction policy"],
        "followup_hints": ["What about thread safety?", "How would you implement LFU instead?"],
    },
    {
        "title": "Find Median from Data Stream",
        "content": "Design a data structure that supports adding integers from a data stream and finding the median of all elements seen so far. Both operations should be efficient.",
        "question_type": "algorithm",
        "skill_areas": ["algorithms", "data_structures"],
        "difficulty_level": "hard",
        "estimated_time_minutes": 35,
        "expected_answer_summary": "Two heaps: max-heap for lower half, min-heap for upper half. Maintain balance so median is always at top.",
        "key_points": ["two heaps", "rebalancing", "O(log n) insert", "O(1) median"],
        "followup_hints": ["What if you could only use one data structure?", "How does this change if 99% of values are between 0-100?"],
    },
    {
        "title": "Word Ladder Problem",
        "content": "Given two words (beginWord and endWord), and a dictionary's word list, find the length of the shortest transformation sequence from beginWord to endWord such that only one letter can be changed at a time, and each transformed word must exist in the word list.",
        "question_type": "algorithm",
        "skill_areas": ["algorithms", "data_structures"],
        "difficulty_level": "medium",
        "estimated_time_minutes": 30,
        "expected_answer_summary": "BFS traversal. For each word, generate all possible one-letter transformations, check if in dictionary, add to queue if not visited.",
        "key_points": ["BFS", "graph modeling", "visited set", "bidirectional BFS optimization"],
        "followup_hints": ["Can you use bidirectional BFS to speed this up?", "What's your time and space complexity?"],
    },
    # Behavioral
    {
        "title": "Technical Decision with Incomplete Information",
        "content": "Tell me about a time you had to make an important technical decision without having all the information you needed. What was the situation, what decision did you make, and what was the outcome?",
        "question_type": "behavioral",
        "skill_areas": ["behavioral"],
        "difficulty_level": "medium",
        "estimated_time_minutes": 10,
        "expected_answer_summary": "STAR format: Situation, Task, Action, Result. Look for: clear reasoning under uncertainty, data-driven approach, risk assessment, learning from outcome.",
        "key_points": ["STAR format", "decision framework", "risk assessment", "learning mindset"],
        "followup_hints": ["What would you do differently?", "How did you communicate the uncertainty to stakeholders?"],
    },
    {
        "title": "Conflict Resolution with Teammate",
        "content": "Describe a situation where you had a significant technical disagreement with a colleague. How did you handle it? What was the result?",
        "question_type": "behavioral",
        "skill_areas": ["behavioral"],
        "difficulty_level": "medium",
        "estimated_time_minutes": 10,
        "expected_answer_summary": "Look for: professional handling, data-driven resolution, compromise, respect for other's perspective, positive outcome for the team",
        "key_points": ["conflict resolution", "communication", "data-driven", "compromise", "team outcome"],
        "followup_hints": ["What did you learn about working with different personalities?", "How did this change your approach to future disagreements?"],
    },
    # ML
    {
        "title": "Design a Recommendation System",
        "content": "Design a recommendation system for a streaming platform like Netflix. The system should recommend movies/shows to 200 million users. Discuss the ML approaches, data pipeline, and serving infrastructure.",
        "question_type": "ml",
        "skill_areas": ["machine_learning", "system_design"],
        "difficulty_level": "hard",
        "estimated_time_minutes": 50,
        "expected_answer_summary": "Collaborative filtering + content-based hybrid, matrix factorization (ALS/SVD), two-stage: retrieval + ranking, A/B testing, feature engineering from user behavior",
        "key_points": ["collaborative filtering", "content-based", "two-stage retrieval/ranking", "cold start problem", "A/B testing"],
        "followup_hints": ["How do you handle the cold start problem?", "How do you evaluate recommendation quality?", "How do you avoid filter bubbles?"],
    },
]


async def seed():
    print("🌱 Seeding database...")
    await create_all_tables()

    async with AsyncSessionLocal() as session:
        # Seed skill areas
        existing_skills = {}
        for skill_data in SKILL_AREAS:
            from sqlalchemy import select
            result = await session.execute(
                select(SkillArea).where(SkillArea.name == skill_data["name"])
            )
            existing = result.scalar_one_or_none()
            if not existing:
                skill = SkillArea(**skill_data)
                session.add(skill)
                await session.flush()
                existing_skills[skill_data["name"]] = skill
                print(f"  ✅ Skill area: {skill_data['name']}")
            else:
                existing_skills[skill_data["name"]] = existing
                print(f"  ⏭️  Skill area exists: {skill_data['name']}")

        # Seed sample questions
        for q_data in SAMPLE_QUESTIONS:
            from sqlalchemy import select
            result = await session.execute(
                select(Question).where(Question.title == q_data["title"])
            )
            if not result.scalar_one_or_none():
                q = Question(**q_data)
                session.add(q)
                print(f"  ✅ Question: {q_data['title']}")
            else:
                print(f"  ⏭️  Question exists: {q_data['title']}")

        await session.commit()
        print("\n✅ Database seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed())

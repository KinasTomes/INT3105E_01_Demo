"""
N+1 Query Problem SOLUTION

This file demonstrates the solution to the N+1 query problem using:
- Eager loading / JOIN simulation
- Only 2 queries total instead of N+1

This results in much better performance!
"""

from fastapi import FastAPI
from typing import List, Dict
from pydantic import BaseModel
import time
from collections import defaultdict

app = FastAPI(title="N+1 Query Problem Solution")

# Same fake database
users_db = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Charlie"},
    {"id": 4, "name": "Diana"},
    {"id": 5, "name": "Eve"},
]

posts_db = [
    {"id": 1, "user_id": 1, "title": "Alice's first post", "content": "Hello world!"},
    {"id": 2, "user_id": 1, "title": "Alice's second post", "content": "Another day"},
    {"id": 3, "user_id": 2, "title": "Bob's post", "content": "Bob here"},
    {"id": 4, "user_id": 2, "title": "Bob's thoughts", "content": "Thinking..."},
    {"id": 5, "user_id": 3, "title": "Charlie's update", "content": "Update from Charlie"},
    {"id": 6, "user_id": 4, "title": "Diana's story", "content": "Once upon a time"},
    {"id": 7, "user_id": 4, "title": "Diana's poem", "content": "Roses are red"},
    {"id": 8, "user_id": 5, "title": "Eve's article", "content": "Technical article"},
]

# Response models
class Post(BaseModel):
    id: int
    user_id: int
    title: str
    content: str

class UserWithPosts(BaseModel):
    id: int
    name: str
    posts: List[Post]

# Simulate database query delay
def simulate_query_delay():
    time.sleep(2)  # 100ms delay per query

def get_all_users() -> List[Dict]:
    """Simulates: SELECT * FROM users"""
    simulate_query_delay()
    return users_db.copy()

def get_all_posts() -> List[Dict]:
    """Simulates: SELECT * FROM posts (or JOIN query)"""
    simulate_query_delay()
    return posts_db.copy()

@app.get("/users-with-posts", response_model=List[UserWithPosts])
def get_users_with_posts_optimized():
    """
    SOLUTION: This endpoint solves the N+1 query problem.
    
    Optimization:
    - Query 1: Get all users
    - Query 2: Get ALL posts at once
    - Group posts by user_id in memory (no additional queries!)
    - Total: Only 2 queries instead of N+1
    """
    start_time = time.time()
    query_count = 0
    
    # Query 1: Get all users
    users = get_all_users()
    query_count += 1
    print(f"Query {query_count}: SELECT * FROM users")
    
    # Query 2: Get ALL posts at once (this is the key optimization!)
    all_posts = get_all_posts()
    query_count += 1
    print(f"Query {query_count}: SELECT * FROM posts (or JOIN users with posts)")
    
    # Group posts by user_id in memory (NO additional database queries)
    posts_by_user = defaultdict(list)
    for post in all_posts:
        posts_by_user[post["user_id"]].append(post)
    
    print("Grouping posts by user_id in memory (no DB query)")
    
    # Build result
    result = []
    for user in users:
        user_posts = posts_by_user.get(user["id"], [])
        result.append(UserWithPosts(
            id=user["id"],
            name=user["name"],
            posts=[Post(**post) for post in user_posts]
        ))
    
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds
    
    print(f"\n{'='*60}")
    print(f"OPTIMIZED SOLUTION RESULTS:")
    print(f"Total queries executed: {query_count}")
    print(f"Total time: {elapsed_time:.2f}ms")
    print(f"Average time per query: {elapsed_time/query_count:.2f}ms")
    print(f"{'='*60}\n")
    
    return result

@app.get("/comparison")
def get_comparison():
    """Compare N+1 problem vs solution"""
    num_users = len(users_db)
    
    # Simulate timing for N+1 problem
    n_plus_1_queries = num_users + 1
    n_plus_1_time = n_plus_1_queries * 10  # 10ms per query
    
    # Simulate timing for optimized solution
    optimized_queries = 2
    optimized_time = optimized_queries * 10  # 10ms per query
    
    improvement = ((n_plus_1_time - optimized_time) / n_plus_1_time) * 100
    
    return {
        "n_plus_1_problem": {
            "queries": n_plus_1_queries,
            "estimated_time_ms": n_plus_1_time,
            "description": "1 query for users + N queries for each user's posts"
        },
        "optimized_solution": {
            "queries": optimized_queries,
            "estimated_time_ms": optimized_time,
            "description": "1 query for users + 1 query for all posts (then group in memory)"
        },
        "improvement": {
            "queries_saved": n_plus_1_queries - optimized_queries,
            "time_saved_ms": n_plus_1_time - optimized_time,
            "performance_improvement_percent": f"{improvement:.1f}%"
        },
        "note": "As the number of users grows, the performance difference becomes more dramatic!"
    }

@app.get("/stats")
def get_stats():
    """Get database statistics"""
    return {
        "total_users": len(users_db),
        "total_posts": len(posts_db),
        "n_plus_1_queries": len(users_db) + 1,
        "optimized_queries": 2,
        "queries_saved": (len(users_db) + 1) - 2
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting N+1 Query Problem SOLUTION Server...")
    print("Try: http://127.0.0.1:8002/users-with-posts")
    print("Try: http://127.0.0.1:8002/comparison")
    print("Try: http://127.0.0.1:8002/stats")
    uvicorn.run(app, host="127.0.0.1", port=8002)

"""
N+1 Query Problem Demonstration

This file demonstrates the N+1 query problem where:
- 1 query to get all users
- N queries (one for each user) to get their posts

This results in poor performance due to multiple database calls.
"""

from fastapi import FastAPI
from typing import List, Dict
from pydantic import BaseModel
import time

app = FastAPI(title="N+1 Query Problem Demo")

# Fake database using arrays
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

# Simulate database query delay (in real DB, this would be network/IO time)
def simulate_query_delay():
    time.sleep(2)  # 10ms delay per query

def get_all_users() -> List[Dict]:
    """Simulates: SELECT * FROM users"""
    simulate_query_delay()
    return users_db.copy()

def get_posts_by_user_id(user_id: int) -> List[Dict]:
    """Simulates: SELECT * FROM posts WHERE user_id = ?"""
    simulate_query_delay()
    return [post for post in posts_db if post["user_id"] == user_id]

@app.get("/users-with-posts", response_model=List[UserWithPosts])
def get_users_with_posts_n_plus_1():
    """
    This endpoint demonstrates the N+1 query problem.
    
    Performance issue:
    - 1 query to get all users (N users)
    - N queries to get posts for each user
    - Total: N+1 queries
    """
    start_time = time.time()
    query_count = 0
    
    # Query 1: Get all users
    users = get_all_users()
    query_count += 1
    print(f"Query {query_count}: SELECT * FROM users")
    
    result = []
    
    # N queries: Get posts for each user (N+1 problem!)
    for user in users:
        user_posts = get_posts_by_user_id(user["id"])
        query_count += 1
        print(f"Query {query_count}: SELECT * FROM posts WHERE user_id = {user['id']}")
        
        result.append(UserWithPosts(
            id=user["id"],
            name=user["name"],
            posts=[Post(**post) for post in user_posts]
        ))
    
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds
    
    print(f"\n{'='*60}")
    print(f"N+1 QUERY PROBLEM RESULTS:")
    print(f"Total queries executed: {query_count}")
    print(f"Total time: {elapsed_time:.2f}ms")
    print(f"Average time per query: {elapsed_time/query_count:.2f}ms")
    print(f"{'='*60}\n")
    
    return result

@app.get("/stats")
def get_stats():
    """Get database statistics"""
    return {
        "total_users": len(users_db),
        "total_posts": len(posts_db),
        "expected_queries_n_plus_1": len(users_db) + 1,
        "note": "With N+1 problem, you'll execute N+1 queries where N is the number of users"
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting N+1 Query Problem Demo Server...")
    print("Try: http://127.0.0.1:8001/users-with-posts")
    print("Try: http://127.0.0.1:8001/stats")
    uvicorn.run(app, host="127.0.0.1", port=8001)

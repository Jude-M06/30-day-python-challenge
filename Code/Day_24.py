#-------------------------------------------
# you need to install fastapi uvicorn first
# python -m pip install fastapi uvicorn
#-------------------------------------------

from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator


class BookCreate(BaseModel):
    title:  str   = Field(..., min_length=1, max_length=200)
    author: str   = Field(..., min_length=1, max_length=100)
    year:   int   = Field(..., ge=1000, le=2100)
    genre:  str   = Field(default="Unknown", max_length=50)
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    read:   bool  = False
    notes:  str   = Field(default="", max_length=1000)

    @field_validator("title", "author")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()

class Book(BookCreate):
    id:         int
    created_at: str

class BookUpdate(BaseModel):
    title:  Optional[str]   = None
    author: Optional[str]   = None
    year:   Optional[int]   = None
    genre:  Optional[str]   = None
    rating: Optional[float] = None
    read:   Optional[bool]  = None
    notes:  Optional[str]   = None

app = FastAPI(
    title="Bookshelf API",
    description="A CRUD REST API for managing your book collection.",
    version="1.0.0",
)


db: list[dict] = [
    {"id": 1, "title": "The Pragmatic Programmer", "author": "David Thomas",
     "year": 1999, "genre": "Tech", "rating": 4.8, "read": True,
     "notes": "Essential reading.", "created_at": "2025-06-01 09:00"},
    {"id": 2, "title": "Clean Code", "author": "Robert C. Martin",
     "year": 2008, "genre": "Tech", "rating": 4.5, "read": True,
     "notes": "Good habits.", "created_at": "2025-06-01 09:01"},
    {"id": 3, "title": "Dune", "author": "Frank Herbert",
     "year": 1965, "genre": "Sci-Fi", "rating": 4.9, "read": False,
     "notes": "", "created_at": "2025-06-01 09:02"},
]

def next_id() -> int:
    return max((b["id"] for b in db), default=0) + 1

def find_book(book_id: int) -> dict:
    book = next((b for b in db if b["id"] == book_id), None)
    if not book:
        raise HTTPException(status_code=404,
                            detail=f"Book {book_id} not found.")
    return book

@app.get("/books", response_model=list[Book], tags=["Books"])
def list_books(
    genre:   Optional[str]  = Query(None, description="Filter by genre"),
    read:    Optional[bool] = Query(None, description="Filter by read status"),
    sort_by: Optional[str]  = Query(None, enum=["title","author","year","rating"],
                                    description="Sort field"),
):
    results = list(db)
    if genre:
        results = [b for b in results if b["genre"].lower() == genre.lower()]
    if read is not None:
        results = [b for b in results if b["read"] == read]
    if sort_by:
        results.sort(key=lambda b: b.get(sort_by, ""))
    return results

@app.get("/books/search", response_model=list[Book], tags=["Books"])
def search_books(q: str = Query(..., min_length=1, description="Search query")):
    q_lower = q.lower()
    return [
        b for b in db
        if q_lower in b["title"].lower()
        or q_lower in b["author"].lower()
        or q_lower in b.get("notes", "").lower()
    ]

@app.get("/books/{book_id}", response_model=Book, tags=["Books"])
def get_book(book_id: int):
    return find_book(book_id)

@app.post("/books", response_model=Book,
          status_code=status.HTTP_201_CREATED, tags=["Books"])
def create_book(payload: BookCreate):
    book = {
        "id":         next_id(),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        **payload.model_dump(),
    }
    db.append(book)
    return book

@app.put("/books/{book_id}", response_model=Book, tags=["Books"])
def replace_book(book_id: int, payload: BookCreate):
    book = find_book(book_id)
    book.update({
        **payload.model_dump(),
        "id":         book_id,
        "created_at": book["created_at"],
    })
    return book

@app.patch("/books/{book_id}", response_model=Book, tags=["Books"])
def update_book(book_id: int, payload: BookUpdate):
    book = find_book(book_id)
    updates = payload.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided.")
    book.update(updates)
    return book

@app.delete("/books/{book_id}",
            status_code=status.HTTP_204_NO_CONTENT, tags=["Books"])
def delete_book(book_id: int):
    book = find_book(book_id)
    db.remove(book)

@app.get("/stats", tags=["Stats"])
def get_stats():
    if not db:
        return {"total": 0}
    ratings = [b["rating"] for b in db if b["rating"] > 0]
    genres  = {}
    for b in db:
        genres[b["genre"]] = genres.get(b["genre"], 0) + 1
    return {
        "total":       len(db),
        "read":        sum(1 for b in db if b["read"]),
        "unread":      sum(1 for b in db if not b["read"]),
        "avg_rating":  round(sum(ratings) / len(ratings), 2) if ratings else 0,
        "top_genre":   max(genres, key=genres.get) if genres else None,
        "genres":      genres,
    }

# --- run ---
# uvicorn main:app --reload

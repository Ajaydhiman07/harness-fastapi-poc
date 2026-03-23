from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="Harness FastAPI POC",
    description="A sample FastAPI app for Harness CI/CD POC",
    version="1.0.0"
)

# ---------- Models ----------

class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    in_stock: bool = True

# ---------- In-memory DB ----------

items_db: dict = {}
counter = {"id": 1}

# ---------- Routes ----------

@app.get("/")
def root():
    return {"message": "Harness FastAPI POC is running!", "status": "healthy"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/items", response_model=List[Item])
def get_items():
    return list(items_db.values())

@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]

@app.post("/items", response_model=Item, status_code=201)
def create_item(item: Item):
    item.id = counter["id"]
    items_db[counter["id"]] = item
    counter["id"] += 1
    return item

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: Item):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    item.id = item_id
    items_db[item_id] = item
    return item

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
    return {"message": f"Item {item_id} deleted successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

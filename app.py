from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, Item  # Import database session and Item model
from pydantic import BaseModel
import time
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TransformData(BaseModel):
    location: list[float] | None = None
    rotation: list[float] | None = None
    scale: list[float] | None = None

class ItemBase(BaseModel):
    name: str
    quantity: int

# 🔹 10-second delay only for transformation endpoints
@app.post("/transform")
async def transform(data: TransformData):
    time.sleep(10)
    logging.info(f"Received transform data: {data}")
    if not any([data.location, data.rotation, data.scale]):
        raise HTTPException(status_code=400, detail="At least one transform required.")
    return {"message": "Transform data received successfully"}

@app.post("/translation")
async def translation(data: TransformData):
    time.sleep(10)
    if not data.location:
        raise HTTPException(status_code=400, detail="Location data is required.")
    logging.info(f"Received translation data: {data.location}")
    return {"message": "Translation received successfully"}

@app.post("/rotation")
async def rotation(data: TransformData):
    time.sleep(10)
    if not data.rotation:
        raise HTTPException(status_code=400, detail="Rotation data is required.")
    logging.info(f"Received rotation data: {data.rotation}")
    return {"message": "Rotation received successfully"}

@app.post("/scale")
async def scale(data: TransformData):
    time.sleep(10)
    if not data.scale:
        raise HTTPException(status_code=400, detail="Scale data is required.")
    logging.info(f"Received scale data: {data.scale}")
    return {"message": "Scale received successfully"}

# 🔹 Get File Path
@app.get("/file-path")
async def get_file_path(projectpath: bool = False):
    file_path = "C:\\Users\\ADMIN\\OneDrive\\Desktop\\Blender\\dcc_plugin\\my_project.blend"
    project_path = "C:\\Users\\ADMIN\\OneDrive\\Desktop\\Blender\\dcc_plugin"
    return {"path": project_path if projectpath else file_path}

# 🔹 Add Item to Inventory
@app.post("/add-item")
async def add_item(item: ItemBase, db: Session = Depends(get_db)):
    existing_item = db.query(Item).filter(Item.name.ilike(item.name)).first()
    if existing_item:
        raise HTTPException(status_code=400, detail="Item already exists.")
    
    new_item = Item(name=item.name, quantity=item.quantity)
    db.add(new_item)
    db.commit()
    logging.info(f"Item added: {new_item.name} ({new_item.quantity})")
    return {"message": "Item added successfully"}

# 🔹 Remove Item from Inventory
@app.post("/remove-item")
async def remove_item(item: ItemBase, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.name.ilike(item.name)).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found.")
    
    db.delete(db_item)
    db.commit()
    logging.info(f"Item removed: {item.name}")
    return {"message": "Item removed successfully"}

# 🔹 Update Quantity (Purchase/Return)
@app.post("/update-quantity")
async def update_quantity(item: ItemBase, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.name.ilike(item.name)).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found.")
    
    # Ensure quantity does not go negative
    db_item.quantity = max(0, db_item.quantity + item.quantity)
    db.commit()
    
    action = "purchased" if item.quantity > 0 else "returned"
    logging.info(f"{item.quantity} units {action} for {item.name}. New quantity: {db_item.quantity}")
    return {"message": f"Item {action} successfully", "new_quantity": db_item.quantity}

# 🔹 Get Inventory
@app.get("/get-inventory")
async def get_inventory(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return [{"name": item.name, "quantity": item.quantity} for item in items]

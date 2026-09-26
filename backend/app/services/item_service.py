from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate

class ItemService:
    """Service layer handling database operations for Items."""

    @staticmethod
    def get_items(db: Session, skip: int = 0, limit: int = 100) -> List[Item]:
        return db.query(Item).offset(skip).limit(limit).all()

    @staticmethod
    def get_item_by_id(db: Session, item_id: int) -> Optional[Item]:
        return db.query(Item).filter(Item.id == item_id).first()

    @staticmethod
    def create_item(db: Session, item_in: ItemCreate) -> Item:
        db_item = Item(
            title=item_in.title,
            description=item_in.description,
            category=item_in.category,
            is_active=item_in.is_active
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    @staticmethod
    def update_item(db: Session, item_id: int, item_in: ItemUpdate) -> Optional[Item]:
        db_item = ItemService.get_item_by_id(db, item_id)
        if not db_item:
            return None
        
        update_data = item_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)
            
        db.commit()
        db.refresh(db_item)
        return db_item

    @staticmethod
    def delete_item(db: Session, item_id: int) -> bool:
        db_item = ItemService.get_item_by_id(db, item_id)
        if not db_item:
            return False
        db.delete(db_item)
        db.commit()
        return True

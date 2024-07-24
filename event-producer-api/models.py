# app/models.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Union, Optional

class ProductUpdate(BaseModel):
    product_id: str
    name: str
    price: float = Field(gt=0)
    category: str
    brand: str
    stock_quantity: int = Field(ge=0)
    weight: float = Field(gt=0)
    dimensions: str
    expiration_date: Optional[datetime] = None

class DepartmentData(BaseModel):
    department_id: str
    name: str
    manager: str
    product_count: int = Field(ge=0)
    total_sales: float = Field(ge=0)
    last_updated: Optional[datetime] = None

class ProductPromotion(BaseModel):
    product_id: str
    promotion_type: str
    discount_percentage: float = Field(ge=0, le=100)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    minimum_quantity: int = Field(default=1, ge=1)
    maximum_discount: Optional[float] = None
    
class Event(BaseModel):
    topic: str
    data: Union[ProductUpdate, DepartmentData, ProductPromotion]
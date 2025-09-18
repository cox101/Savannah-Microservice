from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


# Customer Schemas
class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)
    phone_number: Optional[str] = Field(None, max_length=20)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)


class Customer(CustomerBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomerWithOrders(Customer):
    orders: List["Order"] = []


# Order Schemas
class OrderBase(BaseModel):
    item: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., gt=0)


class OrderCreate(OrderBase):
    customer_id: int


class OrderUpdate(BaseModel):
    item: Optional[str] = Field(None, min_length=1, max_length=200)
    amount: Optional[float] = Field(None, gt=0)


class Order(OrderBase):
    id: int
    customer_id: int
    time: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderWithCustomer(Order):
    customer: Customer


# Response Schemas
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


# Update forward references
CustomerWithOrders.model_rebuild()
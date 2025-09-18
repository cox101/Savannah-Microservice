from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


# Customer Schemas
@dataclass
class CustomerBase:
    name: str
    code: str
    phone_number: Optional[str] = None


@dataclass
class CustomerCreate(CustomerBase):
    pass


@dataclass
class CustomerUpdate:
    name: Optional[str] = None
    phone_number: Optional[str] = None


@dataclass
class Customer(CustomerBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# Order Schemas
@dataclass
class OrderBase:
    item: str
    amount: float


@dataclass
class OrderCreate(OrderBase):
    customer_id: int


@dataclass
class OrderUpdate:
    item: Optional[str] = None
    amount: Optional[float] = None


@dataclass
class Order(OrderBase):
    id: int
    customer_id: int
    time: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None


# Response Schemas
@dataclass
class APIResponse:
    success: bool
    message: str
    data: Optional[dict] = None
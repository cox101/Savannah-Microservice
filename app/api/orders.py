from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_user_mock as get_current_user  # Use mock for now
from app.models.models import Order, Customer
from app.schemas.schemas import Order as OrderSchema, OrderCreate, OrderUpdate, OrderWithCustomer
from app.services.sms_service import sms_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


async def send_order_sms(customer: Customer, order: Order):
    """Background task to send SMS notification"""
    if customer.phone_number:
        success = await sms_service.send_order_notification(
            customer.phone_number,
            customer.name,
            order.item,
            order.amount
        )
        if success:
            logger.info(f"SMS notification sent for order {order.id}")
        else:
            logger.warning(f"Failed to send SMS notification for order {order.id}")
    else:
        logger.info(f"No phone number for customer {customer.code}, skipping SMS")


@router.post("/", response_model=OrderSchema)
async def create_order(
    order: OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new order"""
    try:
        # Check if customer exists
        customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer not found"
            )
        
        db_order = Order(**order.dict())
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        # Send SMS notification in background
        background_tasks.add_task(send_order_sms, customer, db_order)
        
        logger.info(f"Created order: {db_order.id} for customer {customer.code}")
        return db_order
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order"
        )


@router.get("/", response_model=List[OrderWithCustomer])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    customer_id: int = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all orders, optionally filtered by customer"""
    query = db.query(Order)
    
    if customer_id:
        query = query.filter(Order.customer_id == customer_id)
    
    orders = query.offset(skip).limit(limit).all()
    return orders


@router.get("/{order_id}", response_model=OrderWithCustomer)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific order by ID"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order


@router.put("/{order_id}", response_model=OrderSchema)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update an order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    try:
        update_data = order_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)
        
        db.commit()
        db.refresh(order)
        
        logger.info(f"Updated order: {order.id}")
        return order
        
    except Exception as e:
        logger.error(f"Error updating order: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order"
        )


@router.delete("/{order_id}")
async def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete an order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    try:
        db.delete(order)
        db.commit()
        
        logger.info(f"Deleted order: {order.id}")
        return {"message": "Order deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting order: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete order"
        )
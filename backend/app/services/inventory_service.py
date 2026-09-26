import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.receipt import Receipt, ReceiptItem
from app.models.delivery import Delivery, DeliveryItem
from app.models.transfer import InternalTransfer
from app.models.adjustment import StockAdjustment
from app.schemas.receipt import ReceiptCreate
from app.schemas.delivery import DeliveryCreate
from app.schemas.transfer import TransferCreate
from app.schemas.adjustment import AdjustmentCreate
from app.services.ledger_service import LedgerService

class InventoryService:
    """Service handling Receipts, Deliveries, Transfers, and Adjustments operations."""

    # --------------------------------------------------------------------------
    # RECEIPTS (Incoming)
    # --------------------------------------------------------------------------
    @staticmethod
    def create_receipt(db: Session, data: ReceiptCreate) -> Receipt:
        receipt_no = f"REC-{uuid.uuid4().hex[:8].upper()}"
        receipt = Receipt(
            receipt_number=receipt_no,
            supplier_name=data.supplier_name,
            status="Draft"
        )
        db.add(receipt)
        db.flush()

        for item_data in data.items:
            item = ReceiptItem(
                receipt_id=receipt.id,
                product_id=item_data.product_id,
                location_id=item_data.location_id,
                quantity=item_data.quantity
            )
            db.add(item)

        db.commit()
        db.refresh(receipt)
        return receipt

    @staticmethod
    def validate_receipt(db: Session, receipt_id: int) -> Receipt:
        receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
        if not receipt:
            raise HTTPException(status_code=404, detail=f"Receipt #{receipt_id} not found")
        if receipt.status == "Done":
            raise HTTPException(status_code=400, detail="Receipt has already been validated")

        # Record stock movement in ledger for each line item (+qty)
        for item in receipt.items:
            LedgerService.record_move(
                db=db,
                product_id=item.product_id,
                location_id=item.location_id,
                qty_delta=item.quantity,
                source_doc_type="RECEIPT",
                source_doc_id=receipt.id
            )

        receipt.status = "Done"
        db.commit()
        db.refresh(receipt)
        return receipt

    @staticmethod
    def list_receipts(db: Session, skip: int = 0, limit: int = 100) -> List[Receipt]:
        return db.query(Receipt).offset(skip).limit(limit).all()

    # --------------------------------------------------------------------------
    # DELIVERIES (Outgoing)
    # --------------------------------------------------------------------------
    @staticmethod
    def create_delivery(db: Session, data: DeliveryCreate) -> Delivery:
        delivery_no = f"DEL-{uuid.uuid4().hex[:8].upper()}"
        delivery = Delivery(
            delivery_number=delivery_no,
            customer_name=data.customer_name,
            status="Draft"
        )
        db.add(delivery)
        db.flush()

        for item_data in data.items:
            item = DeliveryItem(
                delivery_id=delivery.id,
                product_id=item_data.product_id,
                location_id=item_data.location_id,
                quantity=item_data.quantity
            )
            db.add(item)

        db.commit()
        db.refresh(delivery)
        return delivery

    @staticmethod
    def validate_delivery(db: Session, delivery_id: int) -> Delivery:
        delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
        if not delivery:
            raise HTTPException(status_code=404, detail=f"Delivery #{delivery_id} not found")
        if delivery.status == "Done":
            raise HTTPException(status_code=400, detail="Delivery has already been validated")

        # Validate stock availability and record stock reduction in ledger (-qty)
        for item in delivery.items:
            current_stock = LedgerService.get_current_stock(db, item.product_id, item.location_id)
            if current_stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for Product #{item.product_id} at Location #{item.location_id}. Available: {current_stock}, Requested: {item.quantity}"
                )

            LedgerService.record_move(
                db=db,
                product_id=item.product_id,
                location_id=item.location_id,
                qty_delta=-item.quantity,
                source_doc_type="DELIVERY",
                source_doc_id=delivery.id
            )

        delivery.status = "Done"
        db.commit()
        db.refresh(delivery)
        return delivery

    @staticmethod
    def list_deliveries(db: Session, skip: int = 0, limit: int = 100) -> List[Delivery]:
        return db.query(Delivery).offset(skip).limit(limit).all()

    # --------------------------------------------------------------------------
    # TRANSFERS (Internal Move)
    # --------------------------------------------------------------------------
    @staticmethod
    def create_transfer(db: Session, data: TransferCreate) -> InternalTransfer:
        transfer_no = f"TRF-{uuid.uuid4().hex[:8].upper()}"
        transfer = InternalTransfer(
            transfer_number=transfer_no,
            product_id=data.product_id,
            from_location_id=data.from_location_id,
            to_location_id=data.to_location_id,
            quantity=data.quantity,
            status="Draft"
        )
        db.add(transfer)
        db.commit()
        db.refresh(transfer)
        return transfer

    @staticmethod
    def validate_transfer(db: Session, transfer_id: int) -> InternalTransfer:
        transfer = db.query(InternalTransfer).filter(InternalTransfer.id == transfer_id).first()
        if not transfer:
            raise HTTPException(status_code=404, detail=f"Transfer #{transfer_id} not found")
        if transfer.status == "Done":
            raise HTTPException(status_code=400, detail="Transfer has already been validated")

        current_stock = LedgerService.get_current_stock(db, transfer.product_id, transfer.from_location_id)
        if current_stock < transfer.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock at source Location #{transfer.from_location_id}. Available: {current_stock}, Requested: {transfer.quantity}"
            )

        # 1. Deduct from source location (-qty)
        LedgerService.record_move(
            db=db,
            product_id=transfer.product_id,
            location_id=transfer.from_location_id,
            qty_delta=-transfer.quantity,
            source_doc_type="TRANSFER_OUT",
            source_doc_id=transfer.id
        )

        # 2. Add to target location (+qty)
        LedgerService.record_move(
            db=db,
            product_id=transfer.product_id,
            location_id=transfer.to_location_id,
            qty_delta=transfer.quantity,
            source_doc_type="TRANSFER_IN",
            source_doc_id=transfer.id
        )

        transfer.status = "Done"
        db.commit()
        db.refresh(transfer)
        return transfer

    # --------------------------------------------------------------------------
    # ADJUSTMENTS (Count Reconciliation)
    # --------------------------------------------------------------------------
    @staticmethod
    def create_adjustment(db: Session, data: AdjustmentCreate) -> StockAdjustment:
        if data.counted_qty < 0:
            raise HTTPException(status_code=400, detail="Counted physical quantity cannot be negative")

        adj_no = f"ADJ-{uuid.uuid4().hex[:8].upper()}"
        system_qty = LedgerService.get_current_stock(db, data.product_id, data.location_id)
        delta_qty = data.counted_qty - system_qty

        adjustment = StockAdjustment(
            adjustment_number=adj_no,
            product_id=data.product_id,
            location_id=data.location_id,
            counted_qty=data.counted_qty,
            system_qty=system_qty,
            delta_qty=delta_qty,
            reason=data.reason
        )
        db.add(adjustment)
        db.flush()

        # Update stock ledger with delta_qty
        if delta_qty != 0:
            LedgerService.record_move(
                db=db,
                product_id=data.product_id,
                location_id=data.location_id,
                qty_delta=delta_qty,
                source_doc_type="ADJUSTMENT",
                source_doc_id=adjustment.id
            )

        db.commit()
        db.refresh(adjustment)
        return adjustment

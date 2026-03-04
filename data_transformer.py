"""
Phase 3: Data Transformation
=============================
Real-world scenario:
  Monday.com sends us a board item when a project is marked "Ready to Invoice".
  We need to transform that raw Monday data into a format Xero accepts for
  creating a draft invoice.

This is the core skill of automation engineering.
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional
import json
import logging

# Set up logging (professional alternative to print statements)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ── Step 1: Define what Monday.com sends us ──────────────────────────────────

class MondayItem(BaseModel):
    """Represents a board item from Monday.com"""
    item_id: str
    item_name: str
    client_name: str
    client_email: EmailStr
    project_description: str
    amount: float
    hours_worked: Optional[float] = None
    due_date: str  # Monday sends dates as strings e.g. "2026-03-15"
    status: str


# ── Step 2: Define what Xero expects ────────────────────────────────────────

class XeroLineItem(BaseModel):
    """A single line item on a Xero invoice"""
    Description: str
    Quantity: float
    UnitAmount: float
    AccountCode: str = "200"  # Default revenue account


class XeroInvoice(BaseModel):
    """A draft invoice ready to send to the Xero API"""
    Type: str = "ACCREC"           # Accounts Receivable
    Status: str = "DRAFT"
    ContactName: str
    ContactEmail: str
    DueDate: str                   # Xero requires YYYY-MM-DD
    LineItems: list[XeroLineItem]
    Reference: str                 # Links back to Monday item ID
    CurrencyCode: str = "AUD"


# ── Step 3: Write the transformer function ───────────────────────────────────

def transform_monday_to_xero(monday_item: MondayItem) -> XeroInvoice:
    """
    Takes a validated Monday.com item and returns a Xero-ready invoice.
    This is the core data mapping function.
    """
    logger.info(f"Transforming Monday item '{monday_item.item_name}' for {monday_item.client_name}")

    try:
        # Transform the date from Monday format to Xero format
        # Both happen to use YYYY-MM-DD but we parse/reformat to be safe
        due_date = datetime.strptime(monday_item.due_date, "%Y-%m-%d").date()
        xero_due_date = due_date.strftime("%Y-%m-%d")
    except ValueError as e:
        logger.error(f"Invalid date format in Monday item: {monday_item.due_date}")
        raise ValueError(f"Could not parse due_date '{monday_item.due_date}': {e}")

    # Build the line item
    line_item = XeroLineItem(
        Description=monday_item.project_description,
        Quantity=monday_item.hours_worked if monday_item.hours_worked else 1.0,
        UnitAmount=monday_item.amount if not monday_item.hours_worked else monday_item.amount / monday_item.hours_worked,
    )

    # Build the full Xero invoice
    xero_invoice = XeroInvoice(
        ContactName=monday_item.client_name,
        ContactEmail=monday_item.client_email,
        DueDate=xero_due_date,
        LineItems=[line_item],
        Reference=f"MONDAY-{monday_item.item_id}",
    )

    logger.info(f"Successfully transformed to Xero invoice. Reference: {xero_invoice.Reference}")
    return xero_invoice


# ── Step 4: Test it with fake Monday data ────────────────────────────────────

if __name__ == "__main__":

    test_payloads = [
        # ── Test 1: Perfect payload (should succeed) ──
        {
            "label": "GOOD PAYLOAD",
            "data": {
                "item_id": "9182736450",
                "item_name": "Website Redesign - Phase 2",
                "client_name": "Stark Industries",
                "client_email": "accounts@stark.com",
                "project_description": "Website redesign and development - Phase 2 completion",
                "amount": 4500.00,
                "hours_worked": 30.0,
                "due_date": "2026-04-01",
                "status": "Ready to Invoice"
            }
        },
        # ── Test 2: Invalid email (Pydantic bouncer should catch this) ──
        {
            "label": "BAD EMAIL",
            "data": {
                "item_id": "1111111111",
                "item_name": "Broken Email Test",
                "client_name": "Wayne Enterprises",
                "client_email": "not-a-valid-email",
                "project_description": "Testing invalid email handling",
                "amount": 1000.00,
                "due_date": "2026-04-15",
                "status": "Ready to Invoice"
            }
        },
        # ── Test 3: Wrong date format (try/except should catch this) ──
        {
            "label": "BAD DATE",
            "data": {
                "item_id": "2222222222",
                "item_name": "Broken Date Test",
                "client_name": "Oscorp",
                "client_email": "billing@oscorp.com",
                "project_description": "Testing invalid date handling",
                "amount": 2000.00,
                "due_date": "15/04/2026",  # Wrong format — Xero needs YYYY-MM-DD
                "status": "Ready to Invoice"
            }
        },
    ]

    for test in test_payloads:
        print(f"\n{'='*50}")
        print(f"TEST: {test['label']}")
        print('='*50)
        try:
            monday_item = MondayItem(**test["data"])
            xero_invoice = transform_monday_to_xero(monday_item)
            print(json.dumps(xero_invoice.model_dump(), indent=2))
        except Exception as e:
            logger.error(f"Caught error gracefully: {e}")

from __future__ import annotations

import os
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, create_engine, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / '.env')
DATABASE_URL = os.getenv('DATABASE_URL', '')
if not DATABASE_URL:
    raise RuntimeError('Set DATABASE_URL in a .env file. Copy .env.example first.')

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Client(Base):
    __tablename__ = 'clients'
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(160))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    invoices: Mapped[list['Invoice']] = relationship(back_populates='client')

class Invoice(Base):
    __tablename__ = 'invoices'
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    number: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(16), default='sent')
    issue_date: Mapped[date] = mapped_column(Date)
    due_date: Mapped[date] = mapped_column(Date)
    terms: Mapped[str] = mapped_column(String(100), default='Due in 14 days')
    notes: Mapped[str] = mapped_column(Text, default='')
    terms_text: Mapped[str] = mapped_column(Text, default='')
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    client_id: Mapped[UUID] = mapped_column(ForeignKey('clients.id'))
    client: Mapped[Client] = relationship(back_populates='invoices')
    items: Mapped[list['InvoiceItem']] = relationship(back_populates='invoice', cascade='all, delete-orphan')

class InvoiceItem(Base):
    __tablename__ = 'invoice_items'
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    description: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    rate: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    invoice_id: Mapped[UUID] = mapped_column(ForeignKey('invoices.id'))
    invoice: Mapped[Invoice] = relationship(back_populates='items')

class ItemInput(BaseModel):
    description: str = Field(min_length=1, max_length=255)
    quantity: Decimal = Field(gt=0)
    rate: Decimal = Field(ge=0)

class InvoiceInput(BaseModel):
    clientName: str = Field(min_length=1, max_length=160)
    clientEmail: EmailStr
    issueDate: date
    dueDate: date
    terms: str = 'Due in 14 days'
    notes: str = ''
    termsText: str = ''
    items: list[ItemInput] = Field(min_length=1)

class StatusInput(BaseModel):
    status: str = Field(pattern='^(draft|sent|paid|overdue)$')

def get_db():
    with SessionLocal() as db:
        yield db

def serialize(invoice: Invoice):
    return {'id': str(invoice.id), 'number': invoice.number, 'status': invoice.status, 'clientName': invoice.client.name, 'clientEmail': invoice.client.email, 'issueDate': invoice.issue_date.isoformat(), 'dueDate': invoice.due_date.isoformat(), 'terms': invoice.terms, 'notes': invoice.notes, 'termsText': invoice.terms_text, 'subtotal': float(invoice.subtotal), 'total': float(invoice.total), 'createdAt': invoice.created_at.isoformat(), 'items': [{'description': item.description, 'quantity': float(item.quantity), 'rate': float(item.rate)} for item in invoice.items]}

app = FastAPI(title='Vanta Invoice API', version='1.0.0')

@app.on_event('startup')
def create_tables():
    Base.metadata.create_all(engine)

@app.get('/api/health')
def health():
    return {'ok': True, 'database': 'postgresql'}

@app.get('/api/invoices')
def list_invoices(db: Session = Depends(get_db)):
    return [serialize(invoice) for invoice in db.scalars(select(Invoice).order_by(Invoice.created_at.desc())).all()]

@app.post('/api/invoices', status_code=201)
def create_invoice(payload: InvoiceInput, db: Session = Depends(get_db)):
    if payload.dueDate < payload.issueDate:
        raise HTTPException(422, 'Due date cannot be earlier than issue date.')
    client = db.scalar(select(Client).where(Client.email == str(payload.clientEmail)))
    if client is None:
        client = Client(name=payload.clientName.strip(), email=str(payload.clientEmail))
        db.add(client)
        db.flush()
    else:
        client.name = payload.clientName.strip()
    subtotal = sum(item.quantity * item.rate for item in payload.items)
    count = len(db.scalars(select(Invoice.id)).all()) + 1
    invoice = Invoice(number=f'INV-{date.today().year}-{count:03d}', client=client, issue_date=payload.issueDate, due_date=payload.dueDate, terms=payload.terms, notes=payload.notes, terms_text=payload.termsText, subtotal=subtotal, total=subtotal, status='sent')
    invoice.items = [InvoiceItem(description=item.description.strip(), quantity=item.quantity, rate=item.rate) for item in payload.items]
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return serialize(invoice)

@app.patch('/api/invoices/{invoice_id}/status')
def update_status(invoice_id: UUID, payload: StatusInput, db: Session = Depends(get_db)):
    invoice = db.get(Invoice, invoice_id)
    if invoice is None:
        raise HTTPException(404, 'Invoice not found.')
    invoice.status = payload.status
    db.commit()
    db.refresh(invoice)
    return serialize(invoice)

app.mount('/', StaticFiles(directory=ROOT, html=True), name='frontend')

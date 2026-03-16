"""
Sampoorna Home Services — FastAPI Backend
Run with: uvicorn sampoorna-backend:app --reload --port 8000
Install: pip install fastapi uvicorn pydantic python-multipart
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
import json

app = FastAPI(title="Sampoorna Home Services API", version="1.0.0")

# CORS — allow the React frontend (adjust origin in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory stores (replace with a real DB in production)
contact_submissions = []
newsletter_subscribers = []
booking_enquiries = []


# ── Schemas ────────────────────────────────────────────────────────────────────

class ContactForm(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    message: str

class NewsletterSignup(BaseModel):
    email: str
    name: Optional[str] = None

class BookingEnquiry(BaseModel):
    name: str
    email: str
    phone: str
    service_type: str          # moving / repairs / maintenance / cleaning
    preferred_date: str        # ISO date string
    city: str
    notes: Optional[str] = None


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Sampoorna Home Services API is running ✅"}


@app.post("/api/contact")
def submit_contact(form: ContactForm):
    """Accept a general contact-form submission."""
    entry = {
        "id": len(contact_submissions) + 1,
        "name": form.name,
        "email": form.email,
        "phone": form.phone,
        "message": form.message,
        "submitted_at": datetime.utcnow().isoformat(),
    }
    contact_submissions.append(entry)
    # TODO: send email notification here (e.g. via SendGrid / SMTP)
    return {"success": True, "message": "Thank you! We'll get back to you within 24 hours."}


@app.post("/api/newsletter")
def subscribe_newsletter(data: NewsletterSignup):
    """Subscribe an email to the newsletter."""
    # Prevent duplicates
    existing = [s for s in newsletter_subscribers if s["email"] == data.email]
    if existing:
        return {"success": True, "message": "You're already subscribed — thank you!"}
    entry = {
        "id": len(newsletter_subscribers) + 1,
        "email": data.email,
        "name": data.name,
        "subscribed_at": datetime.utcnow().isoformat(),
    }
    newsletter_subscribers.append(entry)
    return {"success": True, "message": "Subscribed successfully! Welcome aboard."}


@app.post("/api/booking")
def create_booking(booking: BookingEnquiry):
    """Create a relocation-service booking enquiry."""
    allowed_services = ["moving", "repairs", "maintenance", "cleaning", "full-relocation"]
    if booking.service_type.lower() not in allowed_services:
        raise HTTPException(status_code=400, detail=f"service_type must be one of {allowed_services}")

    entry = {
        "id": len(booking_enquiries) + 1,
        "name": booking.name,
        "email": booking.email,
        "phone": booking.phone,
        "service_type": booking.service_type,
        "preferred_date": booking.preferred_date,
        "city": booking.city,
        "notes": booking.notes,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
    }
    booking_enquiries.append(entry)
    # TODO: send confirmation email & notify ops team
    return {
        "success": True,
        "booking_id": entry["id"],
        "message": f"Booking enquiry received! Your reference ID is #SHS{entry['id']:04d}. We'll confirm within 2 hours.",
    }


# ── Admin / Debug (remove in production) ──────────────────────────────────────

@app.get("/admin/contacts")
def list_contacts():
    return {"count": len(contact_submissions), "data": contact_submissions}

@app.get("/admin/bookings")
def list_bookings():
    return {"count": len(booking_enquiries), "data": booking_enquiries}

@app.get("/admin/subscribers")
def list_subscribers():
    return {"count": len(newsletter_subscribers), "data": newsletter_subscribers}

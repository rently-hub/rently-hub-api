from typing import Any, Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

from app.api import deps
from app.models.user import User
from app.models.property import Property
from app.models.rental import Rental
from app.models.expense import Expense

from app import schemas

router = APIRouter()

@router.get("/summary", response_model=schemas.DashboardSummary)
def get_dashboard_summary(

    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    property_id: Optional[int] = Query(None)
) -> Any:
    """
    Get expanded dashboard analytics with optional property filtering.
    """
    # Get user's property IDs for filtering
    if property_id:
        user_props = db.query(Property.id).filter(Property.id == property_id, Property.owner_id == current_user.id).all()
    else:
        user_props = db.query(Property.id).filter(Property.owner_id == current_user.id).all()
    
    prop_ids = [p[0] for p in user_props]

    if not prop_ids:
        return {
            "total_revenue": 0.0, "total_expenses": 0.0, "net_profit": 0.0,
            "upcoming_checkins": 0, "occupancy_rate": 0.0, "adr": 0.0,
            "chart_data": []
        }

    # 1. Total Revenue
    revenue = db.query(func.sum(Rental.total_price)).filter(
        Rental.property_id.in_(prop_ids),
        Rental.status.in_(["active", "completed"])
    ).scalar() or 0.0

    # 2. Total Expenses
    expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.property_id.in_(prop_ids)
    ).scalar() or 0.0

    # 3. Upcoming Check-ins
    upcoming_checkins = db.query(func.count(Rental.id)).filter(
        Rental.property_id.in_(prop_ids),
        Rental.start_date >= date.today(),
        Rental.status == "active"
    ).scalar() or 0

    # 4. Occupancy Rate (Last 30 days)
    thirty_days_ago = date.today() - timedelta(days=30)
    rented_days = db.query(func.sum(
        func.datediff(
            func.least(Rental.end_date, date.today()),
            func.greatest(Rental.start_date, thirty_days_ago)
        ) + 1
    )).filter(
        Rental.property_id.in_(prop_ids),
        Rental.status == "active",
        Rental.end_date >= thirty_days_ago,
        Rental.start_date <= date.today()
    ).scalar() or 0
    
    rented_days_f = float(rented_days)
    occupancy_rate = (rented_days_f / 30) * 100 if rented_days_f else 0

    # 5. Average Daily Rate (ADR)
    total_rented_days = db.query(func.sum(func.datediff(Rental.end_date, Rental.start_date) + 1)).filter(
        Rental.property_id.in_(prop_ids),
        Rental.status.in_(["active", "completed"])
    ).scalar() or 0
    
    revenue_f = float(revenue)
    total_rented_days_f = float(total_rented_days)
    adr = revenue_f / total_rented_days_f if total_rented_days_f > 0 else 0

    # 6. Monthly Breakdown (Last 6 months)
    chart_data = []
    today_first = date.today().replace(day=1)

    for i in range(5, -1, -1):
        start_of_month = today_first - relativedelta(months=i)
        next_month = start_of_month + relativedelta(months=1)
        month_name = start_of_month.strftime("%b")

        month_rev = db.query(func.sum(Rental.total_price)).filter(
            Rental.property_id.in_(prop_ids),
            Rental.status.in_(["active", "completed"]),
            Rental.start_date >= start_of_month,
            Rental.start_date < next_month
        ).scalar() or 0.0

        month_exp = db.query(func.sum(Expense.amount)).filter(
            Expense.property_id.in_(prop_ids),
            Expense.pay_date >= start_of_month,
            Expense.pay_date < next_month
        ).scalar() or 0.0

        chart_data.append({
            "name": month_name,
            "receita": float(month_rev),
            "despesa": float(month_exp)
        })

    return {
        "total_revenue": float(revenue),
        "total_expenses": float(expenses),
        "net_profit": float(revenue - expenses),
        "upcoming_checkins": int(upcoming_checkins),
        "occupancy_rate": round(float(occupancy_rate), 1),
        "adr": round(float(adr), 2),
        "chart_data": chart_data
    }


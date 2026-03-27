from typing import List
from pydantic import BaseModel

class ChartData(BaseModel):
    name: str
    receita: float
    despesa: float

class DashboardSummary(BaseModel):
    total_revenue: float
    total_expenses: float
    net_profit: float
    upcoming_checkins: int
    occupancy_rate: float
    adr: float
    chart_data: List[ChartData]

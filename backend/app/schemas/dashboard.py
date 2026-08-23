from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
import uuid


class KPICard(BaseModel):
    label: str
    value: Any
    change: Optional[float] = None
    change_label: Optional[str] = None
    icon: Optional[str] = None


class ChartData(BaseModel):
    type: str
    title: str
    data: List[dict]


class NationalDashboardResponse(BaseModel):
    kpis: List[KPICard]
    charts: List[ChartData]
    state_progress: List[dict]


class StateDashboardResponse(BaseModel):
    kpis: List[KPICard]
    charts: List[ChartData]
    district_progress: List[dict]


class DistrictDashboardResponse(BaseModel):
    kpis: List[KPICard]
    charts: List[ChartData]
    recent_projects: List[dict]

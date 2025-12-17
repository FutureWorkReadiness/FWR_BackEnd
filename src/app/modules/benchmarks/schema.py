"""
Peer Benchmarking schemas.
Pydantic models for peer comparison data.
"""

from pydantic import BaseModel
from typing import List


class PeerComparison(BaseModel):
    """Comparison of user score vs peer average."""

    category: str
    your_score: float
    peer_average: float
    difference: float
    percentile: int  # e.g., 75 means "better than 75% of peers"
    status: str  # "above", "average", "below"


class CommonInsight(BaseModel):
    """Common strength or gap insight."""

    area: str
    percentage: float
    description: str


class PeerBenchmarkData(BaseModel):
    """Complete peer benchmark data."""

    specialization_name: str
    total_peers: int
    comparisons: List[PeerComparison]
    overall_percentile: int
    common_strengths: List[CommonInsight]
    common_gaps: List[CommonInsight]
    last_updated: str


class PeerBenchmarkResponse(BaseModel):
    """Response schema for peer benchmark endpoint."""

    success: bool
    data: PeerBenchmarkData


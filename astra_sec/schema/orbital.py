"""ASTRA-Sec: Real Orbital Data and Astrodynamics Schema (Pydantic v2).

Enforces strict typing and validation for space network nodes, TLE ephemerides,
SGP4 orbital states, coordinate transformations, and ground station visibility.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SatelliteClassification(str, Enum):
    SIMULATED_TESTBED_NODE = "SIMULATED_TESTBED_NODE"
    REAL_REFERENCE_ORBIT = "REAL_REFERENCE_ORBIT"


class OrbitType(str, Enum):
    POLAR_SSO = "Polar Sun-Synchronous LEO"
    INCLINED_LEO = "Inclined LEO Relay Constellation"
    LEO_STATION = "Low Earth Orbit (LEO)"
    POLAR_LEO = "Sun-Synchronous Polar LEO"
    ISL_CONSTELLATION = "Polar LEO Crosslink Constellation"


class SatelliteOrbitalRecord(BaseModel):
    id: str = Field(description="Unique satellite identifier (e.g., 'sat1', 'iss')")
    norad_cat_id: int = Field(description="NORAD Satellite Catalog number")
    name: str = Field(description="Satellite or spacecraft name")
    intl_designator: str = Field(description="COSPAR International Designator")
    classification: SatelliteClassification = Field(description="Distinction between real space object vs testbed node")
    operational_status: str = Field(description="Flight role or operational status")
    eid: Optional[str] = Field(default=None, description="DTN Endpoint Identifier if part of ASTRA-Sec testbed")
    orbit_type: str = Field(description="Orbital regime description")
    nominal_altitude_km: float = Field(ge=100.0, le=40000.0, description="Nominal orbital altitude in kilometers")
    inclination_deg: float = Field(ge=0.0, le=180.0, description="Orbital plane inclination in degrees")
    period_minutes: float = Field(ge=50.0, le=1500.0, description="Orbital period in minutes")
    color: str = Field(description="Hex color code for 3D visualization")
    line1: str = Field(description="Two-Line Element Set Line 1 (69 chars)")
    line2: str = Field(description="Two-Line Element Set Line 2 (69 chars)")
    role: str = Field(description="Role within ASTRA-Sec or experimental verification role")
    bus_type: str = Field(description="3D spacecraft model configuration description")


class GroundStationRecord(BaseModel):
    id: str = Field(description="Ground station identifier (e.g. 'gsa', 'gsb')")
    name: str = Field(description="Ground station formal designation")
    location: str = Field(description="Geographic location and facility name")
    lat: float = Field(ge=-90.0, le=90.0, description="Geodetic latitude in degrees")
    lng: float = Field(ge=-180.0, le=180.0, description="Geodetic longitude in degrees")
    altitude_km: float = Field(ge=-0.5, le=10.0, description="Elevation above mean sea level in kilometers")
    eid: str = Field(description="DTN Endpoint Identifier (e.g., 'dtn://gsa/app')")
    antenna_type: str = Field(description="Terminal and antenna specification")
    role: str = Field(description="Cryptographic and DTN role in ASTRA-Sec")


class PropagatedSatelliteState(BaseModel):
    id: str
    norad_cat_id: int
    name: str
    classification: SatelliteClassification
    eid: Optional[str] = None
    timestamp_utc: str
    lat: float = Field(ge=-90.0, le=90.0)
    lng: float = Field(ge=-180.0, le=180.0)
    altitude_km: float = Field(ge=100.0)
    velocity_kms: float = Field(ge=5.0, le=12.0)
    orbital_period_min: float
    inclination_deg: float
    sub_satellite_point: str
    in_sunlight: bool = True
    ground_track_elevation_gsa_deg: Optional[float] = None
    ground_track_elevation_gsb_deg: Optional[float] = None
    active_isl_range_km: Optional[float] = None


class OrbitalCatalogPayload(BaseModel):
    source: str
    generated_at: str
    data_freshness_status: str = Field(description="'LIVE_PUBLIC_EPHEMERIS' or 'CACHED_OFFLINE'")
    sgp4_model: str
    air_gapped_fallback: bool
    satellites: List[SatelliteOrbitalRecord]
    ground_stations: List[GroundStationRecord]


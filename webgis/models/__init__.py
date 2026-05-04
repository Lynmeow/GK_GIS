from .user_profile import UserProfile
from .monitoring_station import MonitoringStation
from .air_quality import AirQualityData
from .uhi_data import UHIData
from .water_quality import WaterQualityData
from .green_space import GreenSpaceData
from .soil_quality import SoilQualityData
from .noise import NoiseData
from .waste import WasteData
from .flood import FloodData
from .traffic import TrafficData
from .alert import Alert
from .feedback import Feedback
from .proposal import Proposal
from .site_config import SiteConfig
from .research_application import ResearchApplication

from auditlog.registry import auditlog

auditlog.register(MonitoringStation)
auditlog.register(Alert)
auditlog.register(AirQualityData)
auditlog.register(WaterQualityData)
auditlog.register(UHIData)
auditlog.register(GreenSpaceData)
auditlog.register(SoilQualityData)
auditlog.register(NoiseData)
auditlog.register(WasteData)
auditlog.register(FloodData)
auditlog.register(TrafficData)
auditlog.register(Feedback)
auditlog.register(Proposal)
auditlog.register(UserProfile)
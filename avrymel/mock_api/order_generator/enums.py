from enum import Enum


class TrackingCompany(Enum):
    UPS = "UPS"
    DPD = "DPD"
    FEDEX = "FEDEX"
    USPS = "USPS"


class OrderFinancialStatus(Enum):
    COMPLETED = "paid"
    PENDING = "pending"
    REFUNDED = "refunded"

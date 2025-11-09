import datetime


class Config:
    """Configuration for order generation."""

    SAME_BILLING_AS_SHIPPING_PROB = 0.8
    FINANCIAL_STATUS_PROBABILITIES = [0.8, 0.16, 0.04]
    DISCOUNT_PROBABILITY = 0.1
    TAX_RATE = 0.08
    MIN_ITEMS = 1
    MAX_ITEMS = 5
    MIN_QUANTITY = 1
    MAX_QUANTITY = 5
    COMPANY_PROBABILITY = 0.3
    DATE_RANGE_START = datetime.datetime(2023, 1, 1)
    DATE_RANGE_END = datetime.datetime.now()
    UPDATE_DATE_DELTA_WEEKS = 2
    TRACKING_NUMBER_LENGTH = 18

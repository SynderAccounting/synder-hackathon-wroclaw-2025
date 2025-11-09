import datetime
import random
import string
from typing import Optional

from faker import Faker

from .config import Config
from .constants import COUNTRY_CODES, DISCOUNTS, ITEM_VARIANTS, ITEMS
from .enums import OrderFinancialStatus, TrackingCompany
from .models import (
    Address,
    Customer,
    Discount,
    OrderData,
    OrderFulfillment,
    OrderItem,
)


class OrderGenerator:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.fake = Faker()

    def generate_order_data(self) -> OrderData:
        """Generate random order data.

        Returns:
            OrderData object with all order information.
        """
        created_at = self._generate_date(
            self.config.DATE_RANGE_START, self.config.DATE_RANGE_END
        )
        updated_at = self._generate_date(
            created_at,
            created_at + datetime.timedelta(weeks=self.config.UPDATE_DATE_DELTA_WEEKS),
        )

        order_items = self._generate_order_items(
            random.randint(self.config.MIN_ITEMS, self.config.MAX_ITEMS)
        )
        subtotal = self._calculate_subtotal(order_items)

        discount = self._select_discount()
        discount_amount = self._calculate_discount_amount(subtotal, discount)
        total_tax = self._calculate_tax(subtotal, discount_amount)
        final_price = subtotal - discount_amount + total_tax

        shipping_address = self._generate_address()
        billing_address = (
            shipping_address
            if random.random() < self.config.SAME_BILLING_AS_SHIPPING_PROB
            else self._generate_address()
        )

        return OrderData(
            order_id=self._generate_order_id(),
            created_at=created_at,
            updated_at=updated_at,
            currency=self._select_currency(),
            financial_status=self._select_financial_status(),
            subtotal=subtotal,
            discount=discount,
            total_tax=total_tax,
            final_price=final_price,
            billing_address=billing_address,
            shipping_address=shipping_address,
            items=order_items,
            fulfillment=self._generate_fulfillment(created_at, updated_at),
            customer=Customer(
                email=self.fake.email(),
                first_name=shipping_address.first_name,
                last_name=shipping_address.last_name,
            ),
        )

    # ========================================================================
    # GENERATION HELPERS
    # ========================================================================

    def _generate_order_id(self) -> str:
        return str(random.randint(100000000, 999999999))

    def _select_currency(self) -> str:
        return random.choice(["USD", "PLN", "EUR", "GBP", "CAD"])

    def _select_financial_status(self) -> OrderFinancialStatus:
        rand = random.random()
        if rand < self.config.FINANCIAL_STATUS_PROBABILITIES[0]:
            return OrderFinancialStatus.COMPLETED
        elif rand < sum(self.config.FINANCIAL_STATUS_PROBABILITIES[:2]):
            return OrderFinancialStatus.PENDING
        return OrderFinancialStatus.REFUNDED

    def _generate_address(self) -> Address:
        country = random.choice(list(COUNTRY_CODES.keys()))
        return Address(
            first_name=self.fake.first_name(),
            last_name=self.fake.last_name(),
            company=self.fake.company()
            if random.random() < self.config.COMPANY_PROBABILITY
            else "",
            address=self.fake.street_address(),
            city=self.fake.city(),
            state_or_region=self.fake.state_abbr(),
            country=country,
            postal_code=self.fake.postcode(),
            country_code=COUNTRY_CODES.get(country, "US"),
        )

    def _generate_date(
        self, start: datetime.datetime, end: datetime.datetime
    ) -> datetime.datetime:
        random_date = self.fake.date_between(
            start_date=start.date(), end_date=end.date()
        )
        random_time = self.fake.time_object()
        return datetime.datetime.combine(random_date, random_time)

    def _generate_order_item(self) -> OrderItem:
        item = random.choice(ITEMS)
        return OrderItem(
            item=item,
            variant_name=random.choice(ITEM_VARIANTS),
            quantity=random.randint(self.config.MIN_QUANTITY, self.config.MAX_QUANTITY),
        )

    def _generate_order_items(self, count: int) -> list[OrderItem]:
        return [self._generate_order_item() for _ in range(count)]

    def _generate_fulfillment(
        self, start: datetime.datetime, end: datetime.datetime
    ) -> OrderFulfillment:
        return OrderFulfillment(
            tracking_company=random.choice(list(TrackingCompany)),
            created_at=self._generate_date(start, end),
            tracking_number="".join(
                random.choices(
                    string.ascii_uppercase + string.digits,
                    k=self.config.TRACKING_NUMBER_LENGTH,
                )
            ),
        )

    def _select_discount(self) -> Optional[Discount]:
        return (
            random.choice(DISCOUNTS)
            if random.random() < self.config.DISCOUNT_PROBABILITY
            else None
        )

    # ========================================================================
    # CALCULATION HELPERS
    # ========================================================================

    def _calculate_subtotal(self, items: list[OrderItem]) -> float:
        return sum(item.quantity * item.item.item_price for item in items)

    def _calculate_discount_amount(
        self, subtotal: float, discount: Optional[Discount]
    ) -> float:
        if not discount:
            return 0.0
        return round((subtotal * discount.discount_percent) / 100, 2)

    def _calculate_tax(self, subtotal: float, discount_amount: float) -> float:
        return (subtotal - discount_amount) * self.config.TAX_RATE

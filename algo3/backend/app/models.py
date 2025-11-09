"""
Standardowa struktura danych dla produktów.
Używamy tej struktury wszędzie - bez wyjątków.
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class ProductStatus(str, Enum):
    """Status produktu"""
    ACTIVE = "active"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    INACTIVE = "inactive"


class Channel(str, Enum):
    """Kanał sprzedaży - tylko te dwa"""
    WOOCOMMERCE = "woocommerce"
    SHOPIFY = "shopify"


class PromotionType(str, Enum):
    """Typ promocji"""
    PRICE = "price"
    BUNDLE = "bundle"
    PROMO = "promo"


# ========== GŁÓWNA STRUKTURA PRODUKTU ==========

class ActivePromotion(BaseModel):
    """Aktywna promocja"""
    id: int
    type: str  # price, bundle, promo
    description: str

    class Config:
        use_enum_values = True


class ProductRecord(BaseModel):
    """
    TO JEST GŁÓWNA STRUKTURA KTÓRĄ UŻYWAMY WSZĘDZIE.
    Każdy produkt ZAWSZE ma te pola w tej kolejności.
    """
    # To co wyświetlamy w tabeli:
    sku: str = Field(..., description="Kod produktu")
    name: str = Field(..., description="Nazwa produktu")
    price: float = Field(..., description="Cena")
    stock: int = Field(..., description="Nakład/ilość")
    status: str = Field(..., description="Status (active, low_stock, out_of_stock, inactive)")
    channel: str = Field(..., description="Kanał (shopify lub woocommerce)")
    active_promotion: Optional[str] = Field(None, description="Opis aktywnej promocji lub None")

    # Dodatkowe pola (nie wyświetlamy domyślnie):
    id: Optional[int] = None
    active_promotions: List[ActivePromotion] = Field(default_factory=list)
    created_at: Optional[str] = None
    vendor: Optional[str] = None
    product_type: Optional[str] = None

    class Config:
        use_enum_values = True


# ========== FUNKCJE TRANSFORMACJI ==========

def db_row_to_product(row: dict, promotions: List[dict] = None) -> ProductRecord:
    """
    Konwertuje wiersz z bazy danych na ProductRecord.
    ZAWSZE używaj tej funkcji do konwersji z DB.
    """
    promo_list = []
    if promotions:
        promo_list = [
            ActivePromotion(
                id=p['id'],
                type=p['type'],
                description=p['description']
            )
            for p in promotions
        ]

    # Wybierz jedną promocję do wyświetlenia (pierwszą lub najważniejszą)
    active_promotion_text = None
    if promo_list:
        if len(promo_list) == 1:
            active_promotion_text = promo_list[0].description
        else:
            active_promotion_text = f"{len(promo_list)} aktywne promocje"

    return ProductRecord(
        id=row['id'],
        sku=row['sku'],
        name=row['name'],
        price=round(float(row['price']), 2),
        stock=int(row.get('stock', 0)),
        status=row['status'],
        channel=row['channel'],
        active_promotion=active_promotion_text,
        active_promotions=promo_list,
        created_at=row.get('created_at'),
        vendor=row.get('vendor'),
        product_type=row.get('product_type')
    )


def shopify_to_our_format(shopify_product: dict) -> dict:
    """
    Przekształca produkt z Shopify na naszą strukturę.
    Zwraca dict który można wrzucić do bazy.
    """
    # Shopify może mieć variants - bierzemy pierwszy
    variant = shopify_product.get('variants', [{}])[0] if shopify_product.get('variants') else {}

    price = float(variant.get('price', 0))
    stock = int(variant.get('inventory_quantity', 0))

    # Określ status na podstawie stock
    if stock == 0:
        status = ProductStatus.OUT_OF_STOCK.value
    elif stock < 10:
        status = ProductStatus.LOW_STOCK.value
    else:
        status = ProductStatus.ACTIVE.value

    return {
        'sku': variant.get('sku', f"SHOPIFY-{shopify_product.get('id', 'UNKNOWN')}"),
        'name': shopify_product.get('title', 'Unknown Product'),
        'price': price,
        'stock': stock,
        'status': status,
        'channel': Channel.SHOPIFY.value,
        'external_id': str(shopify_product.get('id', ''))
    }


def woocommerce_to_our_format(woo_product: dict) -> dict:
    """
    Przekształca produkt z WooCommerce na naszą strukturę.
    Zwraca dict który można wrzucić do bazy.
    """
    price = float(woo_product.get('price', 0))
    stock = int(woo_product.get('stock_quantity', 0))

    # Określ status
    stock_status = woo_product.get('stock_status', 'instock')
    if stock_status == 'outofstock' or stock == 0:
        status = ProductStatus.OUT_OF_STOCK.value
    elif stock < 10:
        status = ProductStatus.LOW_STOCK.value
    else:
        status = ProductStatus.ACTIVE.value

    return {
        'sku': woo_product.get('sku', f"WOO-{woo_product.get('id', 'UNKNOWN')}"),
        'name': woo_product.get('name', 'Unknown Product'),
        'price': price,
        'stock': stock,
        'status': status,
        'channel': Channel.WOOCOMMERCE.value,
        'external_id': str(woo_product.get('id', ''))
    }


def transform_external_product(product_data: dict, channel: str) -> dict:
    """
    Uniwersalna funkcja do przekształcania produktów z zewnętrznych platform.

    Args:
        product_data: Surowe dane produktu z platformy
        channel: 'shopify' lub 'woocommerce'

    Returns:
        Dict gotowy do wrzucenia do bazy
    """
    channel_lower = channel.lower()

    if channel_lower == 'shopify':
        return shopify_to_our_format(product_data)
    elif channel_lower == 'woocommerce':
        return woocommerce_to_our_format(product_data)
    else:
        raise ValueError(f"Unsupported channel: {channel}")

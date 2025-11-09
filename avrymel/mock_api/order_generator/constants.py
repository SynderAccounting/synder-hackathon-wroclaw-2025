from .models import Discount, Item


ITEMS = [
    Item("SKU001", "T-Shirt Classic", 19.99),
    Item("SKU002", "T-Shirt Premium", 29.99),
    Item("SKU003", "T-Shirt Vintage", 24.99),
    Item("SKU004", "T-Shirt V-Neck", 22.99),
    Item("SKU005", "Hoodie Premium", 49.99),
    Item("SKU006", "Hoodie Winter", 59.99),
    Item("SKU007", "Hoodie Zip-Up", 54.99),
    Item("SKU008", "iPod Shuffle", 79.99),
    Item("SKU009", "iPod Nano", 99.99),
    Item("SKU010", "iPod Touch", 149.99),
    Item("SKU011", "Baseball Cap", 24.99),
    Item("SKU012", "Baseball Cap Vintage", 29.99),
    Item("SKU013", "Snapback Cap", 27.99),
    Item("SKU014", "Beanie", 19.99),
    Item("SKU015", "Backpack Travel", 89.99),
    Item("SKU016", "Backpack School", 64.99),
    Item("SKU017", "Backpack Laptop", 99.99),
    Item("SKU018", "Socks Pack 3", 12.99),
    Item("SKU019", "Socks Pack 6", 22.99),
    Item("SKU020", "Socks Pack 12", 39.99),
]

ITEM_VARIANTS = [
    "Black",
    "White",
    "Gray",
    "Navy",
    "Red",
    "Blue",
    "Green",
    "Pink",
    "Purple",
    "Yellow",
]

DISCOUNTS = [
    Discount(10, "WELCOME10"),
    Discount(10, "HELLO10"),
    Discount(5, "FREE5"),
    Discount(15, "SUMMER15"),
]

COUNTRY_CODES = {
    "United States": "US",
    "Canada": "CA",
    "United Kingdom": "GB",
    "Germany": "DE",
    "France": "FR",
    "Poland": "PL",
    "Spain": "ES",
    "Italy": "IT",
    "Australia": "AU",
    "Japan": "JP",
}

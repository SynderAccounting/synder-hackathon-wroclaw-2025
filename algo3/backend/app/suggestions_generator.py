import random
import logging

logger = logging.getLogger(__name__)

SUGGESTION_TEMPLATES = {
    'price': [
        'Obniż cenę o {percent}% - konkurencja oferuje podobny produkt taniej',
        'Podwyższ cenę do {new_price} PLN - high demand, niska dostępność u konkurencji',
        'Test A/B: sprawdź {new_price} PLN vs obecna cena',
        'Promocyjna cena {new_price} PLN dla lojalnych klientów',
        'Sezonowa korekta ceny: {new_price} PLN',
    ],
    'promo': [
        'Black Friday: {percent}% rabatu na pierwsze {quantity} sztuk',
        'Promocja "{campaign_name}" - kup {buy_qty}, zapłać za {pay_qty}',
        'Darmowa wysyłka przy zakupie {min_qty} sztuk',
        'Letnia wyprzedaż: -{percent}%',
        'Back to School: -{percent}% dla studentów',
        'Flashsale: {percent}% rabatu przez 24h',
    ],
    'bundle': [
        'Bundle z {other_product} z {percent}% rabatem',
        '{season} Bundle: ten produkt + akcesoria za {bundle_price} PLN',
        'Stwórz pakiet startowy z rabaterri {percent}%',
        'Cross-sell: zaoferuj bundle z produktami komplementarnymi',
    ]
}

def generate_suggestions_for_product(product_id, product_name, product_price):
    """Generate 2-4 suggestions for a product"""
    suggestions = []
    num_suggestions = random.randint(2, 4)

    # Randomly select suggestion types
    suggestion_types = random.sample(['price', 'promo', 'bundle'], k=min(num_suggestions, 3))
    if num_suggestions == 4:
        # Add one more type
        suggestion_types.append(random.choice(['price', 'promo']))

    for sug_type in suggestion_types:
        template = random.choice(SUGGESTION_TEMPLATES[sug_type])

        # Fill in template variables
        description = template.format(
            percent=random.choice([10, 15, 20, 25, 30]),
            new_price=round(product_price * random.uniform(0.85, 1.15), 2),
            quantity=random.choice([20, 30, 50, 100]),
            buy_qty=random.choice([2, 3]),
            pay_qty=random.choice([1, 2]),
            min_qty=random.choice([2, 3]),
            campaign_name=random.choice(['Fitness Challenge', 'Summer Vibes', 'Tech Week', 'Green Friday']),
            other_product=random.choice(['słuchawkami', 'powerbankiem', 'kablem', 'etui']),
            season=random.choice(['Summer', 'Winter', 'Spring', 'Gaming']),
            bundle_price=round(product_price * 1.5, 2)
        )

        # Random status - some already applied for demo
        status = random.choice(['new', 'new', 'new', 'applied'])

        suggestions.append({
            'product_id': product_id,
            'type': sug_type,
            'description': description,
            'status': status
        })

    logger.info(f"Generated {len(suggestions)} suggestions for product {product_id}")
    return suggestions

"""Entry point for running the order generator as a module."""

from .generator import OrderGenerator

# ============================================================================
# USAGE
# ============================================================================

if __name__ == "__main__":
    # Use default config
    generator = OrderGenerator()
    order = generator.generate_order()
    print(order.to_json())

    # Or create custom config
    # custom_config = Config()
    # custom_config.TAX_RATE = 0.10
    # generator = OrderGenerator(custom_config)
    # order = generator.generate_order()
    # print(order.to_json())

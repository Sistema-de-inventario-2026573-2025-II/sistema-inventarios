# sistema-inventarios/backend/app/core/exceptions.py
class InsufficientStockError(Exception):
    """Excepcion para cuando el stock es insuficiente."""
    def __init__(self, item_sku: str, requested: int, available: int):
        self.item_sku = item_sku
        self.requested = requested
        self.available = available
        self.message = (
            f"Stock insuficiente para {item_sku}. "
            f"Solicitado: {requested}, Disponible: {available}"
        )
        super().__init__(self.message)
def validate_sku(sku: str) -> bool:
    return bool(sku and isinstance(sku, str))

def validate_barcode(barcode: str) -> bool:
    return bool(barcode and isinstance(barcode, str))

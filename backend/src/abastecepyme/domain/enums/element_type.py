from enum import Enum

class ElementType(str, Enum):
    PROVEEDOR = "proveedor"
    INSUMO = "insumo"
    PRODUCTO = "producto"

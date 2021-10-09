from service.control_srv import ControlStock


def test_product_exist():
    c = ControlStock()
    valor = c.is_product_available("Chocolate",1)
    assert valor == True

def test_product_dont_exist():
    c = ControlStock()
    valor = c.is_product_available("Frutilla",222)
    assert valor == False

def test_product_dont_exist_stock():
    c = ControlStock()
    valor = c.is_product_available("Chocolate",100)
    assert valor == False
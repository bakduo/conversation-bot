from service.control_srv import ControlCode

def test_validate_code_1():
    c = ControlCode()
    valor = c.validate_discount_code("Primavera2022")
    assert valor == False

def test_validate_code_2():
    c = ControlCode()
    valor = c.validate_discount_code("PrimaverA2021")
    assert valor == True

def test_validate_code_3():
    c = ControlCode()
    valor = c.validate_discount_code("primaverA2021")
    assert valor == False

def test_validate_code_4():
    c = ControlCode()
    valor = c.validate_discount_code("HeladoFrozen")
    assert valor == True

def test_validate_code_5():
    c = ControlCode()
    valor = c.validate_discount_code("heladOFrozen")
    assert valor == True

def test_validate_code_6():
    c = ControlCode()
    valor = c.validate_discount_code("h3lAdOFrozen")
    assert valor == False

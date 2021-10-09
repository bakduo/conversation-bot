from service.control_srv import GeoAPI

def test_temp():
    valor = GeoAPI.is_hot_in_pehuajo()
    assert (valor == False)

import pytest
from runinlyon.city import get_lat_lon, get_woeid


def test_get_lat_lon():
    address = "20 rue des capucins Lyon"
    answer = get_lat_lon(address)
    assert len(answer) == 2
    assert answer[0] == pytest.approx(45.769458,1.E-6)
    assert answer[1] == pytest.approx(4.834862,1.E-6)

def test_get_woeid_london():
    lat = 51.5073509
    lon = -0.1277583
    assert get_woeid(lat,lon)['woeid'] == 44418

def test_get_woeid_lyon():
    lat = 45.769458
    lon = 4.834862
    assert get_woeid(lat,lon)['woeid'] == 609125

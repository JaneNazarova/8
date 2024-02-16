import requests


def get_request(server, params):
    try:
        response = requests.get(server, params)
        response.raise_for_status()  # Вызывает исключение, если запрос неуспешен
        return response
    except requests.RequestException as exc:
        raise exc  # Пробрасывает исключение дальше для обработки вызывающим кодом


def geocoder_request(apikey, geocode, format='json'):
    API_SERVER = 'https://geocode-maps.yandex.ru/1.x/'
    params = {
        'apikey': apikey,
        'geocode': geocode,
        'format': format,
    }

    response = get_request(API_SERVER, params)
    json_data = response.json()

    # Проверка на наличие ключей и индексов в структуре JSON
    if "response" in json_data and "GeoObjectCollection" in json_data["response"]:
        feature_member = json_data["response"]["GeoObjectCollection"].get("featureMember", [])
        if feature_member:
            geo_object = feature_member[0].get("GeoObject", None)
            return geo_object
    return None


def static_maps_request(*, center_point, org_point, scale, map_type):
    API_SERVER = 'https://static-maps.yandex.ru/1.x/'
    params = {
        'll': center_point,
        'z': scale,
        'l': map_type,
        "pt": "{0},pm2dgl".format(org_point)
    }

    # Проверка наличия ключей и значений в параметрах запроса
    if not all(params.values()):
        return None

    response = get_request(API_SERVER, params)

    # Проверка наличия ответа от сервера
    if response and response.status_code == 200:
        return response.content

    return None


def generate_image(*, center_point, org_point, scale, map_type):
    img_content = static_maps_request(
        center_point=center_point,
        org_point=org_point,
        map_type=map_type,
        scale=scale
    )
    with open('map.png', 'wb') as file:
        file.write(img_content)


def geosearch_request(*, apikey, text, lang: str = 'ru_RU', type_: str = 'biz'):
    API_SERVER = "https://search-maps.yandex.ru/v1/"
    map_params = {
        'apikey': apikey,
        'text': text,
        'lang': lang,
        'type': type_,
    }

    if not all(map_params.values()):
        return None

    response = get_request(API_SERVER, params=map_params)

    if response and response.status_code == 200:
        return response.json()

    return None


class Geosearch:
    def __init__(self):
        self.apikey = 'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3'

    def geosearch_request(self, *, address):
        return geosearch_request(
            apikey=self.apikey,
            text=address,
        )

    def get_ll_by_address(self, *, address):
        geosearch_json = self.geosearch_request(address=address)
        organization = geosearch_json["features"][0]
        point = organization["geometry"]["coordinates"]
        return "{},{}".format(point[0], point[1])

    def get_full_address(self, *, address):
        geosearch_json = self.geosearch_request(address=address)
        organization = geosearch_json["features"][0]
        return organization["properties"]['description']


geosearch_controller = Geosearch()

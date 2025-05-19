import json
import leafmap
import leafmap.foliumap as leafmap
import requests

def create_interactive_map():
    # Создаем интерактивную карту
    m = leafmap.Map(center=[20, 0], zoom=2)

    # Добавляем базовую карту
    m.add_basemap('OpenStreetMap')

    # Получаем данные о странах из REST Countries API
    countries_data_url = "https://restcountries.com/v3.1/all"
    response = requests.get(countries_data_url)
    countries_data = response.json()

    # Фильтруем страны по нужным названиям и собираем координаты и население
    filtered_countries = ['Russia', 'United Kingdom', 'Japan']  # Убедитесь, что названия совпадают
    country_info = {}

    for country in countries_data:
        if country['name']['common'] in filtered_countries:
            country_info[country['name']['common']] = {
                'location': country['latlng'],
                'population': country['population'],
                'capital': country['capital'][0] if 'capital' in country else None,
                'capital_coords': country['capitalInfo']['latlng'] if 'capitalInfo' in country else None
            }

    # Получаем границы стран
    countries_geojson_url = "https://datahub.io/core/geo-countries/r/countries.geojson"
    response = requests.get(countries_geojson_url)
    countries_geojson = response.json()

    # Проверяем доступные названия стран в GeoJSON
    available_countries = {feature['properties']['name'] for feature in countries_geojson['features']}
    print("Доступные страны:", available_countries)

    # Фильтруем страны по названию
    filtered_features = []
    for feature in countries_geojson['features']:
        properties = feature.get('properties', {})
        country_name = properties.get('name', None)
        if country_name in filtered_countries:
            filtered_features.append(feature)

    # Если нет отфильтрованных стран, выводим сообщение
    if not filtered_features:
        print("Нет отфильтрованных стран для отображения.")
    else:
        # Добавляем границы стран на карту
        m.add_geojson(
            {
                'type': 'FeatureCollection',
                'features': filtered_features
            },
            layer_name='Границы стран',
            style_function=lambda feature: {
                'fillColor': '#ffffff00',  # прозрачная заливка
                'color': '#FF5733',        # оранжевый цвет границ
                'weight': 1,
                'fillOpacity': 0
            }
        )

    # Добавляем точки стран на карту с popup информацией
    for country, info in country_info.items():
        popup_text = f"{country}<br>Население: {info['population']:,}"
        m.add_marker(location=info['location'], popup=popup_text, tooltip=country)

        # Убираем население у столицы
        if info['capital'] and info['capital_coords']:
            capital_popup_text = f"{info['capital']} (столица {country})"
            m.add_marker(location=info['capital_coords'], popup=capital_popup_text, tooltip=info['capital'], color='red')

    # Сохраняем карту в HTML файл
    m.save('interactive_map_with_borders_and_capitals.html')

if __name__ == "__main__":
    create_interactive_map()

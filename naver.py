import os
import requests
import urllib.parse
from dotenv import load_dotenv
import re

import kakao

load_dotenv()

client_id = os.getenv('NAVER_CLIENT_ID')
client_secret = os.getenv('NAVER_CLIENT_SECRET')

def search_place(query):
    encoded_query = urllib.parse.quote(query)
    
    url = f"https://openapi.naver.com/v1/search/local.json?query={encoded_query}&display=10"

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data['items']
    else:
        print(f"Error Code: {response.status_code}")
        return None

def remove_html_tags(text):
    clean_text = re.sub('<.*?>', '', text)
    return clean_text

def generate_naver_map_search_url(query):
    base_url = "https://map.naver.com/p/search/"
    encoded_query = urllib.parse.quote(remove_html_tags(query))
    return f"{base_url}{encoded_query}"




def main():
    restaurants = kakao.main()

    if restaurants:
        result = []
        for restaurant in restaurants:
            address_name = restaurant['address_name']
            road_address_name = restaurant['road_address_name']

            name = restaurant['name']
            places = search_place(f'{address_name}, {name}')

            if places:
                result.append({
                    'address': f'{address_name}, {name}',
                    'name': name,
                    'distance': restaurant['distance'],
                    'naver_url': generate_naver_map_search_url(f'{address_name} {places[0]["title"]}'),
                    'kakao url': restaurant['place_url'],
                })
            else:
                print(f"'{address_name}, {name}'에 대한 네이버 검색 결과가 없습니다.")
        return result
    else:
        print("카카오 API에서 검색된 레스토랑이 없습니다.")

if __name__ == "__main__":
    main()


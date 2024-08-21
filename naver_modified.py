import os
import requests
import urllib.parse
from dotenv import load_dotenv
import re
import json
import time
import random

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

def load_restaurants_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_processed_restaurants(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_processed_restaurant(file_path, restaurant):
    processed = load_processed_restaurants(file_path)
    processed.append(restaurant)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(processed, f, ensure_ascii=False, indent=4)

def main():
    restaurants = load_restaurants_from_json('restaurant_list_1.0km.json')
    processed_file = 'processed_restaurants.json'
    processed_restaurants = load_processed_restaurants(processed_file)
    processed_names = set(r['name'] for r in processed_restaurants)

    if restaurants:
        result = []
        for index, restaurant in enumerate(restaurants, 1):
            if restaurant['name'] in processed_names:
                print(f"Skipping {restaurant['name']} as it's already processed.")
                continue

            address_name = restaurant['address_name']
            name = restaurant['name']
            
            # Add a long delay between requests
            time.sleep(random.uniform(5, 10))
            
            places = search_place(f'{address_name}, {name}')
            
            if places:
                restaurant_info = {
                    'index': index,
                    'address': f"{address_name}, {name}",
                    'name': name,
                    'distance': restaurant['distance'],
                    'naver_url': generate_naver_map_search_url(f'{address_name} {places[0]["title"]}'),
                    'kakao_url': restaurant['place_url'],
                    'address_name': address_name,
                    'road_address_name': restaurant['road_address_name'],
                    'phone': restaurant['phone'],
                    'longitude': restaurant['longitude'],
                    'latitude': restaurant['latitude']
                }
                result.append(restaurant_info)
                save_processed_restaurant(processed_file, restaurant_info)
                print(f"Processed and saved information for {name}")
            else:
                print(f"'{address_name}, {name}'에 대한 네이버 검색 결과가 없습니다.")
        
        # Save all results to a separate file
        with open('restaurant_list_1.0km_naver.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        
        return result
    else:
        print("JSON 파일에서 레스토랑 정보를 불러오지 못했습니다.")

if __name__ == "__main__":
    main()
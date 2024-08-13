import requests
from math import radians, cos, sin, sqrt, atan2
from dotenv import load_dotenv
import os

load_dotenv()
KAKAO_API_KEY = os.getenv('KAKAO_API_KEY')

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

def get_coordinates_by_keyword(keyword):
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}",
        "KA": "sdk/1.0.0 os/javascript lang/en device/pc",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    params = {"query": keyword}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"Error: API request failed with status code {response.status_code}")
        print("Response:", response.text)
        return None, None
    
    result = response.json()
    
    if 'documents' in result and len(result['documents']) > 0:
        place_info = result['documents'][0]
        x = place_info['x'] 
        y = place_info['y'] 
        return float(x), float(y)
    else:
        print("Error: 'documents' not found in response or no place found.")
        return None, None

def search_nearby_restaurants(x, y, radius=1000):
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}",
        "KA": "sdk/1.0.0 os/javascript lang/en device/pc",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    params = {
        "query": "음식점",
        "x": x,
        "y": y,
        "radius": radius,
        "size": 15  # 한 번에 최대 45개의 결과를 가져옴
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"Error: API request failed with status code {response.status_code}")
        print("Response:", response.text)
        return []
    
    result = response.json()
    
    restaurants = []
    if 'documents' in result and len(result['documents']) > 0:
        for place in result['documents']:
            place_x = float(place['x'])
            place_y = float(place['y'])
            distance = calculate_distance(y, x, place_y, place_x)
            restaurants.append({
                "name": place['place_name'],
                "address_name": place['address_name'],
                "road_address_name": place['road_address_name'],
                "phone": place['phone'],
                "place_url": place['place_url'],
                "distance": distance
            })

        restaurants = sorted(restaurants, key=lambda r: r['distance'])
        
    return restaurants

def create_restaurant_json(index, restaurant):
    restaurant_data = {
        "index": index,
        "name": restaurant['name'],
        "address_name": restaurant['address_name'],
        "road_address_name": restaurant['road_address_name'],
        "phone": restaurant['phone'],
        "place_url": restaurant['place_url'],
        "distance": round(restaurant['distance'], 2)
    }
    return restaurant_data

def main():
    address = '삼평동 670'
    x, y = get_coordinates_by_keyword(address)
    
    if x and y:
        radius_choice = input("검색할 반경을 선택하세요 (1: 1km, 2: 500m, 3,4,5,6,7): ")
        
        if radius_choice == '1':
            radius = 1000
        elif radius_choice == '2':
            radius = 500
        elif radius_choice == '3':
            radius = 300
        elif radius_choice == '4':
            radius = 100
        elif radius_choice == '5':
            radius = 50
        elif radius_choice == '6':
            radius = 30
        elif radius_choice == '7':
            radius = 10
        else:
            print("잘못된 입력입니다. 기본값인 1km 반경으로 검색합니다.")
            radius = 1000
        
        restaurants = search_nearby_restaurants(x, y, radius)
        
        if restaurants:
            return restaurants
        else:
            print(f"해당 위치에서 {radius/1000}km 이내에 음식점이 없습니다.")
    else:
        print("주소를 찾을 수 없습니다.")

if __name__ == "__main__":
    main()

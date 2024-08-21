import requests
from dotenv import load_dotenv
import os
import json
from math import radians, cos, sin, sqrt, atan2

# Load environment variables
load_dotenv()
KAKAO_API_KEY = os.getenv('KAKAO_API_KEY')

def search_restaurants(keyword):
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}",
        "KA": "sdk/1.0.0 os/javascript lang/en device/pc",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    restaurants = []
    print(f"Searching for '{keyword}'...")
    
    for page in range(1, 3):
        params = {
            "query": keyword,
            "page": page,
            "size": 15  # Maximum allowed by Kakao API
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"Error: API request failed with status code {response.status_code}")
            print("Response:", response.text)
            break
        
        result = response.json()
        documents = result.get('documents', [])
        
        if not documents:
            print(f"No more results found for '{keyword}'. Total results: {len(restaurants)}")
            break
        
        for place in documents:
            restaurants.append({
                "name": place['place_name'],
                "address_name": place['address_name'],
                "road_address_name": place['road_address_name'],
                "phone": place['phone'],
                "place_url": place['place_url'],
                "x": place['x'],  # longitude
                "y": place['y']   # latitude
            })
    
    return restaurants

def remove_duplicates(data):
    seen = set()
    unique_data = []
    
    for item in data:
        key = (item['name'], item['address_name'], item['road_address_name'], item['phone'])
        
        if key not in seen:
            seen.add(key)
            unique_data.append(item)
    
    return unique_data

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    distance = R * c
    return distance

def filter_restaurants_by_distance(restaurants, center_lat, center_lon, max_distance):
    filtered_restaurants = []
    
    for restaurant in restaurants:
        restaurant_lat = float(restaurant['y'])
        restaurant_lon = float(restaurant['x'])
        
        distance = calculate_distance(center_lat, center_lon, restaurant_lat, restaurant_lon)
        
        if distance <= max_distance:
            restaurant['distance'] = round(distance, 4)
            filtered_restaurants.append(restaurant)
    
    return filtered_restaurants

def main():
    base_location = "삼평동 670"
    cuisines = [
    "한식", "중식", "일식", "양식", "분식", "치킨", "피자", "패스트푸드",
    "카페", "디저트", "베이커리", "브런치",
    "태국식", "베트남식", "인도식", "멕시코식", "스페인식", "이탈리아식", "프랑스식",
    "퓨전음식", "해산물", "샐러드", "샌드위치", "부리또",
    "삼겹살", "곱창", "족발", "보쌈", "찜", "탕", "찌개",
    "냉면", "국수", "라면", "우동", "소바", "파스타",
    "초밥", "회", "돈까스", "덮밥", "컵밥", "도시락",
    "떡볶이", "순대", "튀김", "김밥", "주먹밥",
    "햄버거", "핫도그", "타코", "케밥",
    "스테이크", "립", "바비큐", "샤브샤브", "곱창",
    "술집", "와인바", "칵테일바", "이자카야",
    "뷔페", "푸드코트", "키친", "다이너",
    "채식", "비건", "글루텐프리", "유기농",
    "야식", "배달", "테이크아웃", "맛집",
]
    
    all_restaurants = []
    
    for cuisine in cuisines:
        keyword = f"{base_location} {cuisine}"
        restaurants = search_restaurants(keyword)
        all_restaurants.extend(restaurants)
    
    unique_restaurants = remove_duplicates(all_restaurants)
    
    print(f"\nTotal unique restaurants found: {len(unique_restaurants)}")
    
    # 삼평동 670 좌표 (위도, 경도)
    center_lat, center_lon = 37.40294806, 127.1050755

    # 1000m 이내의 음식점만 필터링
    filtered_restaurants = filter_restaurants_by_distance(unique_restaurants, center_lat, center_lon, 1.0)

    print(f"1000m 이내 음식점 수: {len(filtered_restaurants)}")

    # 거리순으로 정렬
    filtered_restaurants.sort(key=lambda x: x['distance'])

    # index 초기화 및 JSON 구조 변경
    restaurant_list = []
    for i, restaurant in enumerate(filtered_restaurants, 1):
        restaurant_data = {
            "index": i,
            "distance": restaurant['distance'],
            "name": restaurant['name'],
            "address_name": restaurant['address_name'],
            "road_address_name": restaurant['road_address_name'],
            "phone": restaurant['phone'],
            "place_url": restaurant['place_url'],
            "longitude": restaurant['longitude'],
            "latitude": restaurant['latitude']
        }
        restaurant_list.append(restaurant_data)

    # 결과를 새 JSON 파일로 저장
    with open('restaurant_list_1.0km.json', 'w', encoding='utf-8') as f:
        json.dump(restaurant_list, f, ensure_ascii=False, indent=4)

    print("1000m 이내의 음식점 정보가 'restaurant_list_1.0km' 파일에 저장되었습니다.")

if __name__ == "__main__":
    main()
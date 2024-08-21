import json
import re
import time
import pprint

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait

def create_schedule_dict(text_lines):
    days_of_week = ['월', '화', '수', '목', '금', '토', '일']
    
    schedule_dict = {}

    for line in text_lines:
        for day in days_of_week:
            if day in line:
                schedule_dict[day] = line
                break
    
    return schedule_dict

def extract_date(text):
    current_year = datetime.now().year

    parts = text.split()[0]  
    
    if parts[0].isdigit() and parts[1].isdigit(): 
        year_part = parts.split('.')[0]
        month_day_part = parts[len(year_part)+1:] 
        year = int(year_part)
        if year < 100: 
            year += 2000
    else:
        year = current_year
        month_day_part = parts

    month, day = month_day_part.split('.')[:2]
    
    month = month.zfill(2)
    day = day.zfill(2)

    date_str = f"{year}-{month}-{day}"

    return date_str

def extract_score(text):
    # 정규식 패턴을 소수점 포함 숫자에 맞게 수정
    numbers = re.findall(r'\d+\.\d{1,2}', text)
    if numbers:
        return float(numbers[0])
    else:
        return None

def modify_url(url, option):
    option_list = ['home', 'menu', 'review', 'information', 'feed']
    
    if option in option_list:
        query_string = f'?c=15.00,0,0,0,dh&placePath=/{option}&isCorrectAnswer=true'
        return url + query_string
    else:
        raise ValueError(f"Invalid option '{option}'. Choose from {option_list}.")

def time_wait(num, code):
    try:
        wait = WebDriverWait(driver, num).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, code)))
    except:
        print(code, '태그를 찾지 못하였습니다.')
        driver.quit()
    return wait

def load_merged_restaurants():
    with open('restaurant_list_1.0km_naver.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def save_result_file(result_data):
    with open('restaurant_list_final.json', 'w', encoding='utf-8') as json_file:
        json.dump(result_data, json_file, ensure_ascii=False, indent=4)
    print("데이터가 'restaurant_list_final.json' 파일로 저장되었습니다.")

def is_already_crawled(restaurant):
    return restaurant.get('finished') == 1

def crawl_restaurant(driver, restaurant):
    # 이미 크롤링한 가게인지 확인
    if is_already_crawled(restaurant):
        print(f"{restaurant['name']} (URL: {restaurant['naver_url']})는 이미 크롤링되었습니다. 스킵합니다.")
        return restaurant

    start = time.time()
    print(f"[{restaurant['name']} 크롤링 시작...]")

    try:
        # Home 크롤링
        driver.get(modify_url(restaurant['naver_url'], 'home'))
        driver.implicitly_wait(3)
        driver.switch_to.frame('entryIframe')

        # 카테고리
        restaurant['category'] = driver.find_element(By.CSS_SELECTOR, 'span.lnJFt').text

        # 리뷰 전체 개수
        review_num = 0
        review_num_list = driver.find_elements(By.CSS_SELECTOR, 'span.PXMot')

        for data in review_num_list:
            num = extract_score(data.text)
            if num is not None:
                review_num += num
        restaurant['review_num'] = review_num

        # 리뷰 평점
        try:
            element = driver.find_element(By.CSS_SELECTOR, '.LXIwF')
            restaurant['score'] = extract_score(element.text)
        except NoSuchElementException:
            restaurant['score'] = None

        # 영업시간
        try:
            button_element = driver.find_element(By.CSS_SELECTOR, '.gKP9i.RMgN0')
            button_element.click()
            WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.w9QyJ')))
            time.sleep(2)

            hours = driver.find_elements(By.CSS_SELECTOR, '.w9QyJ')
            hour_lines = []
            for hour in hours:
                print(hour.text)
                hour_lines.append(hour.text)
            restaurant['opening_hours'] = create_schedule_dict(hour_lines)
        except NoSuchElementException:
            restaurant['opening_hours'] = None

        # Menu 크롤링
        driver.get(modify_url(restaurant['naver_url'], 'menu'))
        driver.implicitly_wait(3)
        driver.switch_to.frame('entryIframe')

        menu_list = driver.find_elements(By.CSS_SELECTOR, '.E2jtL')
        restaurant['menu'] = []

        for menu in menu_list:
            try:
                name = menu.find_element(By.CSS_SELECTOR, '.lPzHi').text
            except:
                name = None 

            try:
                description = menu.find_element(By.CSS_SELECTOR, '.kPogF').text
            except:
                description = None 

            try:
                price = menu.find_element(By.CSS_SELECTOR, '.GXS1X').text
            except:
                price = None 

            dict_temp = {
                'name': name,
                'description': description,
                'price': price,
            }
            restaurant['menu'].append(dict_temp)
            print(f'{name} ...완료')

        # 리뷰 크롤링
        time.sleep(2)
        driver.get(modify_url(restaurant['naver_url'], 'review'))
        driver.implicitly_wait(3)
        driver.switch_to.frame('entryIframe')
        
        loaded_reviews = 0
        max_reviews = min(100, review_num) if review_num else 100
        restaurant['review'] = []

        review_list = driver.find_elements(By.CSS_SELECTOR, '.EjjAW ')

        while loaded_reviews < max_reviews:
            # 현재 리뷰 리스트를 가져옴
            review_list = driver.find_elements(By.CSS_SELECTOR, '.EjjAW')

            for review in review_list[loaded_reviews:]:
                if loaded_reviews >= max_reviews:
                    break
                
                try:
                    review_text = review.find_element(By.CSS_SELECTOR, '.pui__vn15t2').text
                except:
                    review_text = None 

                try:
                    tags = []
                    tag_list = review.find_elements(By.CSS_SELECTOR, '.pui__jhpEyP')
                    for tag in tag_list:
                        tag_text = tag.text
                        tags.append(tag_text)
                except:
                    tags = None 

                try:
                    date_text = review.find_element(By.CSS_SELECTOR, '.Vk05k .pui__QKE5Pr .pui__gfuUIT time').text
                    date_text = extract_date(date_text)
                except:
                    date_text = None 

                dict_temp = {
                    'content': review_text,
                    'tags': tags,
                    'date': date_text,
                }
                restaurant['review'].append(dict_temp)
                loaded_reviews += 1
                
                print(f'리뷰 {loaded_reviews}...완료')

            # '더보기' 버튼 클릭
            try:
                more_button = driver.find_element(By.CSS_SELECTOR, 'a.fvwqf')
                more_button.click()
                time.sleep(2)  # 리뷰가 로드될 시간을 기다림
            except:
                print("더 이상 불러올 리뷰가 없습니다.")
                break

        print(f'총 {loaded_reviews}개의 리뷰를 가져왔습니다.')

        # 크롤링 완료 표시
        restaurant['finished'] = 1

        print(f'[{restaurant["name"]} 데이터 수집 완료]\n소요 시간 :', time.time() - start)
        pprint.pprint(restaurant)

        return restaurant

    except Exception as e:
        print(f"Error crawling {restaurant['name']}: {str(e)}")
        # 크롤링 실패 시 finished를 0으로 설정
        restaurant['finished'] = 0
        return restaurant

# 'merged_restaurants.json' 파일에서 데이터를 불러옵니다.
merged_data = load_merged_restaurants()

driver = webdriver.Chrome()

updated_restaurants = []

for restaurant in merged_data:
    updated_restaurant = crawl_restaurant(driver, restaurant)
    updated_restaurants.append(updated_restaurant)
    # 가게 정보를 크롤링할 때마다 JSON 파일 업데이트
    save_result_file(updated_restaurants)

driver.quit()
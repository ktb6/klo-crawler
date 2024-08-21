import json
import re
import time
from time import sleep
import naver
import pprint

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

def extract_first_number(text):
    numbers = re.findall(r'\d+', text)
    if numbers:
        return int(numbers[0])
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

results = naver.main()

driver = webdriver.Chrome()

restaurant_list = []

for result in results:
     # 시작시간
    start = time.time()
    print('[크롤링 시작...]')

    # Home 크롤링
    driver.get(modify_url(result['naver_url'], 'home'))
    driver.implicitly_wait(3)
    driver.switch_to.frame('entryIframe')

     # 카테고리
    category = driver.find_element(By.CSS_SELECTOR, 'span.lnJFt').text

    # 리뷰 전체 개수
    review_num = 0
    review_num_list = driver.find_elements(By.CSS_SELECTOR, 'span.PXMot')

    try:
        for data in range(len(review_num_list)):
            num = extract_first_number(review_num_list[data].text)
            review_num += num
    except NoSuchElementException:
        review_num = None

    # 리뷰 평점
    try:
        element = driver.find_element(By.CSS_SELECTOR, '.LXIwF')
        score = extract_first_number(element.text)
    except NoSuchElementException:
        score = None

    # 영업시간
    button_element = driver.find_element(By.CSS_SELECTOR, '.gKP9i.RMgN0')
    button_element.click()
    WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.w9QyJ')))
    time.sleep(2)

    hours = driver.find_elements(By.CSS_SELECTOR, '.w9QyJ')
    hour_lines = []
    try:
        for hour in hours:
            print(hour.text)
            hour_lines.append(hour.text)
        opening_hours = create_schedule_dict(hour_lines)
    except NoSuchElementException:
        opening_hours = None
    
    # dictionary 생성
    restaurant_dict = {'name': result['name'], 'category': category, 'distance': result['distance'], 'menu': [], 'review': [], 'review_num': review_num, 'score': score, 'opening_hours': opening_hours}

    # Menu 크롤링
    driver.get(modify_url(result['naver_url'], 'menu'))
    driver.implicitly_wait(3)
    driver.switch_to.frame('entryIframe')

    menu_list = driver.find_elements(By.CSS_SELECTOR, '.E2jtL')

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
        restaurant_dict['menu'].append(dict_temp)
        print(f'{name} ...완료')

    # 리뷰 크롤링
    time.sleep(2)
    driver.get(modify_url(result['naver_url'], 'review'))
    driver.implicitly_wait(3)
    driver.switch_to.frame('entryIframe')
    
    loaded_reviews = 0
    max_reviews = min(100, review_num)

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
            restaurant_dict['review'].append(dict_temp)
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

    restaurant_list.append(restaurant_dict)

# JSON 파일로 저장
with open('restaurant_list.json', 'w', encoding='utf-8') as json_file:
    json.dump(restaurant_list, json_file, ensure_ascii=False, indent=4)
print("restaurant_list가 'restaurant_list.json' 파일로 저장되었습니다.")
    
print('[데이터 수집 완료]\n소요 시간 :', time.time() - start)
pprint.pprint(restaurant_list)

driver.quit()  
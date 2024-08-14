from typing import List, Optional, Dict

# 메뉴 항목 타입 정의
class MenuItem:
    name: str
    description: Optional[str]
    price: str

# 리뷰 항목 타입 정의
class Review:
    content: str
    tags: List[str]
    date: str

# 영업시간 타입 정의
OpeningHours = Dict[str, str]

# 레스토랑 타입 정의
class Restaurant:
    name: str
    category: str
    distance: float
    menu: List[MenuItem]
    review: List[Review]
    review_num: int
    score: Optional[float]
    opening_hours: OpeningHours

# 전체 데이터 리스트 타입 정의
RestaurantList = List[Restaurant]
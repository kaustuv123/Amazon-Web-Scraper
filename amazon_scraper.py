import requests
import time
from datetime import datetime
import random
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any, List

def get_random_user_agent() -> str:
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    ]
    return random.choice(user_agents)

def get_headers() -> Dict[str, str]:
    return {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

def get_cookies() -> Dict[str, str]:
    return {
        'session-id': ''.join(random.choices('0123456789-', k=20)),
        'ubid-main': ''.join(random.choices('0123456789', k=13)),
        'x-main': ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=20))
    }

def get_product_title(soup: BeautifulSoup) -> Optional[str]:
    product_title = soup.find('span', {'id': 'productTitle', 'class': 'a-size-large product-title-word-break'})
    return product_title.get_text(strip=True) if product_title else None

def get_current_price(soup: BeautifulSoup) -> Optional[str]:
    price_container = soup.find('span', class_='a-price aok-align-center reinventPricePriceToPayMargin priceToPay')
    if not price_container:
        return None
    
    price_whole = price_container.find('span', class_='a-price-whole')
    price_symbol = price_container.find('span', class_='a-price-symbol')
    
    if price_whole and price_symbol:
        return f"{price_symbol.get_text(strip=True)}{price_whole.get_text(strip=True)}"
    return None

def get_original_price(soup: BeautifulSoup) -> Optional[str]:
    original_price_element = soup.find('span', class_='a-price a-text-price', attrs={'data-a-strike': 'true'})
    if not original_price_element:
        return None
    
    original_price = original_price_element.find('span', class_='a-offscreen')
    return original_price.get_text(strip=True) if original_price else None

def get_rating_info(soup: BeautifulSoup) -> Dict[str, Optional[str]]:
    reviews_container = soup.find('div', id='averageCustomerReviews')
    if not reviews_container:
        return {'rating': None, 'ratings_count': None}
    
    rating_element = reviews_container.find('span', class_='a-size-base a-color-base')
    ratings_count_element = reviews_container.find('span', id='acrCustomerReviewText')
    
    return {
        'rating': rating_element.get_text(strip=True) if rating_element else None,
        'ratings_count': ratings_count_element.get_text(strip=True) if ratings_count_element else None
    }

def get_offers(soup: BeautifulSoup) -> list:
    offers_container = soup.find('div', class_='vsx__offers')
    if not offers_container:
        return []
    
    offer_items = offers_container.find_all('div', class_='offers-items')
    offers = []
    
    for item in offer_items:
        title_element = item.find('h6', class_='offers-items-title')
        content_element = item.find('span', class_='a-truncate-full')
        count_element = item.find('a', class_='vsx-offers-count')
        
        if all([title_element, content_element, count_element]):
            offers.append({
                'title': title_element.get_text(strip=True),
                'content': content_element.get_text(strip=True),
                'count': count_element.get_text(strip=True)
            })
    
    return offers

def get_review_summary(soup: BeautifulSoup) -> Optional[str]:
    review_summary_container = soup.find('div', id='product-summary')
    if not review_summary_container:
        return None
    
    review_summary_paragraph = review_summary_container.find('p', class_='a-spacing-small')
    return review_summary_paragraph.get_text(strip=True) if review_summary_paragraph else None

def get_about_this_item(soup: BeautifulSoup) -> List[str]:
    about_items = []
    
    feature_bullets = soup.find('div', id='feature-bullets', class_='a-section a-spacing-medium a-spacing-top-small')
    if not feature_bullets:
        return []
    
    ul_element = feature_bullets.find('ul', class_='a-unordered-list a-vertical a-spacing-mini')
    if not ul_element:
        return []
    
    items = ul_element.find_all('li', class_='a-spacing-mini')
    
    for item in items:
        span = item.find('span', class_='a-list-item')
        if span:
            text = span.get_text(strip=True)
            if text and text != "About this item":
                about_items.append(text)
    
    return about_items

def get_technical_details(soup: BeautifulSoup) -> Dict[str, str]:
    technical_details = {}
    
    tech_table = soup.find('table', id='productDetails_techSpec_section_1')
    if not tech_table:
        return technical_details
    
    rows = tech_table.find_all('tr')
    
    for row in rows:
        header = row.find('th', class_='a-color-secondary a-size-base prodDetSectionEntry')
        value = row.find('td', class_='a-size-base prodDetAttrValue')
        
        if header and value:
            key = header.get_text(strip=True)
            val = value.get_text(strip=True)
            if key and val:
                technical_details[key] = val
    
    return technical_details

def get_additional_info(soup: BeautifulSoup) -> Dict[str, str]:
    additional_info = {}
    
    info_table = soup.find('table', id='productDetails_detailBullets_sections1')
    if not info_table:
        return additional_info
    
    rows = info_table.find_all('tr')
    
    for row in rows:
        header = row.find('th', class_='a-color-secondary a-size-base prodDetSectionEntry')
        value = row.find('td', class_='a-size-base prodDetAttrValue')
        
        if header and value:
            key = header.get_text(strip=True)
            val = value.get_text(strip=True)
            if key and val:
                additional_info[key] = val
    
    return additional_info

def get_product_image(soup: BeautifulSoup) -> Optional[str]:
    landing_image = soup.find('img', id='landingImage')
    if landing_image and landing_image.get('src'):
        return landing_image['src']
    
    img_wrapper = soup.find('div', id='imgTagWrapperId')
    if img_wrapper:
        img = img_wrapper.find('img')
        if img and img.get('src'):
            return img['src']
    
    return None

def scrape_amazon() -> Dict[str, Any]:
    url = "https://www.amazon.in/Visio-World-inches-VW32S-Ready/dp/B07MNNH484/ref=sr_1_3?crid=3LJ3Q2AOKKDGS&dib=eyJ2IjoiMSJ9.IOoaFUPI-cbgU1wANeJd9dvGWaa8-x-9bO4aGn_z7gExFP3q4FP02HQs3ds_v_vAYTetv0rN0DAEPWOQTIcCxiTu1hL9iZIyKtoqnNtDrL0zbU-ab8PZc95OptDb6DCBMlW45VjmFTx3I_NTx92lCQob2aAiTjw1PBDLQBxYS27T1eVXbhOOw9qCzt6pHFgOerw8mGwABuErSgbsMaylpu7IVTPnGT1rOhbwgPZAIGU.8Ix2gjndsdOUlaYE7m_Wm3tJYaBpXnAsNjW3hgGkc2k&dib_tag=se&keywords=tv&qid=1742926327&sprefix=tv%252Caps%252C351&sr=8-3"
    
    try:
        time.sleep(random.uniform(1, 3))
        session = requests.Session()
        response = session.get(url, headers=get_headers(), cookies=get_cookies())
        
        if response.status_code != 200:
            return {'error': f"Failed to retrieve the page. Status code: {response.status_code}"}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Collect all product information
        product_data = {
            'title': get_product_title(soup),
            'current_price': get_current_price(soup),
            'original_price': get_original_price(soup),
            'rating_info': get_rating_info(soup),
            'offers': get_offers(soup),
            'review_summary': get_review_summary(soup),
            'about_this_item': get_about_this_item(soup),
            'technical_details': get_technical_details(soup),
            'additional_info': get_additional_info(soup),
            'image_url': get_product_image(soup)
        }
        
        return product_data
            
    except Exception as e:
        return {'error': f"An error occurred: {str(e)}"}

def print_product_data(data: Dict[str, Any]) -> None:
    if 'error' in data:
        print(data['error'])
        return
    
    print("\n=== Product Information ===")
    print(f"Title: {data['title'] or 'Not found'}")
    print(f"Current Price: {data['current_price'] or 'Not found'}")
    print(f"Original Price: {data['original_price'] or 'Not found'}")
    print(f"Image URL: {data['image_url'] or 'Not found'}")
    
    print("\n=== Rating Information ===")
    print(f"Rating: {data['rating_info']['rating'] or 'Not found'}")
    print(f"Number of Ratings: {data['rating_info']['ratings_count'] or 'Not found'}")
    
    print("\n=== Offers ===")
    if data['offers']:
        for offer in data['offers']:
            print(f"\nOffer Title: {offer['title']}")
            print(f"Offer Content: {offer['content']}")
            print(f"Offer Count: {offer['count']}")
    else:
        print("No offers found")
    
    print("\n=== Review Summary ===")
    print(data['review_summary'] or 'Not found')
    
    print("\n=== About This Item ===")
    if data['about_this_item']:
        for item in data['about_this_item']:
            print(f"• {item}")
    else:
        print("No 'About This Item' information found")
    
    print("\n=== Technical Details ===")
    if data['technical_details']:
        for key, value in data['technical_details'].items():
            print(f"{key}: {value}")
    else:
        print("No technical details found")
    
    print("\n=== Additional Information ===")
    if data['additional_info']:
        for key, value in data['additional_info'].items():
            print(f"{key}: {value}")
    else:
        print("No additional information found")

if __name__ == "__main__":
    product_data = scrape_amazon()
    print_product_data(product_data)
import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import random
from typing import Optional, Dict, Any, List
from datetime import datetime

from amazon_scraper import (
    get_random_user_agent,
    get_headers,
    get_cookies,
    get_product_title,
    get_current_price,
    get_original_price,
    get_rating_info,
    get_offers,
    get_review_summary,
    get_about_this_item,
    get_technical_details,
    get_additional_info,
    get_product_image
)

def scrape_amazon(url: str) -> Dict[str, Any]:
    try:
        time.sleep(random.uniform(1, 3))
        session = requests.Session()
        response = session.get(url, headers=get_headers(), cookies=get_cookies())
        
        if response.status_code != 200:
            return {'error': f"Failed to retrieve the page. Status code: {response.status_code}"}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
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

def main():
    st.set_page_config(
        page_title="Amazon Product Scraper",
        page_icon="🛍️",
        layout="wide"
    )
    
    st.title("🛍️ Amazon Product Scraper")
    st.write("Enter an Amazon product URL to get detailed information about the product.")
    
    url = st.text_input("Enter Amazon Product URL:", placeholder="https://www.amazon.com/...")
    submit_button = st.button("Scrape Product")
    
    if submit_button and url:
        with st.spinner("Scraping product information..."):
            product_data = scrape_amazon(url)
            
            if 'error' in product_data:
                st.error(product_data['error'])
            else:
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if product_data['image_url']:
                        st.image(product_data['image_url'], use_column_width=True)
                    
                    st.subheader("Basic Information")
                    st.write(f"**Title:** {product_data['title']}")
                    st.write(f"**Current Price:** {product_data['current_price']}")
                    if product_data['original_price']:
                        st.write(f"**Original Price:** {product_data['original_price']}")
                    
                    st.subheader("Rating Information")
                    st.write(f"**Rating:** {product_data['rating_info']['rating']}")
                    st.write(f"**Number of Ratings:** {product_data['rating_info']['ratings_count']}")
                
                with col2:
                    if product_data['offers']:
                        st.subheader("Offers")
                        for offer in product_data['offers']:
                            with st.expander(f"Offer: {offer['title']}"):
                                st.write(f"**Content:** {offer['content']}")
                                st.write(f"**Count:** {offer['count']}")
                    
                    if product_data['review_summary']:
                        st.subheader("AI Generated Customer Reveiw")
                        st.write(product_data['review_summary'])
                    
                    if product_data['about_this_item']:
                        st.subheader("About This Item")
                        for item in product_data['about_this_item']:
                            st.write(f"• {item}")
                    
                    if product_data['technical_details']:
                        st.subheader("Technical Details")
                        for key, value in product_data['technical_details'].items():
                            st.write(f"**{key}:** {value}")
                    
                    if product_data['additional_info']:
                        st.subheader("Additional Information")
                        for key, value in product_data['additional_info'].items():
                            st.write(f"**{key}:** {value}")

if __name__ == "__main__":
    main()
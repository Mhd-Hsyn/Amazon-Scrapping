import csv, os, re, shutil, time, json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromiumService
from fake_useragent import UserAgent
from selenium.webdriver.common.keys import Keys


def get_random_headers():
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept-Language": "en-US,en;q=0.5"
    }
    return headers


def get_chromedrvier_options():
    headers = get_random_headers()
    print(headers)
    # Set Chrome options
    options = Options()
    # options.headless = True
    options.add_argument("--enable-logging")
    options.add_argument("--log-level=0")
    # options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
    options.add_argument(f'user-agent={headers["User-Agent"]}')
    options.add_argument("--no-sandbox")
    prefs = {
        "translate_whitelists": {"de":"en"},  # "de" is for German, "en" is for English
        "translate":{"enabled":True}
    }
    options.add_experimental_option("prefs", prefs)
    return options


def scrap_riviews(html):
  all_riviews_of_product= {
      "product_title": "",
      "reviews": []
  }
  soup = BeautifulSoup(html, 'html.parser')
  
  # For Product Title
  title_tag = soup.find('div', {'class': 'a-row product-title'})
  all_riviews_of_product["product_title"]= title_tag.text.strip() if title_tag else "No title"

  all_riviews_of_product["product_title"]="GIGABYTE GeForce RTX 3060 Gaming OC 12G (REV2.0) Graphics Card, 3X WINDFORCE Fans, 12GB 192-bit GDDR6, GV-N3060GAMING OC-12GD Video Card" 

  reviews_table = soup.find('div', {'id': 'cm_cr-review_list'})
  if reviews_table:
    all_reviews= reviews_table.find_all('div', {'data-hook': 'review'})
    
    for review_div in all_reviews:
      data={}
      
      # For Title
      title_tag = review_div.find('a', class_='a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold')
      # Exclude any nested elements like <i> or other spans by selecting only the last span within the tag
      if title_tag:
          # Find the last span within the a tag to avoid picking up the star rating text
          title = title_tag.find_all('span')[-1].text.strip() if title_tag.find_all('span') else "No title"
      else:
          title = "No title"
      
      data['title']= title


      # For review rating (5.0 out of 5 stars)
      rating_tag = review_div.find('i', {'data-hook':'review-star-rating'})
      rating = rating_tag.span.text.strip() if rating_tag and rating_tag.span else "No rating"
      data['rating']= rating

      # For customer
      customer_div = review_div.find('div', class_='a-profile-content')
      customer_name = customer_div.find('span', class_='a-profile-name')
      data['customer']= customer_name.text.strip() if customer_name else "No customer"

      # For date
      date_div = review_div.find('span', {'data-hook':'review-date'})
      data['date']= date_div.text.strip() if date_div else "No date"

      # For Description
      description_div = review_div.find('span', {'data-hook':'review-body'})
      if description_div:
        # Remove unwanted divs
        for unwanted_div in description_div.find_all('div', class_='a-section a-spacing-small a-spacing-top-mini video-block'):
            unwanted_div.decompose()
        
        # Extract the text from the remaining span
        review_text = description_div.get_text(strip=True) if description_div else "No review text"
      else:
        review_text = "No review text"
      data['description']= review_text

      # For Images 
      image_div= review_div.find("div", {'class': "review-image-tile-section"})
      if image_div:
        all_images= []
        all_img_ele= image_div.find_all('img', {'class': 'review-image-tile'})
        for img_ele in all_img_ele:
          all_images.append(img_ele['src'])
        data['image']= all_images
      else:
        data['image']= []

      # For Video 
      video_tag = review_div.find('input', class_='video-url')
      if video_tag:
        video_url = video_tag.get('value')
        data['video']= video_url


      # print(json.dumps(data, indent=2))

      all_riviews_of_product["reviews"].append(data)
    
    # print(all_riviews_of_product)

    print(json.dumps(all_riviews_of_product, indent=2))


    return all_riviews_of_product




def scrap_amazone_page():
    # try:
       
        options = get_chromedrvier_options()
        # driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install()), options=options)
        driver.maximize_window()

        driver.get("https://www.amazon.com/Fitbit-Management-Intensity-Tracking-Included/product-reviews/B0B5FGP237/ref=cm_cr_getr_d_paging_btm_next_9?ie=UTF8&reviewerType=all_reviews&pageNumber=9")

        scrap_riviews(html= driver.page_source)


        if driver:
            driver.quit()

    # except Exception as e:
    #     print("An error occurred./n/n", e)
    # finally:
    #     print("QUIT WEB DRIVER ______________")
    #     if driver:
    #         driver.quit()



def sysInit():
    scrap_amazone_page()


sysInit()
from numpy.core.fromnumeric import prod
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains as AC
import requests
import os

import time

class music_scraper:
    def __init__(self, driver_path, url_base, out_image_folder):
        self.chrome = webdriver.Chrome(executable_path = driver_path)
        self.url = url_base
        self.out_f = out_image_folder
    def pass_block_wall(self):
        try:
            WebDriverWait(self.chrome, 2).until(EC.presence_of_element_located((By.ID, "px-captcha")))
            block_button = self.chrome.find_element_by_id("px-captcha")
            action = AC(self.chrome)
            action.move_to_element_with_offset(block_button, 50, 50)
            action.click_and_hold()
            action.perform()
            time.sleep(5)
            action.release().perform()
            time.sleep(5)
            print("Block wall passed")
        except:
            print("Block wall not encountered")
    def go_to_link(self, url):
        self.chrome.get(url)
    def return_to_prev_window(self, prev_window):
        self.chrome.close()
        self.chrome.switch_to.window(prev_window)
    def save_image(self, img_link, prod_name):
        page = requests.get(img_link)
        out_file = os.path.join(self.out_f + "pic_%s.wbep" % prod_name)
        with open(out_file, "wb") as f:
            f.write(page.content)
    def get_media_link(self):
        WebDriverWait(self.chrome, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='media']")))
        return self.chrome.find_element_by_css_selector("a[href*='media']").get_attribute("href")
    def get_product_name(self):
        raw_text = self.chrome.find_element_by_class_name("product__name").text
        bad_chars = [" ", "\n", "/", "\\"]
        for char in bad_chars:
            raw_text = raw_text.replace(char, "_")
        prod_name = raw_text.replace("___", "_").replace("_-_", "_")
        return prod_name
    def go_to_variant_product_page(self, link):
        self.chrome.execute_script("window.open('%s')" % link)
        self.pass_block_wall()
        new_window = self.chrome.window_handles[2]
        self.chrome.switch_to.window(new_window)
        img_link = self.get_media_link()
        prod_name = self.get_product_name()
        self.save_image(img_link, prod_name)
    def find_product_variants(self):
        current_window = self.chrome.window_handles[1]
        variants = self.chrome.find_elements_by_class_name("product-property-gallery__variant")
        if variants:
            for variant in variants:
                link = variant.find_element_by_css_selector("a[href*='/store/detail/']").get_attribute("href")
                self.go_to_variant_product_page(link)
                self.return_to_prev_window(current_window)
    def go_to_product_page(self, link):
        self.chrome.execute_script("window.open('%s', 'new window')" % link)
        self.pass_block_wall()
        new_window = self.chrome.window_handles[1]
        self.chrome.switch_to.window(new_window)
        self.find_product_variants()
        img_link = self.get_media_link()
        prod_name = self.get_product_name()
        self.save_image(img_link, prod_name)
    def parse_products_on_page(self):
        elements = self.chrome.find_elements_by_class_name("product-card__name")
        for i, element in enumerate(elements):
            link = element.find_element_by_css_selector("a[href*='/store/detail/']").get_attribute("href")
            self.go_to_product_page(link)
            self.return_to_prev_window(self.main_window)
    def scrape(self):
        self.go_to_link(self.url)
        self.main_window = self.chrome.window_handles[0]
        self.pass_block_wall()
        try:
            while True:
                WebDriverWait(self.chrome, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "product-card__name")))
                self.parse_products_on_page()
                WebDriverWait(self.chrome, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "next")))
                next_button = self.chrome.find_element_by_class_name("next")
                next_button.click()
                self.pass_block_wall()

        except:
            print("Finished parsing")
            #<div id="omQSckiXJkHmvhd"></div>
            #<div id="pDcoNCiqQLpJEKQ" role="main" aria-label="Human Challenge requires verification. Please press and hold the button until verified"><div id="omQSckiXJkHmvhd"></div><p id="eXeFXORxkeJYmog" class="QLKumVhLJZYNQDG">Press &amp; Hold</p><div class="fetching-volume"><span>•</span><span>•</span><span>•</span></div><div id="checkmark"></div><div id="ripple"></div></div>
            #<iframe style="display: block; width: 310px; height: 100px; border: 0; -moz-user-select: none; -khtml-user-select: none; -webkit-user-select: none; -ms-user-select: none; user-select: none;" token="5e254d51bb32574cad8d6958468b26638067932f4a065eb3e21da0c520a3b3aeaca608a3c7aa99c957db1c6e21fd5c604f55e13366b64cfbd7d99fee20d6a645"></iframe>
        
        

        

if __name__ == "__main__":
    driver_exec = "/home/kiegan/Documents/GANs/Utilities/chromedriver"
    scrape_url = 'https://www.sweetwater.com/c590--Solidbody_Guitars'
    out_path = "/home/kiegan/Documents/Datasets/Images/Guitars/Solidbody/"
    ms = music_scraper(driver_exec, scrape_url, out_path)
    ms.scrape()
    
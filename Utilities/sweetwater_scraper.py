from PIL.Image import new
from numpy.core.shape_base import block
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
            block_button = WebDriverWait(self.chrome, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="fCHGVAUAGNpHyRv"]')))
            size = len(block_button)
            action = AC(self.chrome)
            action.click_and_hold(on_element = block_button)
            action.perform()
            print("Block wall passed")
        except:
            print("Block wall not encountered")
    def go_to_link(self, url):
        self.chrome.get(url)
    def scrape(self):
        self.go_to_link(self.url)
        WebDriverWait(self.chrome, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "product-card__name")))
        main_window = self.chrome.window_handles[0]
        elements = self.chrome.find_elements_by_class_name("product-card__name")
        for i, element in enumerate(elements):
            link = element.find_element_by_css_selector("a[href*='/store/detail/']").get_attribute("href")
            self.chrome.execute_script("window.open('%s', 'new window')" % link)
            new_window = self.chrome.window_handles[1]
            self.chrome.switch_to.window(new_window)
            WebDriverWait(self.chrome, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='media']")))
            img_link = self.chrome.find_element_by_css_selector("a[href*='media']").get_attribute("href")
            page = requests.get(img_link)
            out_file = os.path.join(self.out_f + "pic%d.wbep" % i)
            with open(out_file, "wb") as f:
                f.write(page.content)
            self.chrome.close()
            self.chrome.switch_to.window(main_window)

        

if __name__ == "__main__":
    driver_exec = "/home/kiegan/Documents/GANs/Utilities/chromedriver"
    scrape_url = 'https://www.sweetwater.com/c590--Solidbody_Guitars'
    out_path = "/home/kiegan/Documents/Datasets/Images/Guitars/Solidbody/"
    ms = music_scraper(driver_exec, scrape_url, out_path)
    ms.scrape()
    
import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append('/home/kiegan/Documents/pinterest-image-scraper/pinterest_scraper')
import scraper as s
from selenium import webdriver


    

if __name__ == "__main__":
    # username = input('Enter Pinterest Username: ')
    # password = input('Enter Pinterest Password: ')
    chrome = webdriver.Chrome(executable_path = '/home/kiegan/Documents/pinterest-image-scraper/pinterest_scraper/chromedriver')
    ph = s.Pinterest_Helper('kiegan.lenihan@duke.edu', '97Paintball!@', chrome)
    images = ph.runme('https://www.pinterest.com/kieganlenihan/idk/')
    s.download(images, '/home/kiegan/Downloads')
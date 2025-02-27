from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

url = "https://www.kaggle.com/datasets/meharshanali/nvidia-stocks-data-2025"

def setup_driver(chromedriver_path=None):
    """Set up a Chrome driver with enhanced SSL bypass."""
    options = Options()
    # options.add_argument("--headless")  # 暂时禁用headless以调试
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors=yes")
    options.add_argument("--disable-gpu")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    if chromedriver_path:
        driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
    else:
        driver = webdriver.Chrome(options=options)
    return driver

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
import time

def setup_driver():
    """初始化WebDriver"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 无头模式（可选）
    return webdriver.Chrome(options=options)

def extract_file_details(url):
    """Fetch NVDA.csv file details (name, description, and columns) with detailed error handling."""
    driver = setup_driver()
    try:
        print(f"Fetching URL: {url}")
        driver.set_page_load_timeout(30)
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        print("Page title:", driver.title)
        
        cat_features = {"Entity": "", "Code": ""}
        num_features = {"Date": "", "High": "", "Low": ""}
        keys_union = set(cat_features.keys()).union(num_features.keys())  # 修正变量名拼写错误
        
        # 滚动到页面底部
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # 等待页面加载（示例：等待某个元素出现）
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".footer-load-indicator")))
        except TimeoutException:
            print("滚动后内容未加载！")
        
        # 遍历特征名
        for string in keys_union:
            try:
                # 动态构造定位器（需根据实际网页结构调整）
                locator = (By.XPATH, f'//div[contains(@class, "feature-row") and .//text()="{string}"]//span[@class="description"]')
                description_element = wait.until(EC.presence_of_element_located(locator))
                
                if string in cat_features:
                    cat_features[string] = description_element.text
                elif string in num_features:
                    num_features[string] = description_element.text
            except TimeoutException:
                print(f"特征 {string} 的描述元素未找到！")
                continue
        
        print("分类特征:", cat_features)
        print("数值特征:", num_features)
        
    except (WebDriverException, TimeoutException, NoSuchElementException) as e:
        print(f"Error loading page or finding elements: {str(e)}")
        driver.save_screenshot("error_screenshot.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    url = "https://example.com/nvda.csv"  # 替换为实际URL
    extract_file_details(url)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import time
import os

def setup_driver(chromedriver_path=None):
    """Set up a headless Chrome driver with enhanced SSL bypass."""
    options = Options()
    options.add_argument("--headless")  # Temporarily disable headless to debug visually
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors=yes")
    options.add_argument("--disable-gpu")  # Sometimes helps with headless issues
    options.add_argument("--allow-insecure-localhost")  # For potential local proxy issues
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")  # Mimic a real browser
    
    if chromedriver_path:
        driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
    else:
        driver = webdriver.Chrome(options=options)
    return driver

def extract_top_posts(url, num_posts=2):
    """Fetch top discussion posts with detailed error handling."""
    driver = setup_driver()
    try:
        print(f"Fetching URL: {url}")
        driver.set_page_load_timeout(30)  # Set a timeout to avoid hanging
        driver.get(url)
        time.sleep(10)  # Wait for content
        
        print("Page title:", driver.title)
        
        items = driver.find_elements(By.CSS_SELECTOR, ".discussion-list__item")
        print(f"Found {len(items)} discussion items.")

        posts = []
        for item in items:
            try:
                title = item.find_element(By.CSS_SELECTOR, ".discussion-list__title").text.strip()
                replies_text = item.find_element(By.CSS_SELECTOR, ".discussion-list__replies-count").text.split()[0]
                replies = int(replies_text)
                link = "https://www.kaggle.com" + item.find_element(By.TAG_NAME, "a").get_attribute("href")
                posts.append({"title": title, "replies": replies, "link": link})
            except Exception as e:
                print(f"Error parsing item: {e}")
                continue
        
        return sorted(posts, key=lambda x: x["replies"], reverse=True)[:num_posts]
    except WebDriverException as e:
        print(f"WebDriver error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []
    finally:
        driver.quit()

def get_post_content(post, save_path="output"):
    """Fetch post content and comments."""
    driver = setup_driver()
    try:
        print(f"Fetching post: {post['title']}")
        driver.get(post["link"])
        time.sleep(5)

        content_elem = driver.find_element(By.CSS_SELECTOR, ".discussion-post__content")
        content_text = content_elem.text if content_elem else "[Content parsing failed]"

        comments = driver.find_elements(By.CSS_SELECTOR, ".discussion-comment__body")[:3]
        comments_text = "\n".join([f"- {c.text}" for c in comments]) if comments else "No comments found"

        os.makedirs(save_path, exist_ok=True)
        filename = f"{save_path}/{post['title'][:30].replace(' ', '_')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {post['title']}\n\n## Content\n{content_text}\n\n## Comments\n{comments_text}")
        
        return filename
    except Exception as e:
        print(f"Failed to parse post [{post['title']}]: {e}")
        return None
    finally:
        driver.quit()

def main():
    url = "https://www.kaggle.com/datasets/asaniczka/tmdb-movies-dataset-2023-930k-movies/discussion"
    print("🚀 Starting to fetch top posts...")
    top_posts = extract_top_posts(url)
    
    if not top_posts:
        print("⚠️ No posts found.")
        return
    
    print(f"✅ Found {len(top_posts)} top posts:")
    for post in top_posts:
        print(f"📄 Processing: {post['title']} (Replies: {post['replies']})")
        saved_file = get_post_content(post)
        if saved_file:
            print(f"💾 Saved to: {saved_file}")

if __name__ == "__main__":
    start_time = time.time()
    main()
    print(f"⏱️ Total time: {time.time() - start_time:.1f} seconds")
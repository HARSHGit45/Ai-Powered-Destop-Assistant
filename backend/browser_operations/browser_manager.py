import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class BrowserOperations:
    def __init__(self):
        self.driver = None
        self.browser_type = None

    def initialize_browser(self, browser_name):
        """Initialize the specified browser"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        browser_name = browser_name.lower()
    
        try:
            if browser_name == "chrome":
                from selenium.webdriver.chrome.service import Service as ChromeService
                from webdriver_manager.chrome import ChromeDriverManager
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service)
                self.browser_type = "chrome"
            elif browser_name == "firefox":
                from selenium.webdriver.firefox.service import Service as FirefoxService
                from webdriver_manager.firefox import GeckoDriverManager
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service)
                self.browser_type = "firefox"
            elif browser_name in ["edge", "microsoft edge"]:
                from selenium.webdriver.edge.service import Service as EdgeService
                from webdriver_manager.microsoft import EdgeChromiumDriverManager
                service = EdgeService(EdgeChromiumDriverManager().install())
                self.driver = webdriver.Edge(service=service)
                self.browser_type = "edge"
            elif browser_name == "opera":
                # Note: Opera implementation might need adjustment based on current webdriver-manager support
                from selenium.webdriver.chrome.service import Service as ChromeService
                from webdriver_manager.opera import OperaDriverManager
                service = ChromeService(OperaDriverManager().install())
                self.driver = webdriver.Chrome(service=service)  # Opera uses Chrome's WebDriver
                self.browser_type = "opera"
            else:
                # Default to Chrome if browser not specified or recognized
                from selenium.webdriver.chrome.service import Service as ChromeService
                from webdriver_manager.chrome import ChromeDriverManager
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service)
                self.browser_type = "chrome"
                
            self.driver.maximize_window()
            return {"success": True, "message": f"{browser_name.title()} browser opened successfully"}
        except Exception as e:
            return {"success": False, "error": f"Failed to open {browser_name}: {str(e)}"}

    def perform_search(self, query, search_engine="google"):
        """Perform a search in the current browser"""
        if not self.driver:
            result = self.initialize_browser("chrome")
            if not result["success"]:
                return result
                
        try:
            search_engines = {
                "google": "https://www.google.com",
                "bing": "https://www.bing.com",
                "yahoo": "https://search.yahoo.com",
                "duckduckgo": "https://duckduckgo.com"
            }
            
            url = search_engines.get(search_engine.lower(), search_engines["google"])
            self.driver.get(url)
            
            # Different search box selectors for different engines
            selectors = {
                "google": (By.NAME, "q"),
                "bing": (By.NAME, "q"),
                "yahoo": (By.NAME, "p"),
                "duckduckgo": (By.NAME, "q")
            }
            
            selector = selectors.get(search_engine.lower(), selectors["google"])
            
            # Wait for search box to be visible
            search_box = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(selector)
            )
            
            # Enter search query and submit
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            
            # Wait for search results
            time.sleep(3)
            
            return {"success": True, "message": f"Searched for '{query}' on {search_engine}"}
        except Exception as e:
            return {"success": False, "error": f"Search failed: {str(e)}"}

    def navigate_to_url(self, url):
        """Navigate to a specific URL"""
        if not self.driver:
            result = self.initialize_browser("chrome")
            if not result["success"]:
                return result
                
        try:
            # Add http prefix if not present
            if not url.startswith("http"):
                url = "https://" + url
                
            self.driver.get(url)
            return {"success": True, "message": f"Navigated to {url}"}
        except Exception as e:
            return {"success": False, "error": f"Navigation failed: {str(e)}"}

    def gmail_operations(self, action, recipient=None, subject=None, body=None):
        """Handle Gmail operations"""
        if not self.driver:
            result = self.initialize_browser("chrome")
            if not result["success"]:
                return result
                
        try:
            # Navigate to Gmail if not already there
            if "mail.google.com" not in self.driver.current_url:
                self.driver.get("https://mail.google.com")
                time.sleep(3)
            
            # Check if we need to log in
            if "accounts.google.com" in self.driver.current_url:
                return {"success": False, "error": "Gmail login required. Please log in manually first."}
            
            if action == "compose":
                # Click Compose button
                compose_btn = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Compose')]"))
                )
                compose_btn.click()
                
                # Wait for compose window
                time.sleep(2)
                
                # Fill recipient
                if recipient:
                    to_field = WebDriverWait(self.driver, 10).until(
                        EC.visibility_of_element_located((By.XPATH, "//textarea[@name='to']"))
                    )
                    to_field.send_keys(recipient)
                
                # Fill subject
                if subject:
                    subject_field = self.driver.find_element(By.NAME, "subjectbox")
                    subject_field.send_keys(subject)
                
                # Fill body
                if body:
                    body_field = self.driver.find_element(By.XPATH, "//div[@role='textbox']")
                    body_field.send_keys(body)
                
                return {"success": True, "message": "Email composed successfully"}
                
            elif action == "send":
                # Click send button
                send_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Send')]"))
                )
                send_btn.click()
                
                # Wait for confirmation
                time.sleep(2)
                
                return {"success": True, "message": "Email sent successfully"}
                
            elif action == "open":
                # Construct search query based on available data
                search_terms = []
                if subject:
                    search_terms.append(subject)
                if body:
                    # Add a few words from the body
                    body_words = body.split()[:3]
                    search_terms.extend(body_words)
                if recipient:
                    search_terms.append(f"to:{recipient}")
                
                search_query = " ".join(search_terms)
                
                # Click on search box
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Search mail']"))
                )
                search_box.click()
                search_box.clear()
                search_box.send_keys(search_query)
                search_box.send_keys(Keys.RETURN)
                
                # Wait for search results
                time.sleep(3)
                
                # Click on the first email
                first_email = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//tr[@role='row']"))
                )
                first_email.click()
                
                return {"success": True, "message": f"Opened email matching: {search_query}"}
                
            else:
                return {"success": False, "error": f"Unsupported Gmail action: {action}"}
                
        except Exception as e:
            return {"success": False, "error": f"Gmail operation failed: {str(e)}"}

    def youtube_operations(self, query, action="search"):
        """Handle YouTube operations"""
        if not self.driver:
            result = self.initialize_browser("chrome")
            if not result["success"]:
                return result
                
        try:
            # Navigate to YouTube
            self.driver.get("https://www.youtube.com")
            
            # Wait for search box
            search_box = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.NAME, "search_query"))
            )
            
            # Enter search query and submit
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            
            # Wait for search results
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "contents"))
            )
            
            if action == "play":
                # Click on the first video
                first_video = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//ytd-video-renderer[1]//a[@id='thumbnail']"))
                )
                first_video.click()
                
                return {"success": True, "message": f"Playing YouTube video for '{query}'"}
            else:
                return {"success": True, "message": f"Searched for '{query}' on YouTube"}
                
        except Exception as e:
            return {"success": False, "error": f"YouTube operation failed: {str(e)}"}

    def social_media_operation(self, platform, action=None):
        """Handle social media operations"""
        social_urls = {
            "facebook": "https://www.facebook.com",
            "twitter": "https://twitter.com",
            "instagram": "https://www.instagram.com",
            "linkedin": "https://www.linkedin.com",
            "reddit": "https://www.reddit.com"
        }
        
        if platform.lower() in social_urls:
            return self.navigate_to_url(social_urls[platform.lower()])
        else:
            return {"success": False, "error": f"Unsupported social media platform: {platform}"}

    def process_command(self, command_data):
        """Process browser command based on classification"""
        try:
            action_type = command_data.get("action_type", "")
            
            # Check if browser needs to be opened/changed
            browser = command_data.get("browser", "chrome")
            if action_type == "open_browser":
                return self.initialize_browser(browser)
            elif not self.driver:
                # Initialize browser if not already done
                result = self.initialize_browser(browser)
                if not result["success"]:
                    return result
            
            # Process based on action type
            if action_type == "search":
                return self.perform_search(
                    command_data.get("query", ""),
                    command_data.get("search_engine", "google")
                )
                
            elif action_type == "navigate":
                return self.navigate_to_url(command_data.get("url", ""))
                
            elif action_type == "email":
                return self.gmail_operations(
                    command_data.get("email_action", "compose"),
                    command_data.get("recipient"),
                    command_data.get("subject"),
                    command_data.get("body")
                )
                
            elif action_type == "youtube":
                return self.youtube_operations(
                    command_data.get("query", ""),
                    command_data.get("youtube_action", "search")
                )
                
            elif action_type == "social_media":
                return self.social_media_operation(
                    command_data.get("platform", ""),
                    command_data.get("social_action")
                )
                
            else:
                return {"success": False, "error": f"Unsupported browser action: {action_type}"}
                
        except Exception as e:
            return {"success": False, "error": f"Browser operation failed: {str(e)}"}
            
    def close(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                return {"success": True, "message": "Browser closed"}
            except Exception as e:
                return {"success": False, "error": f"Failed to close browser: {str(e)}"}
        return {"success": True, "message": "No browser to close"}
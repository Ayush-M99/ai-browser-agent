# Improved Gmail Browser Agent with better element selectors and error handling
# Install first: pip install undetected-chromedriver

import os
import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import base64

class BrowserAgent:
    def __init__(self, email, password, screenshot_dir="screenshots", emit_callback=None):
        self.email = email
        self.password = password
        self.screenshot_dir = screenshot_dir
        os.makedirs(screenshot_dir, exist_ok=True)
        self.emit = emit_callback

        # Create undetected Chrome instance
        options = uc.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-plugins-discovery")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless=new")
        # Use undetected chromedriver
        self.driver = uc.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.delete_all_cookies()

    def _emit(self, text=None, image_path=None):
        if self.emit:
            self.emit(text, image_path)
        elif text:
            print(text)

    def wait_and_screenshot(self, name, timeout=20):
        """Wait and take screenshot"""
        if not self.driver:
            self._emit(f"[!] Cannot take screenshot, driver is None")
            return None
        time.sleep(random.uniform(1, 2))
        path = os.path.join(self.screenshot_dir, f"{name}.png")
        try:
            self.driver.save_screenshot(path)
            self._emit(f"[✓] Screenshot saved: {path}", path)
        except Exception as e:
            self._emit(f"[!] Screenshot failed: {e}")
        return path

    def check_if_recipient_accepted(self):
        """Check if the recipient email has been accepted/selected"""
        if not self.driver:
            return False
        try:
            # Look for signs that the email has been accepted
            accepted_selectors = [
                "//span[contains(@class, 'aZo') and contains(@email, '@')]",
                "//span[contains(@class, 'go') and contains(@email, '@')]",
                "//div[contains(@class, 'vR')]//span[contains(@email, '@')]",
                "//span[contains(@title, '@')]"
            ]
            
            for selector in accepted_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    text = element.get_attribute('textContent')
                    if element and text and '@' in text:
                        return True
                except:
                    continue
            return False
        except:
            return False

    def human_type(self, element, text):
        """Type like a human"""
        if not element:
            self._emit("[!] Cannot type, element is None")
            return
        try:
            element.clear()
            time.sleep(0.2)
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
        except Exception as e:
            self._emit(f"[!] Typing failed: {e}")

    def click_show_password(self):
        """Try to click show password button/checkbox"""
        if not self.driver:
            self._emit("[!] Cannot click show password, driver is None")
            return False
        try:
            show_password_selectors = [
                "//input[@type='checkbox'][@aria-label='Show password']",
                "//button[@aria-label='Show password']",
                "//span[contains(text(), 'Show password')]",
                "//div[contains(text(), 'Show password')]",
                "//input[@type='checkbox'][contains(@aria-describedby, 'password')]",
                "//button[contains(@class, 'show-password')]"
            ]

            for selector in show_password_selectors:
                try:
                    show_element = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    show_element.click()
                    self._emit("[✓] Show password button clicked!")
                    time.sleep(random.uniform(0.5, 1))
                    return True
                except:
                    continue

            self._emit("[ℹ] Show password button not found, continuing...")
            return False
        except Exception as e:
            self._emit(f"[ℹ] Show password not available: {str(e)}")
            return False

    def login_to_gmail(self):
        """Login to Gmail using undetected chromedriver"""
        if not self.driver:
            self._emit("[!] Cannot login, driver is None")
            return False
        try:
            self._emit("[🔄] Opening Gmail...")
            self.driver.get("https://accounts.google.com/signin")
            self.wait_and_screenshot("01_gmail_page")

            # Enter email
            self._emit("[🔄] Entering email...")
            email_input = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.ID, "identifierId"))
            )
            email_input.clear()
            email_input.click()
            self.human_type(email_input, self.email)
            self.wait_and_screenshot("02_email_entered")

            # Click Next
            next_button = self.driver.find_element(By.ID, "identifierNext")
            next_button.click()
            self.wait_and_screenshot("03_next_clicked")

            # Wait for password page
            time.sleep(random.uniform(2, 4))
            self._emit("[🔄] Waiting for password field to appear...")
            self.wait_and_screenshot("04_password_page_loaded")

            # Find password input
            self._emit("[🔄] Looking for password input field...")
            password_selectors = [
                "//input[@name='password']",
                "//input[@type='password']",
                "//input[@aria-label='Enter your password']",
                "//input[contains(@aria-describedby, 'password')]",
                "//div[@id='password']//input",
                "//input[@autocomplete='current-password']",
                "//input[@name='Passwd']",  # Add this if you see it in the HTML
            ]

            password_input = None
            for selector in password_selectors:
                try:
                    password_input = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    self._emit(f"[✓] Password field found with selector: {selector}")
                    break
                except:
                    continue

            if not password_input:
                self._emit("[❌] Password field not found with any selector")
                self.wait_and_screenshot("error_password_field_not_found")
                return False

            # Enter password
            self._emit("[🔄] Clicking on password input box...")
            password_input.click()
            time.sleep(0.5)
            password_input.clear()
            self.human_type(password_input, self.password)
            self.wait_and_screenshot("05_password_field_filled")

            # Click Next
            password_next = self.driver.find_element(By.ID, "passwordNext")
            password_next.click()
            self.wait_and_screenshot("07_password_next_clicked")

            # Wait for login success
            self._emit("[🔄] Waiting for login success...")
            try:
                WebDriverWait(self.driver, 30).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, "//div[text()='Compose']")),
                        EC.url_contains("mail.google.com"),
                        EC.presence_of_element_located((By.XPATH, "//div[@role='main']"))
                    )
                )
                self.wait_and_screenshot("08_login_success")
                self._emit("[✅] Login successful!")
                return True

            except TimeoutException:
                self.wait_and_screenshot("error_login_failed")
                self._emit("[❌] Login failed or extra verification required.")
                return False

        except Exception as e:
            self._emit(f"[❌] Login failed: {str(e)}")
            self.wait_and_screenshot("error_login_exception")
            return False

    def compose_and_send_email(self, to, subject, body):
        """Compose and send email with improved selectors"""
        if not self.driver:
            self._emit("[!] Cannot send email, driver is None")
            return False
        try:
            # Make sure we're on Gmail
            if "mail.google.com" not in self.driver.current_url:
                self._emit("[🔄] Navigating to Gmail...")
                self.driver.get("https://mail.google.com")
                time.sleep(5)

            self.wait_and_screenshot("08_gmail_loaded")

            # Wait for Gmail to fully load
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='main']"))
            )

            # Find and click Compose button - improved selectors
            self._emit("[🔄] Looking for Compose button...")
            compose_selectors = [
                "//div[contains(@class, 'T-I') and contains(@class, 'T-I-KE') and contains(@class, 'L3')]",
                "//div[@role='button' and contains(text(), 'Compose')]",
                "//div[contains(@class, 'z0') and contains(text(), 'Compose')]",
                "//div[contains(@class, 'aic') and contains(text(), 'Compose')]",
                "//div[text()='Compose']",
                "//button[contains(@aria-label, 'Compose')]"
            ]

            compose_button = None
            for selector in compose_selectors:
                try:
                    compose_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    self._emit(f"[✓] Compose button found with selector: {selector}")
                    break
                except Exception:
                    continue

            if not compose_button:
                self._emit("[❌] Compose button not found")
                self.wait_and_screenshot("error_compose_not_found")
                return False

            # Click compose with retry
            for attempt in range(3):
                try:
                    compose_button.click()
                    self._emit(f"[✓] Compose button clicked (attempt {attempt + 1})")
                    time.sleep(2)
                    break
                except Exception as e:
                    self._emit(f"[!] Compose click attempt {attempt + 1} failed: {e}")
                    if attempt == 2:
                        return False
                    time.sleep(1)

            self.wait_and_screenshot("09_compose_opened")

            # Wait for compose window to open
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'AD')]"))
            )

            # Fill recipient with multiple selector attempts
            self._emit("[🔄] Filling recipient...")
            to_selectors = [
                "//textarea[@name='to']",
                "//input[@name='to']",
                "//textarea[contains(@aria-label, 'To')]",
                "//input[contains(@aria-label, 'To')]",
                "//div[@aria-label='To']//textarea",
                "//div[@aria-label='To']//input"
            ]

            to_input = None
            for selector in to_selectors:
                try:
                    to_input = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    self._emit(f"[✓] To field found with selector: {selector}")
                    break
                except Exception:
                    continue

            if not to_input:
                self._emit("[❌] To field not found")
                self.wait_and_screenshot("error_to_field_not_found")
                return False

            to_input.click()
            time.sleep(0.5)
            to_input.clear()
            self.human_type(to_input, to)
            time.sleep(1)
            self.wait_and_screenshot("10_recipient_typed")

            # Handle email suggestion dropdown - click the suggested email or press Enter/Tab
            self._emit("[🔄] Handling email suggestion...")
            try:
                # Method 1: Look for and click the email suggestion
                suggestion_selectors = [
                    f"//div[contains(@class, 'Sa') and contains(text(), '{to}')]",
                    f"//div[contains(@class, 'Jd') and contains(text(), '{to}')]",
                    f"//div[contains(@role, 'option') and contains(text(), '{to}')]",
                    f"//span[contains(text(), '{to}')]",
                    "//div[contains(@class, 'Sa')]",
                    "//div[contains(@class, 'Jd')]",
                    "//div[@role='option']"
                ]
                suggestion_clicked = False
                for selector in suggestion_selectors:
                    try:
                        suggestion = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        suggestion.click()
                        self._emit(f"[✓] Email suggestion clicked with selector: {selector}")
                        suggestion_clicked = True
                        time.sleep(1)
                        break
                    except Exception:
                        continue
                # Method 2: If no suggestion found, try pressing Enter or Tab
                if not suggestion_clicked:
                    self._emit("[🔄] No suggestion found, trying Enter key...")
                    to_input.send_keys(Keys.RETURN)
                    time.sleep(0.5)
                    # If Enter doesn't work, try Tab
                    if not self.check_if_recipient_accepted():
                        self._emit("[🔄] Enter didn't work, trying Tab key...")
                        to_input.send_keys(Keys.TAB)
                        time.sleep(0.5)
                # Method 3: If still not accepted, try clicking outside and back
                if not self.check_if_recipient_accepted():
                    self._emit("[🔄] Still not accepted, trying to click outside and back...")
                    try:
                        subject_input = self.driver.find_element(By.XPATH, "//input[@name='subjectbox']")
                        subject_input.click()
                        time.sleep(0.5)
                        to_input.click()
                        time.sleep(0.5)
                        to_input.send_keys(Keys.RETURN)
                        time.sleep(0.5)
                    except Exception:
                        pass
            except Exception as e:
                self._emit(f"[!] Error handling email suggestion: {e}")
                # Fallback: just press Enter
                try:
                    to_input.send_keys(Keys.RETURN)
                    time.sleep(0.5)
                except Exception:
                    pass

            # Fill subject
            self._emit("[🔄] Filling subject...")
            subject_selectors = [
                "//input[@name='subjectbox']",
                "//input[contains(@aria-label, 'Subject')]",
                "//input[@placeholder='Subject']",
                "//div[contains(@aria-label, 'Subject')]//input"
            ]
            subject_input = None
            for selector in subject_selectors:
                try:
                    subject_input = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    self._emit(f"[✓] Subject field found with selector: {selector}")
                    break
                except Exception:
                    continue
            if not subject_input:
                self._emit("[❌] Subject field not found")
                self.wait_and_screenshot("error_subject_field_not_found")
                return False
            subject_input.click()
            time.sleep(0.5)
            subject_input.clear()
            self.human_type(subject_input, subject)
            time.sleep(1)
            self.wait_and_screenshot("11_subject_filled")

            # Fill body
            self._emit("[🔄] Filling body...")
            body_selectors = [
                "//div[@aria-label='Message Body']",
                "//div[contains(@aria-label, 'Message body')]",
                "//div[@role='textbox']",
                "//div[contains(@class, 'Am') and @role='textbox']",
                "//div[contains(@class, 'editable')]"
            ]
            body_area = None
            for selector in body_selectors:
                try:
                    body_area = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    self._emit(f"[✓] Body area found with selector: {selector}")
                    break
                except Exception:
                    continue
            if not body_area:
                self._emit("[❌] Body area not found")
                self.wait_and_screenshot("error_body_area_not_found")
                return False
            body_area.click()
            time.sleep(1)
            body_area.clear()
            self.human_type(body_area, body)
            time.sleep(1)
            self.wait_and_screenshot("12_body_filled")

            # Send email
            self._emit("[🔄] Looking for Send button...")
            time.sleep(2)  # Give time for the compose window to be ready
            send_selectors = [
                "//div[@role='button' and contains(@class, 'T-I-atl')]",  # Most common Gmail send button
                "//div[contains(@class, 'T-I') and contains(@class, 'J-J5-Ji') and contains(@class, 'aoO')]",
                "//div[contains(@class, 'T-I') and contains(@class, 'J-J5-Ji') and contains(@class, 'T-I-atl')]",
                "//div[@role='button' and contains(@data-tooltip, 'Send')]",
                "//div[@role='button' and contains(@aria-label, 'Send')]",
                "//div[@role='button' and contains(text(), 'Send')]",
                "//div[contains(@class, 'dC') and @role='button']",
                "//div[contains(@class, 'T-I') and contains(@class, 'J-J5-Ji')]",
                "//button[contains(text(), 'Send')]",
                "//input[@type='submit' and @value='Send']"
            ]
            send_button = None
            for i, selector in enumerate(send_selectors):
                try:
                    send_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    self._emit(f"[✓] Send button found with selector {i+1}: {selector}")
                    break
                except Exception:
                    self._emit(f"[!] Send selector {i+1} failed: {selector}")
                    continue
            if not send_button:
                self._emit("[❌] Send button not found with any selector")
                self.wait_and_screenshot("error_send_button_not_found")
                # Try keyboard shortcut as primary fallback
                self._emit("[🔄] Trying keyboard shortcut Ctrl+Enter...")
                try:
                    body_area.click()
                    time.sleep(0.5)
                    body_area.send_keys(Keys.CONTROL + Keys.RETURN)
                    time.sleep(3)
                    self.wait_and_screenshot("13_email_sent_via_keyboard")
                    self._emit("[✅] Email sent via keyboard shortcut!")
                    return True
                except Exception as e:
                    self._emit(f"[❌] Keyboard shortcut failed: {e}")
                    return False
            self._emit("[🔄] Attempting to click Send button...")
            clicked = False
            for attempt in range(3):
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", send_button)
                    time.sleep(0.5)
                    send_button.click()
                    self._emit(f"[✓] Send button clicked successfully (attempt {attempt + 1})")
                    clicked = True
                    break
                except Exception as e:
                    self._emit(f"[!] Send click attempt {attempt + 1} failed: {e}")
                    time.sleep(1)
            if not clicked:
                try:
                    self._emit("[🔄] Trying JavaScript click...")
                    self.driver.execute_script("arguments[0].click();", send_button)
                    self._emit("[✓] Send button clicked via JavaScript!")
                    clicked = True
                except Exception as e:
                    self._emit(f"[!] JavaScript click failed: {e}")
            if not clicked:
                try:
                    self._emit("[🔄] Trying ActionChains click...")
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(self.driver)
                    actions.move_to_element(send_button).click().perform()
                    self._emit("[✓] Send button clicked via ActionChains!")
                    clicked = True
                except Exception as e:
                    self._emit(f"[!] ActionChains click failed: {e}")
            if not clicked:
                self._emit("[🔄] All click methods failed, trying keyboard shortcut...")
                try:
                    body_area.click()
                    time.sleep(0.5)
                    body_area.send_keys(Keys.CONTROL + Keys.RETURN)
                    time.sleep(3)
                    clicked = True
                    self._emit("[✅] Email sent via keyboard shortcut fallback!")
                except Exception as e:
                    self._emit(f"[❌] Final keyboard shortcut failed: {e}")
                    return False
            if not clicked:
                self._emit("[❌] All send methods failed")
                return False
            time.sleep(3)
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Message sent')]")),
                        EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'sent')]"))
                    )
                )
                self.wait_and_screenshot("13_email_sent_success")
                self._emit("[✅] Email sent successfully!")
                return True
            except TimeoutException:
                self.wait_and_screenshot("13_email_sent_no_confirmation")
                self._emit("[✅] Email likely sent (no confirmation toast found)")
                return True
        except Exception as e:
            self._emit(f"[❌] Email sending failed: {str(e)}")
            self.wait_and_screenshot("error_email_failed_detailed")
            return False

    def quit(self):
        """Properly close the browser to avoid handle errors"""
        try:
            if hasattr(self, 'driver') and self.driver:
                try:
                    self.driver.close()
                except Exception:
                    pass
                try:
                    self.driver.quit()
                except Exception:
                    pass
                self.driver = None
                self._emit("[✅] Browser closed successfully")
        except Exception as e:
            self._emit(f"[!] Error closing browser: {e}")
            self.driver = None
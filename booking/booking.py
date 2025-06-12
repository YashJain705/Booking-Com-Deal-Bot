import os
import time
import booking.constants as const

from selenium import webdriver
from booking.booking_filtrations import BookingFiltration
from booking.booking_report import BookingReport

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException


class Booking(webdriver.Chrome) :
    def __init__(self, driver_path = r"D:\SeleniumDrivers\chromedriver-win64", teardown = False) :
        self.driver_path = driver_path
        self.teardown = teardown
        os.environ['PATH'] += r"D:\SeleniumDrivers\chromedriver-win64"
        super(Booking, self).__init__()
        self.implicitly_wait(20)
        self.maximize_window()

    def __exit__(self, exc_type, exc, traceback) :
        if(self.teardown) :
            self.quit()
    
    def land_first_page(self) :
        self.get(const.BASE_URL)
        
    def select_currency(self, currency_code):
        currency_element = self.find_element(
            By.CSS_SELECTOR, 'button[data-testid="header-currency-picker-trigger"]'
        )
        currency_element.click()
        
        currency_buttons = self.find_elements(By.CSS_SELECTOR, "li button[data-testid='selection-item']")
        for button in currency_buttons:
            try:
                code = button.find_element(By.CLASS_NAME, "CurrencyPicker_currency").text.strip().upper()
                if code == currency_code.upper():
                    button.click()
                    return
            except:
                continue
        raise Exception(f"Currency {currency_code} not found.")
    
    def select_place_to_go(self, place_to_go) :
        search_box = self.find_element(By.CSS_SELECTOR, "input[placeholder='Where are you going?']")
        search_box.clear()
        search_box.send_keys(place_to_go)
        
        # Wait for the first autocomplete result to contain the correct city
        WebDriverWait(self, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "li[id='autocomplete-result-0']"), place_to_go
            )
        )

        # Now that the correct result is loaded, click it
        first_search_result = WebDriverWait(self, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "li[id='autocomplete-result-0']"))
        )
        first_search_result.click()
        
    def select_dates(self, check_in_date, check_out_date) :
        def get_visible_months():
            try:
                headers = self.find_elements(By.CSS_SELECTOR, "h3[class*='e7addce19']")
                return [header.text.strip() for header in headers]  # e.g., ['June 2025', 'July 2025']
            except:
                return []

        def month_str(dt):
            return dt.strftime("%B %Y")  # 'June 2025'

        def go_to_month(target_date):
            target_month = month_str(target_date)
            tries = 0
            while target_month not in get_visible_months():
                if tries > 12:
                    raise Exception(f"Couldn't reach month: {target_month}")
                next_btn = self.find_element(By.CSS_SELECTOR, "button[aria-label='Next month']")
                next_btn.click()
                time.sleep(0.4)
                tries += 1

        def click_date(date_str):
            try:
                date_elem = self.find_element(By.CSS_SELECTOR, f"span[data-date='{date_str}']")
                date_elem.click()
            except NoSuchElementException:
                raise Exception(f"Could not find/select date: {date_str}")

        # --- Validate Dates ---
        try:
            check_in_dt = datetime.strptime(check_in_date, "%Y-%m-%d")
            check_out_dt = datetime.strptime(check_out_date, "%Y-%m-%d")
            today = datetime.today()

            if check_in_dt < today:
                raise ValueError("Check-in date is in the past.")
            if check_out_dt <= check_in_dt:
                raise ValueError("Check-out must be after check-in.")
        except ValueError as ve:
            raise Exception(f"Invalid date input: {ve}")

        # --- Main Logic ---
        try:
            visible_months = get_visible_months()
            check_in_month = month_str(check_in_dt)
            check_out_month = month_str(check_out_dt)

            if check_in_month in visible_months and check_out_month in visible_months:
                # No need to scroll
                click_date(check_in_date)
                click_date(check_out_date)
            else:
                # Navigate months
                go_to_month(check_in_dt)
                click_date(check_in_date)

                go_to_month(check_out_dt)
                click_date(check_out_date)

        except Exception as e:
            raise Exception(f"Date selection failed: {e}")
        
        
    def select_travellers(self, adult_cnt, children_cnt, rooms_cnt):
        occupancy_element = self.find_element(
            By.CSS_SELECTOR, "button[data-testid='occupancy-config']"
        )
        occupancy_element.click()

        # Generic reset function to click "minus" until count is default
        def reset_count(span_selector, minus_selector, default_val):
            tries = 10
            while tries > 0:
                try:
                    span = self.find_element(By.CSS_SELECTOR, span_selector)
                    current = int(span.text.strip())
                    if current <= default_val:
                        break
                    minus_button = self.find_element(By.CSS_SELECTOR, minus_selector)
                    minus_button.click()
                    time.sleep(0.2)
                except:
                    break
                tries -= 1

        # Generic increment function to reach target value
        def increase_to_target(span_selector, plus_selector, target_val):
            tries = 10
            while tries > 0:
                try:
                    span = self.find_element(By.CSS_SELECTOR, span_selector)
                    current = int(span.text.strip())
                    if current >= target_val:
                        break
                    plus_button = self.find_element(By.CSS_SELECTOR, plus_selector)
                    plus_button.click()
                    time.sleep(0.2)
                except:
                    break
                tries -= 1

        # ⬇️ Placeholder selectors (replace these with actual class names or test IDs)
        ADULT_SPAN = "span.css-for-adult-count"
        ADULT_MINUS = "button.css-for-adult-minus"
        ADULT_PLUS = "button.css-for-adult-plus"

        CHILD_SPAN = "span.css-for-child-count"
        CHILD_MINUS = "button.css-for-child-minus"
        CHILD_PLUS = "button.css-for-child-plus"

        ROOM_SPAN = "span.css-for-room-count"
        ROOM_MINUS = "button.css-for-room-minus"
        ROOM_PLUS = "button.css-for-room-plus"

        # 🧹 Reset to default values
        reset_count(ADULT_SPAN, ADULT_MINUS, 1)
        reset_count(CHILD_SPAN, CHILD_MINUS, 0)
        reset_count(ROOM_SPAN, ROOM_MINUS, 1)

        # ⬆️ Increment to desired values
        increase_to_target(ADULT_SPAN, ADULT_PLUS, adult_cnt)
        increase_to_target(CHILD_SPAN, CHILD_PLUS, children_cnt)
        increase_to_target(ROOM_SPAN, ROOM_PLUS, rooms_cnt)

        print("✅ Travellers configured:", adult_cnt, "adults,", children_cnt, "children,", rooms_cnt, "rooms.")
        
    def select_search(self) :
        search_button = self.find_element(
            By.CSS_SELECTOR, "button[type='submit']"
        )
        search_button.click()
        
    def apply_filtrations(self):
        filtration = BookingFiltration(driver=self)
        filtration.apply_star_rating(4, 5)

        filtration.sort_price_lowest_first()
        
    def report_results(self):
        hotel_boxes = self.find_element_by_id(
            'hotellist_inner'
        )

        report = BookingReport(hotel_boxes)
        report.pull_titles()
        
    
    
   
import os
import time
import openpyxl
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class ScrapperContext:
    def __init__(self, controller: object, category:str, output_file:str = "company.xlsx"):
        self.controller = controller
        self.required_category = category
        self.excel_file = output_file
        self.driver = setup_driver()
        self.workbook = setup_excel_workbook(self)
        self.page_count = request_page_count(self)

    def close(self):
        self.driver.quit()
        self.workbook.save(self.excel_file)
        self.context.workbook.close()


def setup_driver():
    """Sets up and returns a Selenium WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode no-graphics
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def setup_excel_workbook(context: ScrapperContext):
    """Loads an existing Excel file or creates a new one if missing."""
    if os.path.exists(context.excel_file):
        return openpyxl.load_workbook(context.excel_file)
    workbook = openpyxl.Workbook()
    workbook.active.append(["ID", "Company Name", "Domain", "Score", "Location", "Address", "Phone", "Email", "Website"])
    workbook.save(context.excel_file)
    return workbook

def request_page_count(context: ScrapperContext):
    if context.driver:
        context.driver.get(f"https://trustpilot.com/categories/{context.required_category}")
    else:
        raise ValueError("There is no driver setup in ScrapperContext context")
    
    try:
        WebDriverWait(context.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "onetrust-close-btn-handler"))
        ).click()
    except:
        pass  # Ignore if button is not found
    
    try:
        last_page = int(WebDriverWait(context.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//a[@data-pagination-button-last-link='true']"))
        ).text)
    except:
        last_page = 1  # Assume 1 page if pagination is missing

        return last_page

def scrape_info(soup, sheet, start_row):
    """Extracts business data from the page and writes it to an Excel sheet."""
    business_links = soup.find_all("a", {"name": "business-unit-card"})
    
    # Retrieve Basic Company Data
    for link in business_links:
        try:
            company_name = link.find("p", class_="CDS_Typography_appearance-default__bedfe1").text.strip()
        except AttributeError:
            company_name = "Unknown"
        
        try:
            company_score = link.find("p", class_="styles_ratingText__A2dmB").text.strip()
        except AttributeError:
            company_score = "TrustScore 0 | 0 reviews"
        
        try:
            company_location = link.find("span", class_="styles_location__wea8G").text.strip()
        except AttributeError:
            company_location = "Unknown"
        
        # Contruct Business Link
        href = link.get("href", "")
        company_domain = href.replace("/review/", "")
        business_url = f"https://trustpilot.com{href}"
        
        # Access business link
        print(f"Processing {business_url}...")
        time.sleep(2)
        response = requests.get(business_url)
        
        # Find contact section and extract details
        if response.status_code == 200:
            soup_sub = BeautifulSoup(response.text, "html.parser")
            contact_details = ["Unknown", "Unknown", "Unknown", "Unknown"] # Address, Phone, Email, Site
            try:
                contact_section = soup_sub.find("ul", class_="styles_itemsColumn__qKHcq")
                contacts = contact_section.find_all("li", class_="styles_itemRow__0RLiS")
                # Extract each contact detail (address, phone, email, site)
                detail = None
                for contact in contacts:
                    if (detail := contact.find("p")) != None:
                        contact_details[0]  = detail.text
                    elif (detail := contact.find("a")) != None:
                        if "tel" in detail["href"]: # Phone
                            contact_details[1] = detail.text
                        elif "mailto" in detail["href"]: # Email
                            contact_details[2] = detail.text
                        elif "http" in detail["href"]: # Site
                            contact_details[3] = detail.text
                
            except AttributeError:
                print(f"Processing Failed")
        else:
            print(f"Failed request for: {business_url}")
            contact_details = ["Unknown", "Unknown", "Unknown", "Unknown"]

        # TODO Extract review comments and store in database
        
        sheet.append([start_row - 1, company_name, company_domain, company_score, company_location] + contact_details)
        start_row += 1

def process_request(context: ScrapperContext):
    """Controls the scraping process, handling navigation and data extraction."""
    page_count = context.page_count
    sheet = context.workbook.active


    for idx in range(page_count):
        # Parse page of businesses
        print(f"Scraping page {idx + 1}...")
        soup = BeautifulSoup(context.driver.page_source, "html.parser")
        scrape_info(soup, sheet, start_row=idx * 20 + 2)
        
        # Click next page
        if idx < page_count - 1:
            try:
                next_button = WebDriverWait(context.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@data-pagination-button-next-link='true']"))
                )
                context.driver.execute_script("arguments[0].click();", next_button)
                time.sleep(3)
            except:
                break

def main():
    process_request()
    print("Scraping completed successfully.")

if __name__ == "__main__":
    main()



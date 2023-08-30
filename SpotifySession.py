from selenium import webdriver
from typing import Tuple,Literal
from string import ascii_lowercase,digits,ascii_letters
from random import choice,randint
from time import sleep
import pickle
import tldextract

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

class SpotifySession:
    def __init__(self,cookies_fp:str | None = None):
        self.driver = uc.Chrome(headless=False,use_subprocess=False)
        self.driver.implicitly_wait(5)

        self.cookies_fp = cookies_fp

        if self.cookies_fp:
            self.load_cookies_for_site("https://spotify.com")

    def reset_driver(self):
        if self.driver:
            self.driver.quit()
        
        self.driver = uc.Chrome(headless=False,use_subprocess=False)


    def set_cookie_filepath(self,fp:str):
        self.cookies_fp = fp


    def load_cookies_for_site(self,site_url:str) -> bool:
        if not self.cookies_fp:
            #no cookies path loaded
            return False
        
        subdomain,domain,suffix = tldextract.extract(site_url)
        
        valid_cookie_domains = []
        if subdomain != "":
            valid_cookie_domains.append(f"{subdomain}.{domain}.{suffix}")
        
        valid_cookie_domains.append(f".{domain}.{suffix}")
        valid_cookie_domains.append(f"{domain}.{suffix}")

        cookies = pickle.load(open((self.cookies_fp),"rb"))
        target_cookies = list(filter(lambda cookie: cookie["domain"] in valid_cookie_domains,cookies))

        failed = 0

        if len(target_cookies) != 0:
            #only force driver to fetch site if any cookies are present to be added.
            self.driver.get(site_url)

        for cookie in target_cookies:
            try:
                self.driver.add_cookie(cookie)
            except:
                failed += 1
        
        print(f"loaded {len(target_cookies) - failed}/{len(target_cookies)} cookies for {site_url}")
        

    def clear_cookies(self):
        self.driver.delete_all_cookies()
    
    def save_cookies(self,cookie_fp:str):
        pickle.dump(self.driver.get_cookies(),open(cookie_fp,"wb"))
    
    def spotify_is_logged_in(self) -> bool:
        logged_in_endpoint = "https://www.spotify.com/uk/account/overview/"

        self.driver.get(logged_in_endpoint)
        wait = WebDriverWait(self.driver,3)
        try:
            wait.until(EC.url_changes(logged_in_endpoint))
            #url changed (redirect occured because user is not logged in.)
            return False
        except:
            return True

    def spotify_account_is_premium(self) -> bool:
        premium_endpoint = "https://www.spotify.com/uk/account/cancel/"

        self.driver.get(premium_endpoint)
        
        try:
            WebDriverWait(self.driver,timeout=5).until(
                EC.url_changes(premium_endpoint)
            )
            return False
        except:
            return True
        

    def spotify_has_cancelled_premium(self) -> bool:
        self.driver.get("https://www.spotify.com/uk/account/overview/")

        try:
            WebDriverWait(self.driver,timeout=5).until(
                EC.presence_of_element_located(By.XPATH,"//button[@data-testid='resubscription-renew-premium']")
            )
            return True
        except:
            return False

        

    def spotify_fetch_user_details(self) -> Tuple[str,str]:
        self.driver.get("https://www.spotify.com/uk/account/overview/")
        
        username = self.driver.find_element(By.XPATH,"//td[text()='Username']/parent::tr/td[not(text() = 'Username')]").text
        email = self.driver.find_element(By.XPATH,"//td[text()='Email']/parent::tr/td[not(text() = 'Email')]").text

        return (email,username)

    def spotify_accept_cookies_popup(self) -> bool:
        if self.driver.get_cookie("eupubconsent-v2"):
            #cookies already accepted
            return False

        sleep(3) #wait a few seconds for fade in animation so consent button becomes clickable
        self.driver.find_element(By.ID,"onetrust-accept-btn-handler").click()

        return True


    def spotify_cancel_premium_plan(self) -> bool:
        if not self.spotify_account_is_premium():
            return False

        self.driver.get("https://www.spotify.com/uk/account/cancel/#benefits")

        elem_confirm_cancel_button = self.driver.find_element(By.XPATH,"//button[@data-testid='submit-button']")
        elem_confirm_cancel_button.click()

        return True

        
    def spotify_premium_plan_signup(self,
        plan_url:str,
        cardnumber:int,
        exp_month:int,
        exp_year:int,
        cvv:int,
    ) -> bool:
        if not self.spotify_is_logged_in() or self.spotify_account_is_premium():
            return False
        
        #load promotion url
        self.driver.get(plan_url)

        #select pay-by-card option
        elem_debitcard_option_selection = self.driver.find_element(By.XPATH,"//a[@role='option'][@data-value='cards']")
        elem_debitcard_option_selection.click()

        #the card-info input elements are contained within an iframe. Therefore, before interaction - we must switch to said iframe.
        
        WebDriverWait(self.driver,timeout=30).until(
            EC.element_to_be_clickable((By.XPATH,"//iframe[@title='Card form']")),
            "failed to locate card input form iframe"
        )

        
        self.driver.switch_to.frame(0) #THIS WILL BREAK IF ANOTHER IFRAME IS ADDED TO PAGE. (try to find how to select iframe by means other than index on page)


        #card number
        elem_debitcard_cardnumber_input = self.driver.find_element(By.ID,"cardnumber")
        elem_debitcard_cardnumber_input.click()
        elem_debitcard_cardnumber_input.send_keys(cardnumber)

        #expirey month/year (auto targets field on card input completion)
        actions = ActionChains(self.driver)

        actions.send_keys(exp_month)
        actions.send_keys(exp_year)

        actions.perform()
        sleep(1)

        #cvv
        elem_cvv_input = self.driver.find_element(By.ID,"security-code")
        elem_cvv_input.click()
        elem_cvv_input.send_keys(cvv)


        #revert back to primary window
        self.driver.switch_to.default_content()

        #buy now button
        elem_buynow_button = self.driver.find_element(By.ID,"checkout_submit")
        elem_buynow_button.click()



        #wait for 3DS

        try:
            WebDriverWait(self.driver,timeout=20).until(
                EC.visibility_of_element_located((By.XPATH,"//div[@data-testid='modal-container']"))
            )
            print("3DS detected. Confirm manually.")
        except:
            print("No 3DS?")


        #3DS has been accepted, await success page redirect
        try:
            WebDriverWait(self.driver,timeout=45).until(
                EC.url_contains("https://www.spotify.com/uk/purchase/success"), #"https://www.spotify.com/uk/purchase/success"
                "timed-out waiting for premium plan signup success page"
            )
            return True
        except:
            return False


    def spotify_signup(self,
        email:str | None = None,
        password:str | None = None,
        gender:Literal["male","female"] | None = None,
        birth_year:int | None = None,
        birth_month:int | None = None,
        birth_day:int | None = None,
    ) -> Tuple[bool,str,str]:
        if not email:
            email = self._gen_email()
        if not password:
            password = self._gen_password()
        if not gender:
            gender = self._gen_gender()
        if not birth_day:
            birth_day = self._gen_birth_day()
        if not birth_month:
            birth_month = self._gen_birth_month()
        if not birth_year:
            birth_year = self._gen_birth_year()

        displayname = ''.join(choice(ascii_lowercase) for _ in range(0,randint(7,10)))

        signup_url = "https://www.spotify.com/uk/signup"

        self.driver.get(signup_url)

        self.spotify_accept_cookies_popup()

        ## email
        elem_email = self.driver.find_element(By.ID,"email")
        elem_email.click()
        elem_email.send_keys(email)

        ## password
        elem_pass = self.driver.find_element(By.ID,"password")
        elem_pass.click()
        elem_pass.send_keys(password)

        ## displayname
        elem_disp_name = self.driver.find_element(By.ID,"displayname")
        elem_disp_name.click()
        elem_disp_name.send_keys(displayname)

        ## day
        elem_birth_day = self.driver.find_element(By.ID,"day")
        elem_birth_day.click()
        elem_birth_day.send_keys(birth_day)

        ## month
        elem_birth_month_dropdown = self.driver.find_element(By.ID,"month")
        elem_birth_month_dropdown.click()

        elem_birth_month_option = self.driver.find_element(By.XPATH,f"//select[@id='month']/option[@value='{birth_month:02}']")
        elem_birth_month_option.click()

        ## year
        elem_birth_year = self.driver.find_element(By.ID,"year")
        elem_birth_year.click()
        elem_birth_year.send_keys(birth_year)


        #gender
        # elem_gender_radio_button = self.driver.find_element(By.XPATH,"//span[@data-encore-id='type'][text()='Male']")
        elem_gender_radio_button = self.driver.find_element(By.XPATH,"//label[@for='gender_option_male']")
        elem_gender_radio_button.click()

        #submit button
        elem_signup_button = self.driver.find_element(By.XPATH,"//button[@type='submit']")
        elem_signup_button.click()

        try:
            WebDriverWait(self.driver,timeout=15).until(
                EC.url_changes(signup_url)
            )
        except:
            pass


        
        if self.spotify_is_logged_in():
            return (True,email,password)
        else:
            return (False,"","")
        

    def _gen_email(self,domain:str | None = None) -> str:
        domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'hotmail.co.uk', 'outlook.com']
        if domain != None:
            domains = [domain]

        return f"{''.join(choice(ascii_lowercase + digits) for _ in range(randint(7,10)))}@{choice(domains)}"
    
    def _gen_password(self) -> str:
        return ''.join(choice(ascii_letters + digits) for _ in range(10))

    def _gen_birth_day(self) -> int:
        return randint(1,28)
    
    def _gen_birth_month(self) -> int:
        return randint(1,12)
    
    def _gen_birth_year(self) -> int:
        return randint(1980,2005)

    def _gen_gender(self) -> str:
        return choice(["male","female"])


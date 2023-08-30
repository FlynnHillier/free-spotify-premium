from SpotifySession import SpotifySession

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from time import sleep


class SpotifyDeveloperSession(SpotifySession):
    def __init__(self, cookies_fp: str | None = None):
        super().__init__(cookies_fp)


    def get_dashboard_ids(self) -> list[str]:
        if self.spotify_is_logged_in() == False:
            return []
        
        self.driver.get("https://developer.spotify.com/dashboard")
        links_to_dashboards = self.driver.find_elements(By.XPATH,"//a[starts-with(@href,'/dashboard/')][@href!='/dashboard/create']")

        dashboard_ids : list[str] = []

        for e in links_to_dashboards:
            link = e.get_attribute("href")
            id = link.split("/")[-1]
            dashboard_ids.append(id)

        return dashboard_ids



    def navigate_to_dashboard_users(self,dashboard_id: str | None = None):
        if dashboard_id == None:
            #fix - will error if no dashboards present
            dashboard_id = self.get_dashboard_ids()[0]

        self.driver.get(f"https://developer.spotify.com/dashboard/{dashboard_id}/users")


    def delete_all_dashboard_users(self,dashboard_id: str | None = None):
        self.navigate_to_dashboard_users(dashboard_id)

        user_options_buttons = self.driver.find_elements(By.XPATH,"//tbody/button[@aria-label='User options']")

        for user_option_button in user_options_buttons:
            user_option_button.click()

            remove_user_button = self.driver.find_element(By.XPATH("//span[text() = 'Remove User']/parent::button"))
            remove_user_button.click()

    

    def add_dashboard_user(self,email:str,name:str | None = None,dashboard_id:str | None = None):
        self.navigate_to_dashboard_users(dashboard_id)

        elem_name_input = self.driver.find_element(By.ID,"name")
        elem_name_input.click()
        elem_name_input.send_keys(name or "AAAA")

        elem_email_input = self.driver.find_element(By.ID,"email")
        elem_email_input.click()
        elem_email_input.send_keys(email)


        elem_add_user_submit_button = self.driver.find_element(By.XPATH,"//button[@type='submit']")
        elem_add_user_submit_button.click()

        sleep(2)
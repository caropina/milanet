import pickle
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import re
import time
import os
from Models.PostOffice import PostOffice


class PostScraper:

    """
        PostScraper constructor.

        Input:
            - timeout: the default timeout for the html elements retrieve

        Initializes:
            - default_url: the default url of Poste Italiane web page for post offices search
            - timeout: the default timeout for the html elements retrieve
            - driver: the selenium driver used to manipulate the browser
    """
    def __init__(self, timeout):
        self.default_url = "https://www.poste.it/cerca/index.html#/vieni-in-poste/"
        self.timeout = timeout

        service = Service()
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(service=service, options=options)

    """
        Updates the Scraper's extracted body element from the Chrome driver.
        
        Returns:
            - the body of the page stored in the driver
    """
    def __updated_extracted_body(self):
        expectation = ec.presence_of_element_located((By.XPATH, '//body'))
        element = WebDriverWait(self.driver, self.timeout).until(expectation)
        self.extracted_body_element = element.get_attribute('innerHTML')
        return self.extracted_body_element

    """
        Performs a click on an element.
        
        Input:
            - xpath: html path to the element to be clicked

        Returns:
            - the updated body of the url stored in the driver
    """
    def __click(self, xpath):
        WebDriverWait(self.driver, self.timeout).until(ec.element_to_be_clickable((By.XPATH, xpath))).click()
        return

    """
        Fills the post offices search field.
    
        Parameters:
            - the post_offices_search_query: the query to search for the post offices

        Returns:
            - the updated body of the url stored in the driver
    """
    def __fill_search_field(self, post_offices_search_query):
        try:
            # retrieve the html search field
            WebDriverWait(self.driver, self.timeout).until(ec.element_to_be_clickable((By.XPATH, '//*[@id="cerca-up-autocomplete-input"]')))
            search_element = self.driver.find_element(By.XPATH, '//*[@id="cerca-up-autocomplete-input"]')

            # clear the search field
            search_element.send_keys(Keys.CONTROL + "a" + Keys.DELETE)

            # fill the field and perform the search
            search_element.send_keys(post_offices_search_query)
            search_element.send_keys(Keys.ENTER)
            search_element.send_keys(Keys.ENTER)

            return self.__updated_extracted_body()

        except:
            print("Error executing __fill_search_field")
            return
    """
        Updates the page by closing the cookie banner.

        Returns:
            - the updated body of the url stored in the driver
    """
    def __close_cookie_banner(self):
        try:
            self.__click('//*[@id="truste-consent-required"]/img')
            return self.__updated_extracted_body()
        except:
            print("Error executing __close_cookie_banner")
            return
    """
        Updates the page by selecting all possible post types.

        Returns:
            - the updated body of the url stored in the driver
    """
    def __filter_point_type(self):
        try:
            self.__click('//*[@id="filtriUP"]/div[1]/div[1]/div[3]/div[1]/a')

            self.__updated_extracted_body()

            self.__click('//*[@id="collapseDesktop-04"]/ng-include/div/div[2]/label/span')
            self.__click('//*[@id="collapseDesktop-04"]/ng-include/div/div[3]/label/span')
            return self.__updated_extracted_body()
        except:
            print("Error executing __filter_point_type")
            return

    """
        Move the kilometer range slider that regulates the radius of search for post offices.
        
        Returns:
            - the updated body of the url stored in the driver
    """
    def __move_range_slider(self):
        slider = self.driver.find_element(By.CSS_SELECTOR, "#collapseDesktop-01 > ng-include > div > p > span > span.irs-slider.single")
        move = ActionChains(self.driver)
        move.click_and_hold(slider).move_by_offset(130, 0).release().perform()
        self.__updated_extracted_body()

    """
        Scrolls down the page until all post offices are loaded.
    
        Returns:
            - the updated body of the url stored in the driver
    """
    def __scroll_page(self):
        while True:
            try:
                next_link = WebDriverWait(self.driver, self.timeout).until(ec.element_to_be_clickable((By.XPATH, '//*[@id="filtriUP"]/div[2]/div/show-more/div/div/a')))
                next_link.click()
            except TimeoutException:
                break
        return self.__updated_extracted_body()

    """
        Extracts the services offered by the post office.
        
        Parameters:
            - position: index of the post office to scrape services from
            
        Returns:
            - an array of services
    """
    def __extract_services(self, position):
        try:
            button = f'/html/body/div[6]/ng-include[1]/div/div/div[2]/div/div[2]/div/div[3]/div/div[{position + 1}]/div/div/div[2]/div/div[3]/ul/li[10]/a'
            WebDriverWait(self.driver, self.timeout).until(ec.element_to_be_clickable((By.XPATH, button))).click()

            self.__updated_extracted_body()

            # extract services from the post office
            post_services = re.findall(r'serviziCompleti" class="ng-binding ng-scope">([A-Za-z0-9\s]*)</li>', self.extracted_body_element)

            return post_services

        except:
            print("Error executing __extract_services")
            return []

    """
        Extracts information (features) about the post office.
        The extracted features are:
            - nome
            - tipo_punto
            - indirizzo
            - telefono
            - fax
            
        Parameters:
            - post_office: post office where to add the features
            - extracted_post_frame: extracted html element corresponding to the post office frame 
        
        Returns:
            - an array of features
    """
    def __extract_features(self, post_office: PostOffice, extracted_post_frame):
        features = [
            'nome',
            'tipo_punto',
            'indirizzo',
            'telefono',
            'fax'
        ]
        patterns = [
            r'class="ng-binding">(.*)</h4>',
            r'<span class="panel-heading-subtitle ng-binding">(.*)</span>',
            r'<li ng-class="{\'text-disabled\': e.ufficioAppoggio}" class="ng-binding">(.*)</li>\n<li ng-class="{\'text-disabled\': e.ufficioAppoggio}" class="ng-binding">(.*)</li>',
            r'<li style="margin-top:15px" ng-show="e.numeroTelefono &amp;&amp; !e.ufficioAppoggio" class="ng-binding">Telefono: (.*)</li>',
            r'<li ng-show="e.fax &amp;&amp; !e.ufficioAppoggio" class="ng-binding">Fax: (.*)</li>'
        ]

        j = 0
        while j < len(features):
            try:
                element = re.findall(patterns[j], extracted_post_frame)

                if (features[j] == 'telefono' and element[0] == "000000000") or (len(element) == 0):
                    element = None
            except:
                print("Error executing __extract_features")
                element = None

            if element is not None:
                if features[j] == 'indirizzo':
                    post_office.indirizzo, post_office.citta = element[0][0], element[0][1]
                else:
                    setattr(post_office, features[j], element[0])

            j += 1

    """
        Extracts opening hours information (timetable) from the post office.

        Returns:
            - a dictionary containing the timetable 
    """
    def __extract_timetable(self):
        timetable: dict = {
            'lunedì': 'CHIUSO',
            'martedì': 'CHIUSO',
            'mercoledì': 'CHIUSO',
            'giovedì': 'CHIUSO',
            'venerdì': 'CHIUSO',
            'sabato': 'CHIUSO',
            'domenica': 'CHIUSO'
        }

        try:
            # click on the timetable
            button2 = '//*[@id="upDetailModal"]/div/div/div[2]/div/div/div[1]/ul/li[2]/a'
            WebDriverWait(self.driver, self.timeout).until(ec.element_to_be_clickable((By.XPATH, button2))).click()

            self.__updated_extracted_body()

            # extract timetable
            schedule = re.findall(r'<td class="vam .*" style="width:34%" ng-.*="orario.orario == \'CHIUSO\'">([^-].*)</td>',
                self.extracted_body_element)

            count = 0
            for k in timetable:
                if count == len(schedule):
                    break

                timetable[k] = schedule[count]
                count += 1

            # close the previously opened timetable window
            WebDriverWait(self.driver, self.timeout).until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'span.close-icon'))).click()
            return timetable

        except:
            print("Error executing __extract_timetable")
            return timetable

    """
        Extracts different kind of data concerning the post office.
        The returned data contains:
            - features
            - services
            - timetable

        Parameters:
            - post_offices_counter: total numer of post offices
    
        Returns:
            - an array of data for each post office
    """
    def __extract_post_data(self, post_offices_counter):
        i = 0
        post_offices = []

        while i < post_offices_counter:
            post_office = PostOffice()

            expectation = ec.presence_of_element_located((By.XPATH, f'//*[@id="filtriUP"]/div[2]/div/div[3]/div/div[{i + 1}]/div/div'))
            element = WebDriverWait(self.driver, self.timeout).until(expectation)
            extracted_post_frame = element.get_attribute('innerHTML')

            self.__extract_features(post_office, extracted_post_frame)
            post_office.servizi = self.__extract_services(i)
            post_office.orari = self.__extract_timetable()

            if 'Milano (MI)' in post_office.citta:
                post_offices.append(post_office)
            i += 1

        return post_offices

    """
        Scrapes post offices information from the Poste Italiane website

        Parameters:
            - post_offices_search_queries: query for the post offices location search
        
        Returns:
            - an array of post offices
    """
    def __remove_duplicates(self, post_offices):
        result = []
        seen_names = set()

        for post_office in post_offices:
            if post_office.nome not in seen_names:
                result.append(post_office)
                seen_names.add(post_office.nome)

        return result

    def scrape_post_offices(self, post_offices_search_queries):

        # get the Poste Italiane web page
        self.driver.get(self.default_url)

        post_offices = []

        # wait for the page to fully load
        time.sleep(self.timeout)
        self.__close_cookie_banner()
        self.__filter_point_type()

        for post_offices_search_query in post_offices_search_queries:
            self.__fill_search_field(post_offices_search_query)
            time.sleep(self.timeout)

            # initialize the driver's body reference
            self.__updated_extracted_body()

            self.__move_range_slider()

            # extracts the number of results
            post_offices_counter = int(re.findall(r'<span class="ng-binding">([0-9]*) risultati</span>', self.extracted_body_element)[0])

            self.__scroll_page()

            query_post_offices = self.__extract_post_data(post_offices_counter)

            post_offices += query_post_offices

        post_offices = self.__remove_duplicates(post_offices)

        with open("post_offices.pkl", 'wb') as fp:
            pickle.dump(post_offices, fp)
            print('saved successfully to file post_offices.pkl')

        return post_offices
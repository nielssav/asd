from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.firefox.options import Options
import unittest, time, re
import json
import pandas

class Airbnb(unittest.TestCase):
    def setUp(self):
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(executable_path=f"C:\Drivers\geckodriver.exe", options=options)
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
        self.f = open("json/myairbnb.json")
        self.f_json = json.load(self.f)
        self.f_data = open("results.json", 'w+')
        self.dict_csv = {"link":[], "host":[], "unit_price":[], "type":[]}
        self.f_data.write('[')
    
    def export_infos(self, link):
        driver = self.driver
        driver.get(link)
        line = driver.find_element_by_class_name('_xcsyj0').text
        host = line[line.index("Hôte : ")+len("Hôte : "):len(line)]
        type = line[0:line.index(" Hôte : ")]
        print(type)
        unit_price = driver.find_element_by_class_name('_me8w3a0').text
        print("unit price is " + unit_price)
        infos_json = {"link":link, "host":host, "unit_price":unit_price, "type":type}
        self.dict_csv['link'].append(link)
        self.dict_csv['host'].append(host)
        self.dict_csv['unit_price'].append(unit_price)
        self.dict_csv['type'].append(type)
        json.dump(infos_json, self.f_data, indent=2)

    def test_airbnb(self):
        driver = self.driver
        for i in self.f_json:
            page=driver.get("https://www.airbnb.fr/s/"+i['location']+"/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_dates%5B%5D=july&flexible_trip_dates%5B%5D=june&flexible_trip_lengths%5B%5D=weekend_trip&date_picker_type=calendar&checkin="+i['checkin']+"&checkout="+i['checkout']+"&adults="+i['nb_adults']+"&place_id=ChIJD7fiBh9u5kcRYJSMaMOCCwQ&query="+i['location']+"&disable_auto_translation=false&source=structured_search_input_header&search_type=autocomplete_click")
            self.driver.implicitly_wait(5)
            page_source = page.page_source
            elem = driver.find_elements_by_class_name("_8ssblpx")
            lowest = 0
            lowest_el = elem[0]
            for j in elem:
                price = j.find_element_by_xpath(".//span[contains(text(), 'au total')]")
                j_txt = price.text.replace("€ au total", '')
                j_txt = j_txt.replace(" ", "")
                if int(j_txt) < lowest or lowest == 0:
                    lowest = int(j_txt)
                    lowest_el = j
            print("price is " + str(lowest)+"€ for "+ i['nb_adults']+" at "+i['location'])
            link = lowest_el.find_element_by_class_name("_mm360j").get_attribute("href")
            print("Here is the link : " + link)
            self.export_infos(link)
            if i != self.f_json[len(self.f_json) - 1]:
                self.f_data.write(',')
            print('')

    def print_lenght(self):
        print('link list lenght : ' + str(len(self.dict_csv['link'])))
        print('host list lenght : ' + str(len(self.dict_csv['host'])))
        print('unit_price list lenght : ' + str(len(self.dict_csv['unit_price'])))
        print('type list lenght : ' + str(len(self.dict_csv['type'])))

    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        infos_csv = pandas.DataFrame(self.dict_csv)
        infos_csv.to_csv('test.csv')
        self.f_data.write(']')
        self.f.close()
        self.f_data.close()
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
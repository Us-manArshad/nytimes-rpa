import datetime
import os
import re
from urllib.parse import urlparse

from RPA.Excel.Files import Files
from RPA.HTTP import HTTP
from SeleniumLibrary.errors import ElementNotFound
from dateutil.relativedelta import relativedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from base_bot import BaseBot, ActionConfig, StepConfig, BotBrowser, ElementCallableConfig
from config import SEARCH_TEXT, SECTIONS, MONTHS, URL, DOWNLOAD_IMAGES_PATH, EXCEL_FILE

params = {
    'search_text': SEARCH_TEXT,
    'sections': SECTIONS,
    'months': MONTHS
}
if not os.path.exists(DOWNLOAD_IMAGES_PATH):
    os.mkdir(DOWNLOAD_IMAGES_PATH)


class NewsBot(BaseBot):
    browser = BotBrowser(url=URL).open()
    files = Files()
    http = HTTP()

    actions_config = [
        ActionConfig(
            action_name='apply_search',
            steps_config=[
                StepConfig(browser.click_button, xpath_name='search_button'),
                StepConfig(browser.input_text, xpath_name='search_input', kwargs={'text': SEARCH_TEXT}),
                StepConfig(browser.click_button, xpath_name='search_submit')
            ]
        ),
        ActionConfig(
            action_name='select_sections',
            steps_config=[
                StepConfig(browser.wait_until_page_contains_element, xpath_name='section_dropdown_btn'),
                StepConfig(
                    browser.find_element,
                    xpath_name='section_dropdown_btn',
                    callable_on_element=ElementCallableConfig(callable_type=WebElement.click)
                ),
                StepConfig(browser.find_elements, xpath_name='section_dropdown_options', post_conditions=True),
                StepConfig(browser.select_from_list_by_value, xpath_name='search_sort_by', args=['newest'])
            ]
        ),
        ActionConfig(
            action_name='apply_date_range',
            steps_config=[
                StepConfig(browser.click_button, xpath_name='date_range_dropdown_btn'),
                StepConfig(browser.click_button, xpath_name='specific_date_btn'),
                StepConfig(browser.input_text, xpath_name='start_date_input', pre_conditions=True),
                StepConfig(browser.input_text, xpath_name='end_date_input', pre_conditions=True),
                StepConfig(browser.press_keys, xpath_name='end_date_input', args=['RETURN'])
            ]
        )
    ]

    def __init__(self, *args, **kwargs):
        """
        Initialize the News bot with required params
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.extra_logic_methods: dict = {
            'section_dropdown_options': self._select_sections,
            'start_date_input': self._get_date_range,
            'end_date_input': self._get_date_range
        }

    @property
    def search_text(self) -> str:
        """
        It will return search text from params which would be defined in config.
        :return:
        """
        return self.params.get('search_text', '')

    @property
    def months(self) -> int:
        """
        It will return month from params which would be defined in config.
        :return:
        """
        return self.params.get('months', 0)

    @property
    def sections(self) -> list[str]:
        """
        It will return list of sections from params which would be defined in config.
        :return:
        """
        return self.params.get('sections', [])

    def click_show_more_button(self):
        """
        click on show more button until page contains
        :return:
        """
        while True:
            show_more_btn = self.browser.does_page_contain_button(self.xpath_mapper.get('show_more_btn'))
            if show_more_btn is None or show_more_btn is False:
                break
            else:
                try:
                    self.browser.scroll_element_into_view(self.xpath_mapper.get('show_more_btn'))
                    self.browser.find_element(self.xpath_mapper.get('show_more_btn')).click()
                except ElementNotFound:
                    pass

    @staticmethod
    def _check_amount(text: str):
        """
        Search dollar amounts from text
        :param text:
        :return:
        """
        return re.search(r'(\$[\d,]+\.\d{1,2}\b|\d+\sdollars|\d+\sUSD)', text)

    def scrap_data(self):
        """
        Scrap data by applying searches
        :return:
        """
        self.click_show_more_button()

        for element in self.browser.find_elements(self.xpath_mapper.get('search_results')):
            img_link = element.find_element(By.TAG_NAME, 'img')
            image_name = urlparse(img_link.get_attribute('src')).path.split('/')[-1]

            self.http.download(img_link.get_attribute('src'), target_file=DOWNLOAD_IMAGES_PATH)
            title = element.find_element(By.TAG_NAME, 'h4').text
            description = element.find_elements(By.TAG_NAME, 'p')[1].text

            self.data.add(
                tuple(
                    {
                        'title': title,
                        'description': description,
                        'date': element.find_element(By.TAG_NAME, 'span').text,
                        'picture_name': f'{DOWNLOAD_IMAGES_PATH}/{image_name}',
                        'search_phrase_in_title': title.count(self.search_text),
                        'search_phrase_in_description': description.count(self.search_text),
                        'is_contains_amount': any([self._check_amount(title), self._check_amount(description)])
                    }.items()
                )
            )

    def _select_sections(self, options: list[WebElement]):
        """
        apply select sections according to config.ppy
        :param options:
        :return:
        """
        for option in options:
            section = option.get_attribute('value').split('|')[0]
            if section in self.sections:
                self.browser.select_checkbox(option)

    def _get_date_range(self, xpath_name: str) -> dict:
        """
        apply date range
        :param xpath_name:
        :return:
        """
        current_date = datetime.date.today()
        end_date = current_date.strftime("%m/%d/%Y")

        start_date = (current_date - relativedelta(months=self.months - 1)).strftime("%m/%d/%Y")
        if self.months < 2:
            start_date = current_date.replace(day=1).strftime("%m/%d/%Y")
            end_date = start_date
        date = {
            'text': start_date
            if xpath_name == 'start_date_input'
            else end_date
        }
        return date

    def take_actions(self, step: StepConfig, action: ActionConfig):
        if step.pre_conditions and step.xpath_name in ['start_date_input', 'end_date_input']:
            step.kwargs = self.get_extra_logic_method(xpath_name=step.xpath_name)(xpath_name=step.xpath_name)

        element = step.apply_step(self.get_xpath(step.xpath_name))

        if step.post_conditions and step.xpath_name == 'section_dropdown_options':
            self.get_extra_logic_method(xpath_name=step.xpath_name)(options=element)

    def start_process(self):
        """
        It will search and write the data in excel file in output folder
        :return:
        """
        data = list(bot.get_data())
        table_data = {
            "title": [],
            "description": [],
            "date": [],
            "picture_name": [],
            "search_phrase_in_title": [],
            "search_phrase_in_description": [],
            "is_contains_amount": [],
        }
        for item in data:
            item = dict(item)
            for key, value in item.items():
                table_data[key].append(value)
        w = self.files.create_workbook(EXCEL_FILE)
        w.append_worksheet("Sheet", table_data, header=True, start=1)
        w.save()


if __name__ == '__main__':
    xpaths_mapper = {
        'search_button': '//button[@data-test-id="search-button"]',
        'search_input': '//input[@data-testid="search-input"]',
        'search_submit': '//button[@data-test-id="search-submit"]',
        'section_dropdown_btn': '//button[@data-testid="search-multiselect-button"]/label[text()="Section"]',
        'section_dropdown_options': '//input[@data-testid="DropdownLabelCheckbox"]',
        'search_sort_by': '//select[@data-testid="SearchForm-sortBy"]',
        'search_results': '//ol/li[@data-testid="search-bodega-result"]/div',
        'show_more_btn': '//button[@data-testid="search-show-more-button"]',
        'date_range_dropdown_btn': '//button[@data-testid="search-date-dropdown-a"]',
        'specific_date_btn': '//button[@value="Specific Dates"]',
        'end_date_input': '//input[@id="endDate"]',
        'start_date_input': '//input[@id="startDate"]',
    }
    bot = NewsBot(
        xpaths_mapper=xpaths_mapper,
        params=params,
    )

    bot.start_process()


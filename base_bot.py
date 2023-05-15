import os
from abc import abstractmethod, ABC
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum

from RPA.Browser.Selenium import Selenium
from RPA.HTTP import HTTP

from selenium.webdriver.remote.webelement import WebElement

from config import DOWNLOAD_IMAGES_PATH


@dataclass
class ElementCallableConfig:
    callable_type: callable
    args: list = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)

    def call(self, element):
        self.callable_type(element, *self.args, **self.kwargs)


@dataclass
class BotBrowser:
    url: str

    def open(self):
        """
        Open RPA's selenium browser and return
        :return:
        """
        selenium = Selenium()
        selenium.set_download_directory(DOWNLOAD_IMAGES_PATH)
        selenium.open_available_browser(url=self.url, maximized=True)
        return selenium


@dataclass
class StepConfig:
    browser_action: Callable
    xpath_name: str
    callable_on_element: ElementCallableConfig = None
    post_conditions: bool = False
    pre_conditions: bool = False
    args: list = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)

    def apply_step(self, xpath):
        element = self.browser_action(xpath, *self.args, **self.kwargs)
        if self.callable_on_element and element:
            self.callable_on_element.call(element)
        return element


@dataclass
class ActionConfig:
    action_name: str
    steps_config: list[StepConfig]


class BaseBot(ABC):
    """
    Abstract base class.
    """
    actions_config: list[ActionConfig] = []
    browser: Selenium

    def __init__(self, params: dict, xpaths_mapper: dict):
        """
        Initialize the required params
        :param params:
        :param xpaths_mapper:
        """
        self.params = params
        self.data = set()
        self.xpath_mapper = xpaths_mapper
        self.http = HTTP()
        self.extra_logic_methods: dict = {}

    @abstractmethod
    def scrap_data(self):
        ...

    def get_xpath(self, xpath_name) -> str:
        """
        get actual xpath from xpath_mapper.
        :param xpath_name:
        :return:
        """
        return self.xpath_mapper.get(xpath_name, None)

    def get_data(self) -> set:
        """
        process to start scraping data after applying filter
        :return:
        """
        self.start_actions()
        self.scrap_data()
        return self.data

    def get_extra_logic_method(self, xpath_name):
        if xpath_name in self.extra_logic_methods:
            return self.extra_logic_methods.get(xpath_name)
        raise NotImplementedError

    def take_actions(self, step: StepConfig, action: ActionConfig):
        step.apply_step(self.get_xpath(step.xpath_name))

    def start_actions(self):
        """
        apply filters and searches
        :return:
        """
        for action in self.actions_config:
            for step in action.steps_config:
                if step.pre_conditions or step.post_conditions:
                    self.get_extra_logic_method(xpath_name=step.xpath_name)
                self.take_actions(step=step, action=action)

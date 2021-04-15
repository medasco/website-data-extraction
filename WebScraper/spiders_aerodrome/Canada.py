
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class CanadaSpider(AeroChartSpider):
    """ Canada airport charts spider """
    name = 'Canada'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'http://www.navcanada.ca/en/products-and-services/pages/aeronautical-information-products-canadian-airports-charts.aspx'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)

        # pdf_link = self.browser.find_element_by_xpath('//*[@id="ctl00_PlaceHolderMain_RichHtmlField2__ControlWrapper_RichHtmlField"]/ul/li[1]/div/a[7]')
        pdf_link = self.browser.find_element_by_xpath('//*[@id="ctl00_PlaceHolderMain_RichHtmlField2__ControlWrapper_RichHtmlField"]/ul/li[1]/div/a')

        print('\nExtracting :', self.country_name)

        link = pdf_link.get_attribute('href')
        desc = pdf_link.text
        file = link.split('/')[-1].split('.')[0]

        print('\t   : {} : {}'.format(file, link))

        chart_item = ChartItem()

        chart_item['country'] = self.country_name
        chart_item['icao'] = 'All'
        chart_item['link'] = link
        chart_item['desc'] = desc
        chart_item['file'] = file
        chart_item['club'] = 'Default'

        list_of_charts.append(chart_item)

        # Go to "Part 4 – AIP Canada (ICAO) Supplements" page
        self.click_enable(self.browser.find_element_by_xpath('//a[@id="LogoLinkEN"]'))
        self.click_enable(self.browser.find_element_by_xpath('//li[@id="tab1"]/span/span/a'))
        self.scroll_down_window_height()
        self.click_enable(self.browser.find_element_by_xpath('//a[@title="Aeronautical Information Products"]'))
        self.scroll_down_window_height()
        self.click_enable(self.browser.find_element_by_xpath('//div[@id="ctl00_PlaceHolderMain_RichHtmlField2__ControlWrapper_RichHtmlField"]/div/div[8]/a'))
        self.click_enable(self.browser.find_element_by_xpath('//div[@id="ctl00_PlaceHolderMain_RichHtmlField2__ControlWrapper_RichHtmlField"]/ul/li[1]/div/a'))
        self.click_enable(self.browser.find_element_by_xpath('//div[@id="ctl00_PlaceHolderMain_RichHtmlField2__ControlWrapper_RichHtmlField"]/ul/li[4]/div/a'))

        # Get all SUP table rows
        supplements = self.browser.find_elements_by_xpath('//*[@id="ctl00_PlaceHolderMain_RichHtmlField2__ControlWrapper_RichHtmlField"]/div/div[3]/table/tbody/tr')
        
        # Process data
        for supp in supplements:
            file = ''
            link = ''
            desc = ''
            td_list = supp.find_elements_by_tag_name('td')
            if len(td_list) == 3:
                file = td_list[1].text
                link = td_list[1].find_element_by_tag_name('a').get_attribute('href')
                desc = td_list[2].text
            elif len(td_list) == 2:
                file = td_list[0].text
                link = td_list[0].find_element_by_tag_name('a').get_attribute('href')
                desc = td_list[1].text

            if '(CY' in desc:
                cy_list = desc.split('(CY')
                for cy in cy_list:
                    if cy[2] == ')':
                        icao = 'CY' + cy[:2]
                        break
            else:
                icao = 'SUP'

            chart_item = ChartItem()

            if link != '':
                chart_item['country'] = self.country_name
                chart_item['icao'] = icao
                chart_item['link'] = link
                chart_item['desc'] = desc
                chart_item['file'] = file
                chart_item['club'] = 'Default'

                list_of_charts.append(chart_item)

        self.chart_mgr = CanadaChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)
    
    def scroll_down_window_height(self):
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.browser.wait(2)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class CanadaChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Canada')

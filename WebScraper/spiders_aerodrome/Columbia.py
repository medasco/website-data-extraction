
import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver
from selenium.common.exceptions import NoSuchElementException


class ColumbiaSpider(AeroChartSpider):
    """ Columbia airport charts spider """
    name = 'Columbia'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'https://www.google.com/'
        # self.url = 'http://www.aerocivil.gov.co/servicios-a-la-navegacion/servicio-de-informacion-aeronautica-ais/aerodromos'

    def parse(self, response):
        """ Parsing callback function """

        # Prepare a list of charts (with ChartItem elements) --> [ChartItem_1, ChartItem_2, ...]
        # but will be treated as a normal list of dicts --> [{}, {}, ...]
        list_of_charts = []

        # Start the selenium Chrome driver
        self.browser.get(response.url)
        self.browser.get('http://www.aerocivil.gov.co/servicios-a-la-navegacion/servicio-de-informacion-aeronautica-ais/aerodromos')
        self.browser.wait(3)

        xpath = self.browser.find_elements_by_xpath('//div[@class="buttons"]/a[@class="tool-doc view"]')

        for a in xpath:
            link = a.get_attribute('href')
            title = a.get_attribute('title')
            file = ''.join(title.split(' '))
            icao = title.split(' ')[0]
            pdf = link.rsplit('/', 1)[1].split('.')[0]
            desc = '_'.join(pdf.split('%20'))

            if '_AD_' not in desc:

                chart_item = ChartItem()

                chart_item['country'] = self.country_name
                chart_item['icao'] = icao
                chart_item['link'] = link
                chart_item['file'] = file
                chart_item['desc'] = desc
                chart_item['club'] = 'Default'

                list_of_charts.append(chart_item)

        # Go to SUPP page
        self.click_enable(self.browser.find_element_by_xpath('//div[@id="cbqwpctl00_g_13b5b729_ce34_457f_a20a_7a3fac6e8c82"]/ul/li[1]/a'))
        self.click_enable(self.browser.find_element_by_xpath('//a[@title="Gestión de Información Aeronáutica (AIM)"]'))
        self.click_enable(self.browser.find_element_by_xpath('//a[@title="Suplementos AIP"]'))
        self.browser.wait(2)

        # Get all supplements table rows
        supplements = self.browser.find_elements_by_xpath('//*[@id="ctl00_PlaceHolderMain_ctl03__ControlWrapper_RichHtmlField"]/table/tbody/tr')

        # Process data
        for supp in supplements:
            td_list = supp.find_elements_by_tag_name('td')
            if td_list != []:
                try:
                    link = td_list[3].find_element_by_tag_name('a').get_attribute('href')
                    file = link.split('/')[-1].replace('.pdf', '').replace('%20', '_')
                    desc = file

                    # Desc text container too inconsistent to use this:
                    # span_list = td_list[1].find_elements_by_tag_name('span')
                    # p_list = td_list[1].find_elements_by_tag_name('p')
                    # if span_list != []:
                    #     desc = ' '.join([span.text for span in span_list])
                    # elif p_list != []:
                    #     desc = p_list[0].text
                    # elif p_list == [] and td_list[1].text != '':
                    #     desc = td_list[1].text
                    # else:
                    #     desc = td_list[2].text

                    if 'SK' in desc:
                        index = desc.find('SK')
                        icao = desc[index:index+4]
                    else:
                        icao = 'SUP'

                    chart_item = ChartItem()

                    chart_item['country'] = self.country_name
                    chart_item['icao'] = icao
                    chart_item['link'] = link
                    chart_item['file'] = file
                    chart_item['desc'] = desc
                    chart_item['club'] = 'Default'

                    list_of_charts.append(chart_item)
                except NoSuchElementException:
                    pass

        self.chart_mgr = ColumbiaChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class ColumbiaChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        self.print_chart_list()
        self.save_chart_list('Columbia')

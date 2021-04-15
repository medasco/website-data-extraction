import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver


class UruguaySpider(AeroChartSpider):
    """ Uruguay airport charts spider """
    name = 'Uruguay'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = self.name
        self.url = 'http://www.dinacia.gub.uy/ais/'

    def parse(self, response):

        # initialize lists
        list_of_pdf_Urls = []           # collection of PDF Links
        list_of_desc = []               # collection of Chart Description
        list_of_charts = []             # collection of Chart Items

        # go to main url
        self.browser.get(response.url)

        # get link xpath to AIP Uruguay page and enter
        aip_uruguay = self.browser.find_element_by_xpath('//*[@id="g-navigation"]/div/div/div/div[2]/div/nav/ul/li[3]/ul/li/div/div/ul/li[3]/a').get_attribute('href')
        self.browser.get(aip_uruguay)

        ##
        ##  SUP Section
        ##

        sup_pdf_Urls = self.browser.find_elements_by_xpath('//*[@id="g-utility"]/div/div/div/div/div/div/div/div/div/div[6]/ul/li/a')
        for sup_pdf_Url in sup_pdf_Urls:
            list_of_pdf_Urls.append(sup_pdf_Url.get_attribute('href'))
            
            # re-structure captured SUP description to match AIP default formatting
            sup_description = "SUP - " + sup_pdf_Url.get_attribute('text')
            list_of_desc.append(sup_description)

        ##
        ##  AIP Section
        ##

        # get pdf urls and description of AIP AD2 Charts
        aip_pdf_Urls = self.browser.find_elements_by_xpath('//*[@id="ad2-aerodromes"]/div/ul/li/a')
        for aip_pdf_Url in aip_pdf_Urls:
            list_of_pdf_Urls.append(aip_pdf_Url.get_attribute('href'))
            list_of_desc.append(aip_pdf_Url.get_attribute('text'))

        
        # close browser
        self.browser.close()
        
        # process CSV Information

        for index in range (len(list_of_pdf_Urls)):
            url = list_of_pdf_Urls[index]
            file = url.split('/')[-1].split('.pdf')[0]
            icao = str(list_of_desc[index]).split('-')[0][:-1]      # last bit of string manipulation is for removal of excess spaces
            desc = str(list_of_desc[index]).split('-')[1][1:]       # last bit of string manipulation is for removal of excess spaces

            chart_item = ChartItem()

            if "SUP" == icao:
                cat = "SUP"
            else:
                cat = "AIP-AD"
                
            chart_item['country'] = self.country_name
            chart_item['icao'] = icao
            chart_item['link'] = url
            chart_item['file'] = icao + "_" + file
            chart_item['desc'] = desc
            chart_item['club'] = cat
            chart_item['category'] = "N/A"      # no available effectivity date to parse

            list_of_charts.append(chart_item)

        self.chart_mgr = UruguayChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self


class UruguayChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        # self.print_chart_list()
        self.save_chart_list('Uruguay')
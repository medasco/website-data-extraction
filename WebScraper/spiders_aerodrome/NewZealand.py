import scrapy
from AerodromeChartScraper.psw_spider import AeroChartSpider
from AerodromeChartScraper.items import ChartItem
from AerodromeChartScraper.pipelines import ChartPipeline
from AerodromeChartScraper.web_drivers import ChromeDriver
from selenium import webdriver


class NewZealandSpider(AeroChartSpider):
    """ New Zealand airport charts spider """
    name = 'NewZealand'
    version = '1.0.0'

    def __init__(self):
        super().__init__()
        self.country_name = 'New Zealand'
        self.url = 'http://www.aip.net.nz/Default.aspx'

    def parse(self, response):
        # Initialize lists 
        list_of_charts = []               # collection of all charts to process
        listOfUrlsInAerodromeCharts = []  # list of AIP Charts
        listOfPdfUrls = []                # list of AIP pdf url

        # go to main url
        urlMain = self.browser.get(response.url)

        # hit "I Agree" button
        self.click_enable(self.browser.find_element_by_xpath('//*[@id="btnAgree"]'))
        self.browser.get('http://www.aip.net.nz/Home.aspx')

        # get Supplement Charts url
        urlSupplementCharts = self.browser.find_elements_by_xpath('//*[@id="Form1"]/table[2]/tbody/tr[2]/td[2]/div/div/a')

        # get Aerodrome Charts url
        urlAerodromeCharts = self.browser.find_element_by_xpath('//*[@id="Form1"]/table[2]/tbody/tr[2]/td[1]/div/h3[5]/a').get_attribute('href')

        ##
        ## SUP Section
        ##

        # parse supp charts information
        for sup_entry in urlSupplementCharts:
            link = sup_entry.get_attribute('href')
            print(link)

            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['icao'] = "SUP"
            chart_item['link'] = link
            chart_item['file'] = link.split('/')[-1].replace('.pdf', '') 
            chart_item['desc'] = sup_entry.get_attribute('innerText')
            chart_item['club'] = "SUP"
            chart_item['category'] = link.split('_')[-1].replace('.pdf', '')     #effectivity date

            list_of_charts.append(chart_item)

            
        ##
        ## AIP Section
        ##
        
        # go to Aerodrome Charts url
        self.browser.get(urlAerodromeCharts)
        if len(self.browser.find_elements_by_xpath('//*[@id="btnAgree"]')) > 0:# check if agree button exist
            self.browser.find_element_by_xpath('//*[@id="btnAgree"]').click() # click agree button.
            self.browser.get(urlAerodromeCharts) # go back to the url where you left off

        # get the links inside Aerodrome Charts, not yet urls
        elemsInAerodromeCharts = self.browser.find_elements_by_xpath('//*[@id="Form1"]/table[2]/tbody/tr[2]/td/table/tbody/tr/td/a')

        # url count inside Aerodrome Charts
        count = 0
        for elem in elemsInAerodromeCharts:
            listOfUrlsInAerodromeCharts.append(elem.get_attribute('href'))
            count += 1

        # process all pdf urls
        pdfCount = 0
        for url in listOfUrlsInAerodromeCharts:

            # check url if it ends with .pdf
            if str(url).lower().split('.')[-1] == 'pdf': 
                listOfPdfUrls.append(url) # add url in list if its a pdf
                pdfCount += 1             # count found pdf
                print(url)

            # check url if it does not end with .pdf
            elif str(url).lower().split('.')[-1] != 'pdf': 
                self.browser.get(url)      # if its not a pdf, go to the url.

                # check if agree button exist
                if len(self.browser.find_elements_by_xpath('//*[@id="btnAgree"]')) > 0:
                    clickIt = self.browser.find_element_by_xpath('//*[@id="btnAgree"]') # click agree button.
                    self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    clickIt.click()
                    self.browser.get(url) # go back to the url where you left off

                # get sub urls in current url
                urlSubUrls = self.browser.find_elements_by_xpath('//*[@id="Form1"]/table[2]/tbody/tr[2]/td/table/tbody/tr/td/a') 
                countOfPdfsInLink = 0
                
                # process all sub urls
                for subUrl in urlSubUrls:
                    listOfPdfUrls.append(subUrl.get_attribute('href')) # add url in list if its a pdf
                    pdfCount += 1 # count found pdf
                    print(subUrl.get_attribute('href'))
                    countOfPdfsInLink += 1
                print(countOfPdfsInLink)
                
        print('Icao Links: ' + str(count) + '  PDF: ' + str(pdfCount))
        print('SUP links: ' + str(len(urlSupplementCharts)))

        # close browser
        self.browser.close()

        # start parsing captured AIP elements
        for url in listOfPdfUrls:
            file = url.split('/')[-1].split('.pdf')[0]
            icao = file.split('_')[0]
            desc = file

            chart_item = ChartItem()

            chart_item['country'] = self.country_name
            chart_item['icao'] = icao
            chart_item['link'] = url
            chart_item['file'] = file
            chart_item['desc'] = desc
            chart_item['club'] = 'AIP-AD'
            chart_item['category'] = "N/A"

            list_of_charts.append(chart_item)

        self.chart_mgr = NewZealandChartPipeline(list_of_charts)
        self.chart_mgr.process_charts()

    def click_enable(self, buttonName):
        self.browser.execute_script('arguments[0].click();', buttonName)
        self.browser.wait(2)

    def close(self, reason):
        # Quit the browser
        self.browser.quit()
        # Delete
        del self

class NewZealandChartPipeline(ChartPipeline):

    def process_charts(self):
        """
            This method must describe how the extracted ChartItems
            must be processed!
        """

        # Prints the chart list to console
        #self.print_chart_list()
        self.save_chart_list('NewZealand')
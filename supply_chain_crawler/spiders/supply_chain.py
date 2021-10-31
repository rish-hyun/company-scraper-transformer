from scrapy import Spider, Request
from supply_chain_crawler.spiders import company_spiders


class SupplychainSpider(Spider):

    name = 'supply_chain'

    def __init__(self):
        self.find_company_base_url = 'https://find-and-update.company-information.service.gov.uk/'
        self.company_urls = [
            'https://www.wincanton.co.uk/',
            'https://www.palletways.com/',
            'https://www.gac.com/',
        ]

    # ----------------------------------------------------------------------------------------------

    def start_requests(self):
        for url in self.company_urls:
            domain = url.split('//')[-1].split('.')
            search_string = domain[1] if 'www' in domain[0] else domain[0]
            endpoint = 'search?q=' + search_string

            res = Request(url=self.find_company_base_url + endpoint, callback=self.find_company)
            res.meta['data'] = {
                'URL': url,
                'ID': search_string
            }
            yield res

    # ----------------------------------------------------------------------------------------------

    def find_company(self, response):
        url = self.find_company_base_url + response.xpath('//li[@class="type-company"]//a').attrib['href']
        res = Request(url=url, callback=self.find_company_details)
        res.meta['data'] = response.meta['data']
        yield res

    # ----------------------------------------------------------------------------------------------

    def find_company_details(self, response):
        response.meta['data'].update({
            'Company Name': response.xpath('//p[@class="heading-xlarge"]//text()').get(),
            'Company House Number': response.xpath('//p[@id="company-number"]//strong//text()').get(),
            'Company Status': response.xpath('//dd[@id="company-status"]//text()').get(),
            'Company Type': response.xpath('//dd[@id="company-type"]//text()').get(),
            'Company Office Address': response.xpath('//dl//dd//text()').get(),
            'Industry': response.xpath('//span[@id="sic0"]//text()').get(),
            # 'Company Financial Status': '-------'
            'content': False,
            'transform': False
        })

        url = f"https://www.trustpilot.com/review/{response.meta['data']['URL'].split('//')[1]}"
        res = Request(url=url, callback=self.company_review)
        res.meta['data'] = response.meta['data']
        yield res

    # ----------------------------------------------------------------------------------------------

    def company_review(self, response):
        review = response.xpath('string(//div[starts-with(@class,"styles_summaryInfo")])').get()
        response.meta['data']['Reviews'] = f'Trustpilot : {review}'

        res = Request(url=response.meta['data']['URL'], callback=self.crawl_company)
        res.meta['data'] = response.meta['data']
        yield res

    # ----------------------------------------------------------------------------------------------

    def crawl_company(self, response):
        company_name = response.meta['data']['ID']
        if hasattr(company_spiders, company_name):
            company = company_spiders.__getattribute__(company_name)()
            yield from company.parse(response)
        else:
            yield response.meta['data']

    # ----------------------------------------------------------------------------------------------


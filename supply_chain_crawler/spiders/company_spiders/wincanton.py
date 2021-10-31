from scrapy import Request


class wincanton:

    def parse(self, response):
        social_media = []
        for tag in response.xpath('//ul[@class="list-inline"]//a'):
            media = tag.attrib['aria-label']
            link = tag.attrib['href']
            social_media.append(f'{media}\n{link}\n')

        news_list = []
        for news in response.xpath('//a[@class="page-card "]'):
            link = news.attrib['href']
            text = news.xpath('string(.//h5)').get()
            news_list.append(''.join([link, '\n', text, '\n']))

        text = []
        text.append([response.xpath('//meta[@property="og:description"]').attrib['content'],
                     response.xpath('//p[@style="text-align: center;"]/text()')[1].get()])

        response.meta['data'].update({
            'Social Media': social_media,
            'Recent News': news_list,
            'Quality Certifications': None,
            'Summary': text,
            'content': True
        })

        what_we_do = response.xpath('//li[@class="trigger sub-menu"]')[1].xpath('./ul/li/a')[-1].attrib['href']
        res = Request(url=what_we_do, callback=self.what_we_do)
        res.meta['data'] = response.meta['data']
        yield res

    # ----------------------------------------------------------------------------------------------

    def what_we_do(self, response):
        text = response.meta['data']['Summary']

        sectors = []
        for info in response.xpath('//li[@class="trigger sub-menu active section"]/ul/li')[:-1]:
            sector = info.xpath('./a/text()').getall()
            sector.append(', '.join(info.xpath('./ul/li/a/text()').getall()))
            sectors.append(' - '.join(sector))

        services = response.xpath('//div[@class="small-caption"]/text()').getall()
        response.meta['data'].update({
            'Sectors': sectors,
            'Products/Services': services
        })

        text.append(['Company works for following industries - ', ', '.join(sectors)])
        text.append(['Company services are', ', '.join(services)])
        response.meta['data']['Summary'] = text

        why_wincanton = response.xpath('//li[@class="trigger sub-menu"]/a')[1].attrib['href']
        res = Request(url=why_wincanton, callback=self.why_wincanton)
        res.meta['data'] = response.meta['data']
        yield res

    # ----------------------------------------------------------------------------------------------

    def why_wincanton(self, response):
        text = response.meta['data']['Summary']
        text.append([response.xpath('//meta[@property="og:description"]').attrib['content'],
                     response.xpath('string(//section[@class="section pv-3-large"])').get().strip()])

        links = []
        message = []
        for info in response.xpath('//a[@class="ccm-block-page-list-page-entry "]'):
            msg = info.xpath('string(.//div[@class="ccm-block-page-list-description"])').get().strip()
            links.append(info.attrib['href'])
            message.append(msg)
        message.append(response.xpath('//div[@class="overlay-desc__box"]/p//text()')[0].get())

        text.append(message)
        response.meta['data']['Summary'] = text

        res = Request(url=links[0], callback=self.what_makes_us_different)
        res.meta['data'] = response.meta['data']
        yield res

    # ----------------------------------------------------------------------------------------------

    def what_makes_us_different(self, response):
        text = response.meta['data']['Summary']

        solutions = []
        for sol in response.xpath('//div[@class="row--flex"]/div[@class="row--content"]'):
            solutions.append(sol.xpath('string()').get().strip())

        text.append(solutions)
        response.meta['data']['Summary'] = text

        innovation = response.xpath('//a[@class="page-card related"]')[-1].attrib['href']
        res = Request(url=innovation, callback=self.innovation)
        res.meta['data'] = response.meta['data']
        yield res

    # ----------------------------------------------------------------------------------------------

    def innovation(self, response):
        text = response.meta['data']['Summary']

        technology = [response.xpath('string(//section[@class="section pv-3-large"])').get().strip()]
        for tech in response.xpath('//div[@class="card-text"]'):
            caption = tech.xpath('./p')[:-1].xpath('string()').getall()
            technology.append(' '.join(caption))

        text.append(technology)
        response.meta['data']['Summary'] = text

        who_we_are = response.xpath('//li[@class="trigger sub-menu"]/a')[0].attrib['href']
        res = Request(url=who_we_are, callback=self.who_we_are)
        res.meta['data'] = response.meta['data']
        yield res

    # ----------------------------------------------------------------------------------------------

    def who_we_are(self, response):
        text = response.meta['data']['Summary']

        links = []
        messages = [response.xpath('//meta[@property="og:description"]').attrib['content']]
        for info in response.xpath('//a[@class="ccm-block-page-list-page-entry "]'):
            msg = info.xpath('string(.//div[@class="ccm-block-page-list-description"])').get().strip()
            links.append(info.attrib['href'])
            messages.append(msg)

        text.append(messages)
        response.meta['data']['Summary'] = text

        res = Request(url=links[2], callback=self.customer)
        res.meta['data'] = response.meta['data']
        yield res

    # ----------------------------------------------------------------------------------------------

    def customer(self, response):
        text = response.meta['data']['Summary']
        
        messages = [response.xpath('//meta[@property="og:description"]').attrib['content']]
        for info in response.xpath('//div[@class="our-partners__body"]/p/text()'):
            messages.append(info.get().strip())

        text.append(messages)
        response.meta['data']['Summary'] = text
        yield response.meta['data']

    # ----------------------------------------------------------------------------------------------

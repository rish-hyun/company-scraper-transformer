from scrapy import Request


class palletways:

    def parse(self, response):
        social_media = []
        for info in response.xpath('//div[@class="footer__social"]//a'):
            link = info.attrib['href']
            name = info.attrib['title']
            social_media.append(f'{name}\n{link}')

        news_list = []
        for news in response.xpath('//div[@class="card card_news"]//a')[:4]:
            title = news.attrib['title']
            link = news.attrib['href']
            news_list.append(f'{title}\n{link}')

        text = [[response.xpath('//meta[@name="description"]').attrib['content']]]
        for info in response.xpath('//div[@class="editable"]')[::2]:
            text[-1].append(info.xpath('string()').get())

        response.meta['data'].update({
            'Social Media': social_media,
            'Recent News': news_list,
            'Quality Certifications': None,
            'Summary': text,
            'content': True
        })

        about_us = response.xpath('//a[@title=" About us"]').attrib['href'].replace('../', '')
        res = Request(url=about_us, callback=self.about_us)
        res.meta['data'] = response.meta['data']
        yield res

    # ----------------------------------------------------------------------------------------------

    def about_us(self, response):
        text = response.meta['data']['Summary']

        about_us = []
        for info in response.xpath('//div[@id="about_us_2_parg"]//div[@class="editable"]//p'):
            about_us.append(info.xpath('string()').get())

        text.append(about_us)
        response.meta['data']['Summary'] = text

        services = response.xpath('//a[@title="Services"]').attrib['href'].replace('../', '')
        res = Request(url=services, callback=self.services)
        res.meta['data'] = response.meta['data']
        yield res

    # ----------------------------------------------------------------------------------------------

    def services(self, response):
        services = []
        for info in response.xpath('//div[@class="title"]'):
            if int(info.xpath('not(h5)').get()):
                services.append(info.xpath('string()').get().strip())

        text = response.meta['data']['Summary']
        text.append(response.xpath('//div[@class="title title_accent"]//h1//text()').getall())
        text[-1].append('-')
        text[-1].append(', '.join(services))

        response.meta['data']['Products/Services'] = services
        response.meta['data']['Summary'] = text

        sectors = response.xpath('//a[@title="Industry sectors"]').attrib['href'].replace('../', '')
        res = Request(url=sectors, callback=self.sectors)
        res.meta['data'] = response.meta['data']
        yield res

    # ----------------------------------------------------------------------------------------------

    def sectors(self, response):
        sectors = []
        for info in response.xpath('//div[@class="inner-content"]'):
            title = info.xpath('string(.//div[@class="title"]//h2)').get()
            content = info.xpath('.//div[@class="editable"]//p//text()').get()
            sectors.append(f'{title} - "{content}"')

        sectors = response.xpath('//a[@data-role="scroll-to"]//text()').getall()
        text = response.meta['data']['Summary']
        text.append([response.xpath('//div[@class="title"]//p//text()').get()])
        text[-1].append('-')
        text[-1].append(', '.join(sectors))

        response.meta['data']['Sectors'] = response.xpath('//a[@data-role="scroll-to"]//text()').getall()
        response.meta['data']['Summary'] = text

        yield response.meta['data']

    # ----------------------------------------------------------------------------------------------

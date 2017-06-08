import scrapy

class CragsSpider(scrapy.Spider):
    name = 'CragsSpider'
    start_urls = ['https://27crags.com/countries/sweden']

    def parse(self, response):
        for crag in response.css('a.location'):
            yield response.follow(crag, self.parse_crag)

        next_page_url = response.css('a.next::attr(href)').extract_first()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))

    def parse_crag(self, response):
        routelist_url = response.css('#crags-show section.crag-big-menu a::attr(href)').extract_first()
        if routelist_url is not None:
            yield scrapy.Request(response.urljoin(routelist_url), callback=self.parse_routelist)

    def parse_routelist(self, response):
        for sector in response.css('a.sector-item:not(.all-routes)'):
            yield response.follow(sector, self.parse_sector)

    def parse_sector(self, response):
        coordinates_string = response.css('.topo-navigation a.sector-property::attr(data-href)').extract_first()
        coordinates = [c.strip() for c in coordinates_string.split(',')]
        yield {
            'lat': coordinates[0],
            'lng': coordinates[1],
            'sector_name': response.css('.topo-navigation span.name::text').extract_first(),
            'crag_name': response.css('h1.cragname::attr(title)').extract_first()
        }

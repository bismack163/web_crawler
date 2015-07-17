# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.selector import Selector
import logging
from scrapy_pr1.items import ScrapyPr1Item
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# logging = logging.getLogger()

class AwwSpider(scrapy.Spider):
    name = "aww"
    allowed_domains = ["youtube.com"]
    start_urls = (
        'https://www.youtube.com/playlist?list=PLrEnWoR732-DN561GnxXKMlocLMc4v4jL',
    )

    def parse(self, response):
        counter = 0
        for tr in response.xpath('//table/tbody/tr'):
            item = ScrapyPr1Item()
            item['title'] = tr.xpath('@data-title').extract()[0]
            item['vid'] = tr.xpath('@data-video-id').extract()[0]
            counter+=1
            yield item
        load_more = response.xpath("//button[@data-uix-load-more-target-id]/@data-uix-load-more-href").extract()[0]
        logging.debug('load %d on first page', counter)
        logging.debug('load more href on first page = %s', load_more)
        if load_more != None:
            url = response.urljoin(load_more)
            yield scrapy.Request(url, callback=self.loadMoreAjax)            
        
    def loadMoreAjax(self, response):
        counter = 0;
        data_dict = json.loads(response.body)
        if data_dict == None:
            logging.debug('no more ajax')
            return
        if not data_dict.has_key('content_html'):
            logging.debug('no more ajax')
            return
        content = Selector(text=data_dict['content_html'])
        for tr in content.xpath('//tr[@data-title]'):
            item = ScrapyPr1Item()
            item['title'] = tr.xpath('@data-title').extract()[0]
            item['vid'] = tr.xpath('@data-video-id').extract()[0]
            counter+=1
            yield item        
        logging.debug("load %d more items in ajax", counter)    
        more = Selector(text=data_dict['load_more_widget_html'])
        load_more = more.xpath("//button[@data-uix-load-more-target-id]/@data-uix-load-more-href").extract()
        if len(load_more) > 0:
            load_more = load_more[0]
        else:
            load_more = None
        logging.debug('load more on Ajax = %s', load_more)
        if load_more != None:
            url = response.urljoin(load_more)
            yield scrapy.Request(url, callback=self.loadMoreAjax)
        return           
        
            

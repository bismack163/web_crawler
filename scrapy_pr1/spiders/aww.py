# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.selector import Selector
import logging
from scrapy_pr1.items import ScrapyPr1Item
import youtube_dl
import shutil
ydl_opts = {'outtmpl':'./vid/%(title)s-%(id)s.%(ext)s'}
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# logging = logging.getLogger()

class AwwSpider(scrapy.Spider):
    name = "aww"
    allowed_domains = ["youtube.com"]
    start_urls = (
        'https://www.youtube.com/playlist?list=PLrEnWoR732-DN561GnxXKMlocLMc4v4jL',
    )
    
    def __init__(self, category=None, *args, **kwargs):
        super(AwwSpider, self).__init__(*args, **kwargs)
        self.items = []
        with open('vids.json') as data_file:    
            self.history = json.load(data_file)
            if len(self.history) > 0:
                self.lastHistoryVid = self.history[0]['vid']
            else:
                self.lastHistoryVid = None
    
    def closed(self, reason):
        if reason != 'finished':
            return
        shutil.copy2('vids.json', 'vids.json.bak')
        with open('vids.json', 'wb') as data_file:    
            data_file.write('[\n')
            for item in self.items:
                line = json.dumps(dict(item)) + ",\n"
                data_file.write(line)
            for item in self.history:
                line = json.dumps(dict(item)) + ",\n"
                data_file.write(line)
            data_file.write(']\n')
         
    def _extractData(self, tr):
        item = ScrapyPr1Item()
        item['vid'] = tr.xpath('@data-video-id').extract()[0]
        if self.lastHistoryVid == item['vid']:
            return None
#         for oldItem in self.history:
#             if oldItem['vid'] == item['vid']:
#                 return None
        item['title'] = tr.xpath('@data-title').extract()[0]
        item['duration'] = tr.xpath('.//div[@class="timestamp"]/span/text()').extract()[0]
        self._download(item['vid'])
        self.items.append(item)
        return item
    
    def _download(self, vid):
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(['http://www.youtube.com/watch?v=%s'% vid])
    
    def parse(self, response):
        counter = 0
        for tr in response.xpath('//table/tbody/tr'):
            item = self._extractData(tr)
            if item == None:
                return
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
            item = self._extractData(tr)
            if item == None:
                return
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
        
            

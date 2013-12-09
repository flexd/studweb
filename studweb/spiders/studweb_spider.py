#!/usr/bin/env python
# encoding=utf-8

from scrapy.spider import BaseSpider
from scrapy.conf import settings
from scrapy.http import Request
from scrapy.http import FormRequest
from scrapy.selector import Selector
from scrapy import log
import sys
### Kludge to set default encoding to utf-8
reload(sys)
sys.setdefaultencoding('utf-8')
from pynma import PyNMA
import redis

class StudwebSpider(BaseSpider):
    name = "studweb"
    allowed_domains = ["www.studweb.no"]
    start_urls = [
        "https://www.studweb.no/as/WebObjects/studentweb2?inst=HiOA"
        #"https://www.studweb.no/as/WebObjects/studentweb2"
    ]

    def parse(self, response):
      return [FormRequest.from_response(response, formname='fnrForm', formdata={'fodselsnr': self.crawler.settings.get('STUDWEB_FNR'),
              'pinkode': self.crawler.settings.get('STUDWEB_PIN')},
                                        callback=self.after_login)]
    def after_login(self, response):
      s = Selector(response)
      innsyn_url = s.xpath('//*[@id="navig-menu"]/table/tr[5]/td[1]/a/@href').extract()[0]
      print "Innsyn URL er: %s " % innsyn_url
      return Request('https://www.studweb.no%s' % innsyn_url, callback=self.after_innsyn)
    def after_innsyn(self, response):
      hxs = Selector(response)
      resultater_url = hxs.xpath('//*[@id="navig-menu"]/table/tr[8]/td[1]/a/@href').extract()[0]
      return Request('https://www.studweb.no%s' % resultater_url, callback=self.parse_results)
    def parse_results(self, response):
      nma = PyNMA(self.crawler.settings.get('NMA_APIKEY'))

      r = redis.StrictRedis(host='localhost')
      forrige_studiepoeng = r.get('forrige_studiepoeng')
      hxs = Selector(response)
      studiepoeng = hxs.xpath('/html/body/table/tr[3]/td[2]/table/tr[last()]/td[3]/text()').extract()[0]
      studiepoeng = float(str(studiepoeng).replace(",", "."))
      #self.log("Antall studiepoeng: %s" % studiepoeng)
      if forrige_studiepoeng is None:
        r.set('forrige_studiepoeng', studiepoeng)
        self.log('Redis key did not exist, setting it now!')
      else:
        if studiepoeng > float(forrige_studiepoeng):
          nma.push('Karakterer', 'Eksamensresultater', 'Antall studiepoeng har gått opp!')
          r.set('forrige_studiepoeng', studiepoeng)
          self.log('Studiepoeng er høyere enn forrie gang!')
        else:
          self.log('Studiepoeng: %s, forrige Studiepoeng: %s' % (studiepoeng, forrige_studiepoeng))
      #resultater_table = hxs.select('/html/body/table/tr[3]/td[2]/table/tr')
      #for resultat in resultater_table:
        #print resultat

# Scrapy settings for studweb project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'studweb'

SPIDER_MODULES = ['studweb.spiders']
NEWSPIDER_MODULE = 'studweb.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'studweb (+http://www.yourdomain.com)'
# http://notifymyandroid.com
NMA_APIKEY = "<REPLACE ME>"

STUDWEB_FNR = '<REPLACE ME>'
STUDWEB_PIN = '<REPLACE ME> '

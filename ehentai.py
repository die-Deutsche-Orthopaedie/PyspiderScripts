from pyspider.libs.base_handler import *
import os

url = ""
folder = ""
wgetlog = "log.txt"

class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        
        self.crawl(url, callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        
        global folder
        global wgetlog
        
        title = response.doc('title').text()
        mkdir = "cd \""+folder+"\" && if [ ! -d \""+title+"\" ]; then mkdir \""+title+"\"; fi && cd \""+title+"\" && if [ ! -d dumped ]; then mkdir dumped; fi" 
        os.system(mkdir)
        folder = folder+"/"+title
        
        if wgetlog:
            clearwgetlog = "cd \""+folder+"\" && rm -rf \""+wgetlog+"\""
            os.system(clearwgetlog)
            wgetlog = folder+"/"+wgetlog
        
        folder = folder+"/"+"dumped"
        
        for each in response.doc('tr>td>a').items():
            if each.text().find(">") >= 0:
                self.crawl(each.attr.href, callback=self.index_page2)

        for each in response.doc('div#gdt>div.gdtm>div>a').items():
            self.crawl(each.attr.href, callback=self.detail_page)
            
            
    @config(age=10 * 24 * 60 * 60)
    def index_page2(self, response):
        
        for each in response.doc('tr>td>a').items():
            if each.text().find(">") >= 0:
                self.crawl(each.attr.href, callback=self.index_page2)

        for each in response.doc('div#gdt>div.gdtm>div>a').items():
            self.crawl(each.attr.href, callback=self.detail_page)        
        
                   
    @config(priority=2)
    def detail_page(self, response):
        
        for each in response.doc('div.sni>a>img').items():
            imageURL = each.attr.src
       
        wget = "cd \""+folder+"\" && wget \""+imageURL+"\""
        if wgetlog:
            wget = wget+" 2>> \""+wgetlog+"\""
        print wget
        os.system(wget)
        
        return {
            "url": response.url,
            "title": response.doc('title').text(),
            "imageURL": imageURL,
        }

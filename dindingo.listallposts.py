from pyspider.libs.base_handler import *
import codecs

class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://www.dindincc.com/bbs/thread.php?fid-118.html', callback=self.index_page)
        
    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        f = codecs.open("ddg.txt","a+",'utf-8')
        
        for each in response.doc('a.pages_next').items():
            self.crawl(each.attr.href, callback=self.index_page)

        for each in response.doc('tr.tr3').items():
            #self.crawl(each.children('td.subject>a.subject_t.f14').attr.href, callback=self.detail_page)
            print "Title: "+each.children('td.subject>a.subject_t.f14').text()
            f.write("Title: "+each.children('td.subject>a.subject_t.f14').text()+'\n')
            print "Link: "+each.children('td.subject>a.subject_t.f14').attr.href
            f.write("Link: "+each.children('td.subject>a.subject_t.f14').attr.href+'\n')            
            for each2 in each.children('td.author>p').items():
                if each2.children('a').text() == "":
                    print "PostTime: "+each2.text()
                    f.write("PostTime: "+each2.text()+'\n')
                else:
                    print "CommentTime: "+each2.text()
                    f.write("CommentTime: "+each2.text()+'\n')
            print
            f.write('\n')
        
        f.close()
                   
    @config(priority=2)
    def detail_page(self, response):
        return {
            "url": response.url,
            "title": response.doc('title').text(),
        }

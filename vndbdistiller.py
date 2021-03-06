from pyspider.libs.base_handler import *
import MySQLdb

dbHost = ""
dbUsername = ""
dbPassword = ""
dbName = ""

class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        c = MySQLdb.connect(host=dbHost,user=dbUsername,passwd=dbPassword,db=dbName,charset="utf8")
        cur = c.cursor()
        
        statement="CREATE TABLE IF NOT EXISTS `characters` (\
          `ID` int(11) NOT NULL,\
          `rName` text NOT NULL,\
          `jName` text NOT NULL,\
          `URL` text NOT NULL,\
          `pURL` text NOT NULL,\
           PRIMARY KEY (`ID`)\
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Characters Table';"
        try:
            cur.execute(statement)
            c.commit()
        except:
            c.rollback()
            
        statement="CREATE TABLE IF NOT EXISTS `vns` (\
          `ID` int(11) NOT NULL,\
          `pID` int(11) NOT NULL,\
          `Title` text NOT NULL,\
          `URL` text NOT NULL,\
          PRIMARY KEY (`ID`)\
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='VNs Table';"
        try:
            cur.execute(statement)
            c.commit()
        except:
            c.rollback()
        
        statement="CREATE TABLE IF NOT EXISTS `cvr` (\
          `cID` int(11) NOT NULL,\
          `vnID` int(11) NOT NULL,\
          `IMC` text NOT NULL\
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Character-VN Relations Table';"
        try:
            cur.execute(statement)
            c.commit()
        except:
            c.rollback()
              
        cur.close()
        c.close()        
        self.crawl('https://vndb.org/c13454', callback=self.character_page)
        self.crawl('https://vndb.org/c13453', callback=self.character_page)
        self.crawl('https://vndb.org/c465', callback=self.character_page)
        self.crawl('https://vndb.org/c/all?q=&fil=gender-f.trait_inc-29~146.tagspoil-0', callback=self.index_page)
        
    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        c = MySQLdb.connect(host=dbHost,user=dbUsername,passwd=dbPassword,db=dbName,charset="utf8")
        cur = c.cursor()
        
        for each in response.doc('ul.maintabs.browsetabs.bottom>li>a').items():
            if each.text().find("next") >= 0:
                self.crawl(each.attr.href, callback=self.index_page)

        for each in response.doc('table.stripe>tr').items():
            jName = each.children('td.tc2>a').attr.title.replace('\'','\\\'')
            rName = each.children('td.tc2>a').text().replace('\'','\\\'')
            cURL = each.children('td.tc2>a').attr.href.replace('\'','\\\'')
            cID = cURL.strip('https://vndb.org/c')
            
            print "Japanese Name: "+jName
            print "Romanji Name: "+rName
            print "URL: "+cURL
            print "ID: "+cID
            
            statement="insert into characters values ('"+cID+"', '"+rName+"', '"+jName+"', '"+cURL+"', '')"
            try:
                cur.execute(statement)
                c.commit()
            except:
                c.rollback()
            
            
            self.crawl(cURL, callback=self.character_page)
            
            """
            print "this character has been appeared in: "
            
            for each2 in each.children('td.tc2>b.grayedout>a').items():
                vnTitle = each2.attr.title.replace('\'','\\\'')
                vnURL = each2.attr.href.replace('\'','\\\'')
                vnID = vnURL.strip('https://vndb.org/v').strip('/chars')
                print "\t"+vnTitle+" / "+vnURL+" / "+vnID
            
                statement="insert into vns values ('"+vnID+"', '"+cID+"', '"+vnTitle+"', '"+vnURL+"')"
                print statement
                try:
                    cur.execute(statement)
                    c.commit()
                except:
                    c.rollback()
            """
            print
            
        cur.close()
        c.close()
                   
    @config(priority=2)
    def character_page(self, response):
        c2 = MySQLdb.connect(host=dbHost,user=dbUsername,passwd=dbPassword,db=dbName,charset="utf8")
        cur2 = c2.cursor()
        
        if response.doc('div.chardetails.charspoil.charspoil_0>div.charimg').text().find("No image uploaded yet") < 0:
            pURL = response.doc('div.chardetails.charspoil.charspoil_0>div.charimg>img').attr.src
        else:
            pURL = ""
        cID = response.url.strip('https://vndb.org/c')
        
        print "Picture URL: "+pURL
        print "Character ID: "+cID
        print
        
        statement="UPDATE characters SET `pURL` = '"+pURL+"' WHERE `ID` = "+cID
        try:
            cur2.execute(statement)
            c2.commit()
        except:
            c2.rollback()

        sign = 1

        print "this character has been appeared in: "
        print
        
        for each in response.doc('tr').items():
            if each.children('td.key').text().find("novel") >= 0:
                for each2 in each.children('td>span.charspoil.charspoil_0').items():           
                    if sign == 1:
                        vnIMC = each2.text()[0:4]
                        if vnIMC.find("Main") < 0 and vnIMC.find("Side") < 0:
                            vnIMC = "Undefined"
                            vnTitle = each2.children('a').text().replace('\'','\\\'')
                            vnURL = each2.children('a').attr.href.replace('\'','\\\'')
                            vnpID = vnURL.strip('https://vndb.org/v').strip('/chars')
                        
                            print vnIMC+" Character"
                            print vnTitle
                            print vnURL
                            print vnpID
                            print
                            
                            statement="insert into vns values ('"+vnpID+"', '', '"+vnTitle+"', '"+vnURL+"')"
                            try:
                                cur2.execute(statement)
                                c2.commit()
                            except:
                                c2.rollback()
                            
                            statement="SELECT * FROM cvr WHERE cID = "+cID+" AND vnID = "+vnpID+""
                            try:
                                count = cur2.execute(statement)
                                c2.commit()
                            except:
                                print statement
                                c2.rollback()
                                                        
                            if count == 0:
                                statement="insert into cvr values ('"+cID+"', '"+vnpID+"', '"+vnIMC+"')"
                                try:
                                    cur2.execute(statement)
                                    c2.commit()
                                except:
                                    print statement
                                    c2.rollback()
                            
                            for each3 in each2.children('span.charspoil.charspoil_0').items():
                                vnIMC = each3.text()[2:6]
                                vnTitle = each3.children('a').text().replace('\'','\\\'')
                                vnURL = each3.children('a').attr.href.replace('\'','\\\'')
                                vnID = vnURL.strip('https://vndb.org/v').strip('/chars')
                            
                                print vnIMC+" Character"
                                print vnTitle
                                print vnURL
                                print vnID
                                print
                            
                                statement="insert into vns values ('"+vnID+"', '"+vnpID+"', '"+vnTitle+"', '"+vnURL+"')"
                                try:
                                    cur2.execute(statement)
                                    c2.commit()
                                except:
                                    c2.rollback()
                                
                                statement="SELECT * FROM cvr WHERE cID = "+cID+" AND vnID = "+vnID+""
                                try:
                                    count = cur2.execute(statement)
                                    c2.commit()
                                except:
                                    print statement
                                    c2.rollback()
                                                                
                                if count == 0:
                                    statement="insert into cvr values ('"+cID+"', '"+vnID+"', '"+vnIMC+"')"
                                    try:
                                        cur2.execute(statement)
                                        c2.commit()
                                    except:
                                        print statement
                                        c2.rollback()
                                    
                        else:
                            vnTitle = each2.children('a').text().replace('\'','\\\'')
                            vnURL = each2.children('a').attr.href.replace('\'','\\\'')
                            vnID = vnURL.strip('https://vndb.org/v').strip('/chars')
                        
                            print vnIMC+" Character"
                            print vnTitle
                            print vnURL
                            print vnID
                            print
                        
                            statement="insert into vns values ('"+vnID+"', '', '"+vnTitle+"', '"+vnURL+"')"
                            try:
                                cur2.execute(statement)
                                c2.commit()
                            except:
                                c2.rollback()
                            
                            statement="SELECT * FROM cvr WHERE cID = "+cID+" AND vnID = "+vnID+""
                            try:
                                count = cur2.execute(statement)
                                c2.commit()
                            except:
                                c2.rollback()
                            
                            if count == 0:
                                statement="insert into cvr values ('"+cID+"', '"+vnID+"', '"+vnIMC+"')"
                                try:
                                    cur2.execute(statement)
                                    c2.commit()
                                except:
                                    print statement
                                    c2.rollback()
                                    
                        print
                sign = 0
        
        cur2.close()
        c2.close()
        
        return {
            "url": response.url,
            "title": response.doc('title').text(),
        }
        

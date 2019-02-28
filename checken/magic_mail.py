import smtplib
import requests
import re
import sys
import datetime
import urllib.parse
import urllib.request
import ssl, socket, OpenSSL

from pprint import pprint
from bs4 import BeautifulSoup
from email.message import EmailMessage
from email.headerregistry import Address
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from http.cookiejar import CookieJar

# IMPORT CONSTANTS
from .constants import META_DSC_MAX_LEN 
from .constants import META_DSC_MIN_LEN 
from .constants import META_DSC_COUNT 

from .constants import META_KEYWORD_MAX_LEN 
from .constants import META_KEYWORD_MIN_LEN 
from .constants import META_KEYWORD_COUNT 

from .constants import SITE_TITLE_MAX_LEN 
from .constants import SITE_TITLE_MIN_LEN 
from .constants import SITE_TITLE_COUNT 

from .constants import H1_MAX_LEN 
from .constants import H1_MIN_LEN 
from .constants import H1_COUNT 

from .constants import H2_MAX_LEN 
from .constants import H2_MIN_LEN 
from .constants import H2_COUNT 

from .constants import SMTP_HOST 
from .constants import SMTP_USERNAME 
from .constants import SMTP_PASS 
from .constants import SMTP_PORT 

from .constants import FROM_TITLE 
from .constants import MAIL_SUBJECT 

class Crack_hunt:
    def __init__(self, input_url, input_email = ''):
        if self.validate_url(input_url) is False:
            print("INVALID URL SUPPLIED!")
            return None
        else:
            self.hunt_url = input_url
            self.hunt_email = input_email 
        
        #USED DICTIONARY
        self.issues = dict()
        self.performance = dict()
        self.meta_data = dict()

        #USED SETS
        self.internal_broken_links = set()
        self.external_broken_links = set()
        
        #ERROR SETS
        self._error_missing_meta = set()
        self._error_lengthy_meta = set()
        self._error_short_meta = set()
        self._error_meta_count = set()
        self._error_header1_tag_count = set()
        self._error_header1_lengthy_tag = set()
        self._error_header1_short_tag = set()
        self._error_header2_tag_count = set()
        self._error_header2_lengthy_tag = set()
        self._error_header2_short_tag = set()
        self._error_broken_links = set()

        self.configure_settings()

        """ r  = requests.get(input_url)
        data = r.text
        soup = BeautifulSoup(data)

        for link in soup.find_all('a'):
            print(link.get('href')) """

    def configure_settings(self):
        self.performance['seo_performance'] = dict()
        self.performance['website_performance'] = dict()
        
        self.performance['seo_performance']['negative'] = 0
        self.performance['seo_performance']['positive'] = 0
        self.performance['website_performance']['negative'] = 0
        self.performance['website_performance']['positive'] = 0
        
        self._recommended_meta = {
            "title" : {
                'max_length' : SITE_TITLE_MAX_LEN,
                'min_length' : SITE_TITLE_MIN_LEN,
                'count' : SITE_TITLE_COUNT
            },
            "description" : {
                "max_length" : META_DSC_MAX_LEN,
                "min_length" : META_DSC_MIN_LEN,
                "count" : META_DSC_COUNT
            },
            "keywords" : {
                "max_length" : META_KEYWORD_MAX_LEN,
                "min_length" : META_KEYWORD_MIN_LEN,
                "count" : META_KEYWORD_COUNT
            }
        }
        
        self._required_html_tag = {
            "title" : {
                "max_length" : SITE_TITLE_MAX_LEN,
                "min_length" : SITE_TITLE_MIN_LEN,
                "count" : SITE_TITLE_COUNT
            },
            "meta": True,
            "h1" : {
                "max_length" : H1_MAX_LEN,
                "min_length" : H1_MIN_LEN,
                "count" : H1_COUNT
            },
            "h2" : {
                "max_length" : H2_MAX_LEN,
                "min_length" : H2_MIN_LEN,
                "count" : H2_COUNT
            },
        }

    def configure_mail(self): 
        self.server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        self.server.starttls()
        #Next, log in to the server
        self.server.login(SMTP_USERNAME, SMTP_PASS)

    def validate_url(self, given_url):
        try:
            regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

            if re.match(regex, given_url) is not None:
                return True
        except:
            return False

        return False

    def send_mail(self, email_to, email_title, mail_subject, mail_content):
        self.configure_mail()
        
        #msg = EmailMessage()
        msg = MIMEMultipart('alternative')
        msg['Subject'] = mail_subject
        msg['From'] = SMTP_USERNAME # str(Address(display_name=FROM_TITLE, addr_spec='dhirendra@ethanetechnologies.org'), 'UTF-8')
        msg['To'] = email_to # str(Address(display_name=email_title, addr_spec=email_to), 'UTF-8')
        part1 = MIMEText('text', 'plain')
        part2 = MIMEText(mail_content, 'html')
        #msg.add_header('Content-Type','text/html')
        msg.attach(part1)
        msg.attach(part2)
        #msg.set_content(mail_content) 

        #Send the mail
        #self.server.send_message(msg)
        self.server.sendmail(SMTP_USERNAME, email_to, msg.as_string())
        self.server.quit()

    def check_internal_links(self):
        parsed_hunt_url = urllib.parse.urlparse(self.hunt_url)

        if parsed_hunt_url.netloc:
            site_domain_name = parsed_hunt_url.netloc
        else:
            return False
        
        links = set()
        self.parsed_url_internal_links = set()
        self.parsed_url_external_links = set()
        
        for link in self.hunted_html_domobj.find_all("a"):
            if self.validate_url(link.get("href")) is True:
                links.add(link.get("href"))
        
        if links is not None:
            for link in links:
                parsed_url = urllib.parse.urlparse(link)
                
                if(parsed_url.netloc and (parsed_url.netloc == site_domain_name)):
                    self.parsed_url_internal_links.add(link)
                else:
                    self.parsed_url_external_links.add(link)
        
        return self.parsed_url_external_links

    def check_alt_tag(self):
        for img in self.hunted_html_domobj.find_all('img'):
            if 'alt' not in img:
                return True
        
        return False

    def hunt_this(self):
        start_time = datetime.datetime.now()
        r  = requests.get(self.hunt_url)
        end_time = datetime.datetime.now()
        self.hunted_html_string = r.text
        self.hunted_html_domobj = BeautifulSoup(self.hunted_html_string, "lxml")
        diff_btw = end_time - start_time
        self.load_time = diff_btw.total_seconds()

    def check_responsive(self):
        for element in self.hunted_html_domobj.find_all(attrs={"name":"viewport"}):
            if element is not None:
                return False
        
        return True

    def check_not_exist_link(self, given_url):
        if self.validate_url(given_url):
            try:
                req=urllib.request.Request(given_url, None, {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; G518Rco3Yp0uLV40Lcc9hAzC1BOROTJADjicLjOmlr4=) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3','Accept-Encoding': 'gzip, deflate, sdch','Accept-Language': 'en-US,en;q=0.8','Connection': 'keep-alive'})
                cj=CookieJar()
                opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
                resp=opener.open(req)
                resp.close()
            except urllib.request.HTTPError:
                return True

            """ req=urllib.request.Request(url=given_url)
            resp=urllib.request.urlopen(req) """
            #request = requests.get(given_url)
        else:
            return False
        
        if resp.status in [400,404,403,408,409,501,502,503]:
            return True
        else:
            return False

    def check_broken_links(self):
        
        for in_lk in self.parsed_url_internal_links:
            if self.check_not_exist_link(in_lk):
                self.internal_broken_links.add(in_lk)
        
        for ex_lk in self.parsed_url_external_links:
            if self.check_not_exist_link(ex_lk):
                self.external_broken_links.add(ex_lk)


    def get_meta_report(self):
        self.issues['meta'] = dict()

        title = self.hunted_html_domobj.find('title')

        if title.text != '':
            self.issues['meta']['site_title'] = 'Found'
            self.performance['seo_performance']['positive'] += 1
            self.performance['website_performance']['positive'] += 1
            
            if len(title.text) < self._recommended_meta['title']['min_length']:
                
                self.issues['meta']['title_short_length'] = 'BAD'
                self.performance['seo_performance']['negative'] += 1
            else:
                self.issues['meta']['title_short_length'] = 'GOOD'
                self.performance['seo_performance']['positive'] += 1
            
            if len(title.text) > self._recommended_meta['title']['max_length']:
                
                self.issues['meta']['title_long_length'] = 'BAD'
                self.performance['seo_performance']['negative'] += 1
            else:
                self.issues['meta']['title_long_length'] = 'GOOD'
                self.performance['seo_performance']['positive'] += 1
        else:
            self.issues['meta']['site_title'] = 'Not Found'
            self.performance['seo_performance']['negative'] += 1
            self.performance['website_performance']['negative'] += 1

        for element in self.hunted_html_domobj.find_all('meta'):

            if "name" in element.attrs:
                self.meta_data[element.attrs.get("name", None)] = element.attrs.get("content", None)
            
            if "property" in element.attrs:
                self.meta_data[element.attrs.get("property")]  = element.attrs.get("content", None)
        
        meta_count = dict()

        for meta_k in self.meta_data:
            if meta_k not in meta_count:
                meta_count[meta_k] = 1
            else:
                meta_count[meta_k] = meta_count[meta_k] + 1
                
                if meta_k in self._recommended_meta:
                    if meta_count[meta_k] > self._recommended_meta[meta_k]['count']:
                        self._error_meta_count.add(meta_k)

        
        for meta_key, meta_value in self._recommended_meta.items():
            if meta_key not in self.meta_data:
                self._error_missing_meta.add(meta_key)
            else:
                if len(self.meta_data[meta_key]) > meta_value['max_length']:
                    self._error_lengthy_meta.add(meta_key)
                
                if len(self.meta_data[meta_key]) < meta_value['min_length']:
                    self._error_short_meta.add(meta_key)
        
        """ PRINT META COUNT ERROR """
        self.issues['meta_tag_repeated'] = set()
        for error in self._error_meta_count:
            self.issues['meta_tag_repeated'].add("Meta Tag " + error + " repeated multiple times.")
        
        """ PRINT META MISSING ERROR """
        self.issues['meta_tag_missing'] = set()
        for error in self._error_missing_meta:
            self.issues['meta_tag_missing'].add("Meta Tag " + error + " missing.")
        
        """ PRINT META MAX LENGTH ERROR """
        self.issues['meta_tag_lengthy'] = set()
        for error in self._error_lengthy_meta:
            self.issues['meta_tag_lengthy'].add("Meta Tag " + error + " is lengthy than recommended value")
        
        """ PRINT META MIN LENGTH ERROR """
        self.issues['meta_tag_short'] = set()
        for error in self._error_short_meta:
            self.issues['meta_tag_short'].add("Meta Tag " + error + " is shorter than recommended value")

    def get_tag_report(self):

        self.issues['h1_tag_repeated'] = set()
        self.issues['h2_tag_repeated'] = set()
        self.issues['h1_tag_lengthy'] = set()
        self.issues['h2_tag_lengthy'] = set()
        self.issues['h1_tag_short'] = set()
        self.issues['h2_tag_short'] = set()

        h1_content = self.hunted_html_domobj.find('h1')
        h2_content = self.hunted_html_domobj.find('h2')

        if h1_content and 'text'in h1_content:
            if len(h1_content.text) > self._required_html_tag['h1']['max_length']:
                self._error_header1_lengthy_tag.add('H1')

            if len(h1_content.text) < self._required_html_tag['h1']['min_length']:
                self._error_header1_short_tag.add('H1')

        if h2_content and 'text'in h2_content:
            if len(h2_content.text) > self._required_html_tag['h2']['max_length']:
                self._error_header1_lengthy_tag.add('H2')

            if len(h2_content.text) < self._required_html_tag['h2']['min_length']:
                self._error_header2_short_tag.add('H2')

        # PRINT HEADER COUNT ERROR 
        if self._error_header1_tag_count:
            self.performance['website_performance']['negative'] += 1
            
            for error in self._error_header1_tag_count:
                self.issues['h1_tag_repeated'].add(error + " Tag is repeated multiple times.")
        else:
            self.performance['website_performance']['positive'] += 1
        
        if self._error_header2_tag_count:
            self.performance['website_performance']['negative'] += 1
            
            for error in self._error_header2_tag_count:
                self.issues['h2_tag_repeated'].add(error + " Tag is repeated multiple times.")
        else:
            self.performance['website_performance']['positive'] += 1

        # PRINT HEADER MAX LENGTH ERROR
        if self._error_header1_lengthy_tag:
            self.performance['seo_performance']['negative'] += 1
            
            for error in self._error_header1_lengthy_tag:
                self.issues['h1_tag_lengthy'].add(error + " Tag is lengthy than recommended value")
        else:
            self.performance['seo_performance']['positive'] += 1
        
        if self._error_header2_lengthy_tag:
            self.performance['seo_performance']['negative'] += 1
            
            for error in self._error_header2_lengthy_tag:
                self.issues['h2_tag_lengthy'].add(error + " Tag is lengthy than recommended value")
        else:
            self.performance['seo_performance']['positive'] += 1
            

        # PRINT HEADER MIN LENGTH ERROR
        if self._error_header1_short_tag:
            self.performance['seo_performance']['negative'] += 1
            
            for error in self._error_header1_short_tag:
                self.issues['h1_tag_short'].add(error + "Tag is short than recommended value")
        else:
            self.performance['seo_performance']['positive'] += 1
        
        if self._error_header2_short_tag:
            self.performance['seo_performance']['negative'] += 1
            
            for error in self._error_header2_short_tag:
                self.issues['h2_tag_short'].add(error + "Tag is short than recommended value")
        else:
            self.performance['seo_performance']['positive'] += 1

    def generate_mail(self):
        
        if self.overall_positive_per < 75:
            hello = 'Hi There'

            html = """\
                <!DOCTYPE html>
                <html>

                <head>
                    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <meta http-equiv="X-UA-Compatible" content="IE=edge">
                    <meta name="format-detection" content="telephone=no">
                    <title>RankingBySEO</title>
                    <link href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700" rel="stylesheet">
                    <style>
                        body{font-family: 'Roboto', sans-serif;}
                        a { outline-style: none;text-decoration: none;}tr,td { padding: 0; } p {margin:0;}h1, h2, h3, h4, h5, h6{margin: 0;}
                        @media(max-width: 570px) {
                            .main_table {width: 100% !important; max-width: 100% !important; }.full {width: 100%!important; }.tab {  width: 100% !important; } }     
                    </style>
                </head>
                <body bgcolor="#f5f5f5" align="center">
                        <table class="main_table" border="0" cellpadding="0" cellspacing="0" width="600" align="center" style="background-color: #e0e0e0;border: 1px solid #ddd;">
                        <tbody  style="background: #FFF;">
                            <tr><td colspan="2" style="font-size:24px;padding:20px 20px 10px 20px;text-align: center;color: #000;">Audit Report</td></tr>
                            <tr><td colspan="2" style="font-size:18px;padding:0px 20px 20px 20px;text-align: center;"><a href='""" + self.hunt_url + """'  style="color:#2b94e1;">""" + self.hunt_url + """ </a></td></tr>
                            <tr><td colspan="2">
                                    <table width="80%" style="margin: 0px 0px 5px;border-color: #ebccd1;width: 80%; margin: 0 auto;color: #fff;border-bottom: 1px solid #ccc;">
                                        <tr><td style=""></td>
                                        </tr> </table> </td></tr>          
                            <tr><td colspan="2" style="font-size:16px;padding:20px 20px 10px 20px;text-align: left;color: #2b94e1;">""" + hello + """,</td></tr>
                            <tr><td colspan="2" style="padding: 0 20px 10px 25px; text-align: left;color: #000; font-size: 12px;line-height: 1.7;letter-spacing: 1px;">We have run an audit on your website about to trace your Perfomance and in """ + str(self.load_time) + """ we find out these facts.
                                </td></tr>
                            <tr><td width="30%" style="width:30% ;background: #2b94e1;">
                                    <table width="100%" style="background: #2b94e1;" cellpadding="0" cellspacing="0">
                                        <tr><td style="color: #FFF;text-align: left;padding: 10px 0px 10px 25px; font-size: 16px;"> Report Overview</td> </tr>
                                    </table>
                                </td>
                                <td width="70%" style="width:70%">
                                    <table width="100%" cellpadding="0" cellspacing="0">
                                        <tr style="background: #2da303;color: #FFF;text-align: left;"><td style=" padding: 10px 15px; font-size: 14PX;">""" + str(self.overall_positive_per) + """% SEO Friendly Structure</td></tr>
                                        <tr style="background: #da0505;color: #FFF;text-align: left;"><td style="padding: 10px 15px; font-size: 14PX;">""" + str(self.overall_negative_per) + """% Bad Result which affecting your Website Perfomance</td></tr>
                                    </table>
                                </td>
                            </tr>
                            <tr><td colspan="2" style="padding: 20px 20px 20px 25px; text-align: center;color: #000; font-size: 12px;line-height: 1.7;letter-spacing: 1px;">Here are some of Insights</td></tr>
            """

            if 'seo_performance' in self.performance:                        
                
                html += """<tr>
                    <td colspan="2" style="text-align: left; font-size:22px; padding: 20px 20px 20px 25px;">
                        <strong style="font-weight: 400;">  SEO Performance </strong>- &nbsp;  <span style="font-size: 14px;">""" + str(self.performance['seo_performance']['total_positive_weightage']) + """% Out of """ + str(self.performance['seo_performance']['total_weightage']) + """% of this Report.   </span>
                    </td>
                </tr>
                <tr><td colspan="2" style="padding: 0px 20px 10px 15px; border-bottom: 1px solid #ccc;"> 
                        <ul style="margin: 0; padding: 0; list-style: none; text-align: center;">
                """
                                        
                if 'schema_markup' in self.issues:   
                    if self.issues['schema_markup'] == 'Not Found':
                        color_code = '#ff0000' 
                    else : 
                        color_code = '#007ed6' 
                    html += """<li style="font-size: 14px;display: inline-block;width: 20%;margin: 10px;border: 1px solid #ccc;color: #000;padding: 10px 5px; text-align: center;">Schema Markup<br><span style="margin-top: 10px;color: """ + color_code + """;display: inline-block;font-weight: 500;font-size: 14px;">""" + self.issues['schema_markup'] + """</span></li>"""
                
                if 'analytics' in self.issues:    
                    if self.issues['analytics'] == 'Not Found':
                        color_code = '#ff0000' 
                    else : 
                        color_code = '#007ed6' 
                    html += """<li style="font-size: 14px;display: inline-block;width: 15%;margin: 10px;border: 1px solid #ccc;color: #000;padding: 10px 5px; text-align: center;">Analytics<br><span style="margin-top: 10px;color: """ + color_code + """;display: inline-block;font-weight: 500;font-size: 14px;">""" + self.issues['analytics'] +  """</span></li>"""
                
                if 'webmaster' in self.issues:
                    if self.issues['webmaster'] == 'Not Found':
                        color_code = '#ff0000' 
                    else : 
                        color_code = '#007ed6'
                    html += """<li style="font-size: 14px;display: inline-block;width: 15%;margin: 10px;border: 1px solid #ccc;color: #000;padding: 10px 5px; text-align: center;">Webmaster<br><span style="margin-top: 10px;color: """ + color_code + """;display: inline-block;font-weight: 500;font-size: 14px;">""" + self.issues['webmaster'] + """</span></li>"""
                
                if 'robots_txt' in self.issues:
                    if self.issues['robots_txt'] == 'Not Found':
                        color_code = '#ff0000' 
                    else : 
                        color_code = '#007ed6'
                    html += """<li style="font-size: 14px;display: inline-block;width: 15%;margin: 10px;border: 1px solid #ccc;color: #000;padding: 10px 5px; text-align: center;">Robots(.Txt)<br><span style="margin-top: 10px;color: """ + color_code + """;display: inline-block;font-weight: 500;font-size: 14px;">""" + self.issues['robots_txt'] + """</span></li>"""
                
                if 'sitemap' in self.issues:
                    if self.issues['sitemap'] == 'Not Found':
                        color_code = '#ff0000' 
                    else : 
                        color_code = '#007ed6'
                    html += """<li style="font-size: 14px;display: inline-block;width: 15%;margin: 10px;border: 1px solid #ccc;color: #000;padding: 10px 5px; text-align: center;">Sitemap<br><span style="margin-top: 10px;color: """ + color_code + """;display: inline-block;font-weight: 500;font-size: 14px;">""" + self.issues['sitemap'] + """</span></li>"""
                
                if 'meta' in self.issues:
                    if self.issue_count > 3:
                        html += """<li style="font-size: 14px;display: inline-block;width: 15%;margin: 10px;border: 1px solid #ccc;color: #545454;padding: 10px 5px;">Meta Tag<br><span   style="margin-top: 10px;color: #46ae00;display: inline-block;font-weight: 500;font-size: 14px;">BAD</span></li>"""
                    else:
                        html += """<li style="font-size: 14px;display: inline-block;width: 15%;margin: 10px;border: 1px solid #ccc;color: #545454;padding: 10px 5px;">Meta Tag<br><span  style="margin-top: 10px;color: #ff0000;display: inline-block;font-weight: 500;font-size: 14px;">VERY BAD</span></li>"""
                else:
                    html += """<li style="font-size: 14px;display: inline-block;width: 15%;margin: 10px;border: 1px solid #ccc;color: #545454;padding: 10px 5px;">Meta Tag<br><span style="margin-top: 10px;color: #007ed6;display: inline-block;font-weight: 500;font-size: 14px;">VERY GOOD</span></li>"""
                                
                                
                html += """</ul>
                    </td>
                </tr>"""
                    
                if self.performance['website_performance']:
                    html += """<tr>
                        <td colspan="2" style="text-align: left; font-size:22px; padding: 20px 20px 20px 25px;">
                            <strong style="font-weight: 400;">  Website Performance </strong>- &nbsp;  <span style="font-size: 14px;">""" + str(self.performance['website_performance']['total_positive_weightage']) + """% Out of """+ str(self.performance['website_performance']['total_weightage']) +"""% of this Report.   </span>
                        </td>
                    </tr>
                    <tr><td colspan="2" style="padding: 0px 20px 10px 15px; border-bottom: 1px solid #ccc;"> 
                                <ul style="margin: 0; padding: 0; list-style: none; text-align: center;">
                    """
                    if self.load_time <= 1:
                        html += """<li style="font-size: 14px;display: inline-block;width: 15%;margin: 10px;border: 1px solid #ccc;color: #545454;padding: 10px 5px;">Load Time<br><span style="margin-top: 10px;color: #007ed6;display: inline-block;font-weight: 500;font-size: 14px;">VERY GOOD</span></li>"""
                    elif self.load_time <= 3:
                        html += """<li style="font-size: 14px;display: inline-block;width: 15%;margin: 10px;border: 1px solid #ccc;color: #545454;padding: 10px 5px;">Load Time<br><span style="margin-top: 10px;color: #82bee8;display: inline-block;font-weight: 500;font-size: 14px;">GOOD</span></li>"""
                    elif self.load_time <= 5:
                        html += """<li style="font-size: 14px;display: inline-block;width: 15%;margin: 10px;border: 1px solid #ccc;color: #545454;padding: 10px 5px;">Load Time<br><span   style="margin-top: 10px;color: #46ae00;display: inline-block;font-weight: 500;font-size: 14px;">BAD</span></li>"""
                    else:
                        html += """<li style="font-size: 14px;display: inline-block;width: 15%;margin: 10px;border: 1px solid #ccc;color: #545454;padding: 10px 5px;">Load Time<br><span  style="margin-top: 10px;color: #ff0000;display: inline-block;font-weight: 500;font-size: 14px;">VERY BAD</span></li>"""

                    if 'ssl_issue' in self.issues:
                        if self.issues['ssl_issue'] == 'Not Found':
                            color_code = '#ff0000' 
                        else : 
                            color_code = '#007ed6'
                        html += """<li style="font-size: 14px;display: inline-block;width: 15%;margin: 10px;border: 1px solid #ccc;color: #000;padding: 10px 5px; text-align: center;">SSL<br><span style="margin-top: 10px;color: """ + color_code + """;display: inline-block;font-weight: 500;font-size: 14px;">""" + self.issues['ssl_issue'] + """</span></li>"""
                    
                    if self.issues['alt_tag']:
                        if self.issues['alt_tag'] == 'Not Found':
                            color_code = '#ff0000' 
                        else : 
                            color_code = '#007ed6'
                        html += """<li style="font-size: 14px;display: inline-block;width: 15%;margin: 10px;border: 1px solid #ccc;color: #000;padding: 10px 5px; text-align: center;">Alt Attrib<br><span style="margin-top: 10px;color: """ + color_code + """;display: inline-block;font-weight: 500;font-size: 14px;">""" + self.issues['alt_tag'] + """</span></li>"""
                    if self.issues['mobile_responsive']:
                        if self.issues['mobile_responsive'] != 'Responsive':
                            color_code = '#ff0000' 
                        else : 
                            color_code = '#007ed6'
                        html += """<li style="font-size: 14px;display: inline-block;width: 25%;margin: 10px;border: 1px solid #ccc;color: #000;padding: 10px 5px; text-align: center;">Mobile Responsive<br><span style="margin-top: 10px;color: """ + color_code + """;display: inline-block;font-weight: 500;font-size: 14px;">""" + self.issues['mobile_responsive'] + """</span></li>"""
                    if 'tag_repeated' in self.issues['meta']:
                        html += """<li style="font-size: 14px;display: inline-block;width: 15%;margin: 10px;border: 1px solid #ccc;color: #000;padding: 10px 5px; text-align: center;">Meta Repeat<br><span style="margin-top: 10px;color:#ff0000;display: inline-block;font-weight: 500;font-size: 14px;">BAD</span></li>"""
                                
                    
                    html += """        </ul>
                            </td>
                        </tr>
                    <tr>
                        <td colspan="2" style="font-size: 20px;font-weight: 600; text-align: left;padding: 20px 20px 10px 25px;">You've reached the limit of checked pages</td>
                    </tr>
                    <tr>
                        <td  colspan="2"  style="font-size: 14px;text-align: left;padding: 0px 20px 0px 25px; font-size: 15px; line-height: 1.3;">
                            Your custom limit of pages that can be crawled per audit has been reached. We recommend that you change your checked pages limit to audit all pages on your website, detect all issues, and get a full picture of your website's health. 
                        </td>
                    </tr>
                    <tr>
                        <td   colspan="2"  style="font-size: 12px;"><p style="display: inline-block;margin-bottom: 20px; border-bottom: 1px solid #ccc; padding: 20px;">If you do not wish to receive these newsletters in the future, please <a href="#">click here</a>.</p></td>
                    </tr>
                    <tr>
                        <td colspan="2">
                            <table width="100%" style="background: #d00000;" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="padding: 25px;">

                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr><td colspan="2" style="padding: 20px 20px 0px 20px; text-align: left;color: #000; font-size: 18px; font-weight: 500;line-height: 1.3;letter-spacing: 1px;">Thanks,</td></tr>
                    <tr> <td colspan="2" style="padding: 0px 20px 20px 20px; text-align: left;color: #000; font-size: 16px;line-height: 1.3;letter-spacing: 1px;">The RankingBySeo Team</td></tr>
                    <tr> <td colspan="2" style="padding: 0px 20px 0px 20px; text-align: left;color: #000; font-size: 14px;line-height: 1.7;letter-spacing: 1px;">Email: <a style="color:#2a94e0;" href="mailto:mail@rankingbyseo.com">mail@rankingbyseo.com</a></td></tr>
                    <tr> <td colspan="2" style="padding: 0px 20px 20px 20px; text-align: left;color: #000; font-size: 14px;line-height: 1.7;letter-spacing: 1px;">Twitter: <a style="color:#2a94e0;" href="https://www.twitter.com/rankingbyseo">@rankingbyseo</a></td></tr>

                </tbody>
            </table>
        </body>
        </html>
            """

        return html
    
    def check_ssl(self):
        #res = requests.get(self.hunt_url, cert='/path/server.crt', verify=True)
        #pprint(res)

        # connect to server and get certificate as binary (DER)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        url = re.compile(r"https?://")
        normal_url = url.sub('', self.hunt_url).strip().strip('/')
        pprint(normal_url)
        sock.connect((normal_url, 443))
        sslsock = ssl.wrap_socket(sock)
        cert_der = sslsock.getpeercert(True)

        # load binary certificate and get signature hash algorithm
        cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert_der)
        pprint(cert.get_signature_algorithm())
        sys.exit()

    def __del__(self):
        print("End")
        #self.server.close()

    def run(self):
        self.hunt_this()
        
        if self.hunted_html_domobj:
            
            schema_searched = re.search( r'schema.org', self.hunted_html_string, re.M)
            if schema_searched:
                self.issues['schema_markup'] = 'Not Found'
                self.performance['seo_performance']['negative'] += 1
            else:
                self.issues['schema_markup'] = 'Found'
                self.performance['seo_performance']['positive'] += 1
            
            anlytics_searched = re.search( r'UA-[0-9]{5,}-[0-9]{1,}', self.hunted_html_string, re.M)
            if anlytics_searched:
                self.issues['analytics'] = 'Not Found'
                self.performance['seo_performance']['negative'] += 1
            else:
                self.issues['analytics'] = 'Found'
                self.performance['seo_performance']['positive'] += 1
            
            webmaster_searched = re.search( r'google-site-verification', self.hunted_html_string, re.M)
            if webmaster_searched:
                self.issues['webmaster'] = 'Not Found'
                self.performance['seo_performance']['negative'] += 1
            else:
                self.issues['webmaster'] = 'Found'
                self.performance['seo_performance']['positive'] += 1

            
            """ if self.check_ssl():
                self.issues['ssl_issue'] = 'Found'
                self.performance['website_performance']['negative'] += 1
            else: 
                self.issues['ssl_issue'] = 'Not Found'
                self.performance['website_performance']['positive'] += 1 """
            
            if self.check_alt_tag():
                self.issues['alt_tag'] = 'Not Found'
                self.performance['website_performance']['negative'] += 1
            else:
                self.issues['alt_tag'] = 'Found'
                self.performance['website_performance']['positive'] += 1
            
            if self.check_responsive():
                self.issues['mobile_responsive'] = 'Not Responsive'
                self.performance['website_performance']['negative'] += 1
            else:
                self.issues['mobile_responsive'] = 'Responsive'
                self.performance['website_performance']['positive'] += 1
            
            if self.check_not_exist_link(self.hunt_url + '/robots.txt'):
                self.issues['robots_txt'] = 'Not Found'
                self.performance['seo_performance']['negative'] += 1
            else:
                self.issues['robots_txt'] = 'Found'
                self.performance['seo_performance']['positive'] += 1


            """ internal_links = self.check_internal_links()
            
            if len(internal_links) < 1:
                self.issues['internal_link'] = 'Not Found'
            else:
                self.issues['internal_link'] = 'Found'
            

            self.check_broken_links()

            if len(self.internal_broken_links) > 0:
                self.issues['internal_broken_links'] = 'Found'
            else: 
                self.issues['internal_broken_links'] = 'Not Found'

            if len(self.external_broken_links) > 0:
                self.issues['external_broken_links'] = 'Found'
            else: 
                self.issues['external_broken_links'] = 'Not Found' """
            
            self.get_meta_report()
            self.get_tag_report()

            self.overall_positive = 0
            self.overall_negative = 0
            
            for obj in self.performance:
                self.overall_positive = self.overall_positive + self.performance[obj]['positive']
                self.overall_negative = self.overall_negative + self.performance[obj]['negative']
            
            self.total = self.overall_positive + self.overall_negative
            self.overall_positive_per = int((self.overall_positive*100)/(self.total))
            self.overall_negative_per = 100 - self.overall_positive_per
            
            self.seo_total = 0
            self.seo_total = self.performance['seo_performance']['positive'] + self.performance['seo_performance']['negative']
            self.performance['seo_performance']['total_weightage'] = round((self.seo_total*100)/self.total, 0)
            self.performance['seo_performance']['total_positive_weightage'] = round((self.performance['seo_performance']['positive']*100)/self.total, 0)
            
            self.website_total = 0
            self.website_total = self.performance['website_performance']['positive'] + self.performance['website_performance']['negative']
            self.performance['website_performance']['total_weightage'] = round((self.website_total*100)/self.total, 0)
            self.performance['website_performance']['total_positive_weightage'] = round((self.performance['website_performance']['positive']*100)/self.total, 0)

            if 'meta' in self.issues:
                if 'tag_missing' in self.issues['meta']:
                    missing_count = len(self.issues['meta']['tag_missing'])
                else:
                    missing_count = 0

                if 'tag_lengthy' in self.issues['meta']:
                    tag_lengthy = len(self.issues['meta']['tag_lengthy'])
                else:
                    tag_lengthy = 0

                if 'tag_short' in self.issues['meta']:
                    tag_short = len(self.issues['meta']['tag_short'])
                else:
                    tag_short = 0

                if 'tag_repeated' in self.issues['meta']:
                    tag_repeated = len(self.issues['meta']['tag_repeated'])
                else:
                    tag_repeated = 0

                if 'h1_tag_repeated' in self.issues:
                    h1_tag_repeated = len(self.issues['h1_tag_repeated'])
                else:
                    h1_tag_repeated = 0

                if 'h1_tag_lengthy' in self.issues:
                    h1_tag_lengthy = len(self.issues['h1_tag_lengthy'])
                else:
                    h1_tag_lengthy = 0

                if 'h1_tag_short' in self.issues:
                    h1_tag_short = len(self.issues['h1_tag_short'])
                else:
                    h1_tag_short = 0

                if 'h2_tag_repeated' in self.issues:
                    h2_tag_repeated = len(self.issues['h2_tag_repeated'])
                else:
                    h2_tag_repeated = 0

                if 'h2_tag_lengthy' in self.issues:
                    h2_tag_lengthy = len(self.issues['h2_tag_lengthy'])
                else:
                    h2_tag_lengthy = 0

                if 'h2_tag_short' in self.issues:
                    h2_tag_short = len(self.issues['h2_tag_short'])
                else:
                    h2_tag_short = 0
                                            
                self.issue_count = missing_count + tag_lengthy + tag_short + tag_repeated + h1_tag_repeated + h1_tag_lengthy + h1_tag_short + h2_tag_repeated + h2_tag_lengthy + h2_tag_short 

            if self.hunt_email != '':
                mail_content = self.generate_mail()
                self.send_mail(self.hunt_email, FROM_TITLE, MAIL_SUBJECT, mail_content)
            else:
                return self
            
            return True
    
        else:
            return False






import urllib2
import CommonFunctions
common = CommonFunctions
from xml.dom import minidom
import globalvar
import simplejson as json
import xbmcaddon

url_base='http://www.arte.tv/papi/tvguide-flow/sitemap/feeds/videos/F.xml' 

def fix_text(text):
    print
    return text.replace('&amp;','&').encode('utf-8').replace('&#039;',' ')

def list_shows(channel,folder):
    shows=[]
    d=dict()
    
    if folder=='none':
        xml = open(globalvar.CATALOG_ARTE).read()
        url=common.parseDOM(xml, "url")
        for i in range(0, len(url)):
            categoryTab=common.parseDOM(url[i], "video:category")
            if len(categoryTab)>0:
                category=fix_text(categoryTab[0])
                if category not in d:
                    shows.append( [channel,category,category,'','folder'] )
                    d[category]=category
    else:
        xml = open(globalvar.CATALOG_ARTE).read()
        url=common.parseDOM(xml, "url")
        for i in range(0, len(url)):
            titleTab=common.parseDOM(url[i], "video:title")
            if len(titleTab)>0:
                title=fix_text(titleTab[0])
            categoryTab=common.parseDOM(url[i], "video:category")
            if len(categoryTab)>0:
                if(fix_text(categoryTab[0])==folder and title not in d):                   
                    shows.append( [channel,title,title,'','shows'] )
                    d[title]=title
    return shows

def getVideoURL(channel,url):
    url=urllib2.unquote(url)
    results = urllib2.urlopen(url).read()
    jsonobj = json.loads(results)
    # Read quality from settings
    if xbmcaddon.Addon().getSetting('video_quality') == '0':
        quality = 'RTMP_EQ_1'
    else:
        quality = 'RTMP_SQ_1'
    streamer = jsonobj['videoJsonPlayer']['VSR'][quality]['streamer']
    endpoint = jsonobj['videoJsonPlayer']['VSR'][quality]['url']
    return streamer + endpoint
    
def list_videos(channel,show_title):
    videos=[]
    xml = open(globalvar.CATALOG_ARTE).read()
    url=common.parseDOM(xml, "url")
    for i in range(0, len(url)):
        video_url=''
        name=''
        image_url=''
        date=''
        duration=''
        views=''
        desc=''
        rating=''
        titleTab=common.parseDOM(url[i], "video:title")
        if len(titleTab)>0:
            title=fix_text(titleTab[0])
        if(title==show_title):
            tmpTab=common.parseDOM(url[i], "video:publication_date")
            if len(tmpTab)>0:
                date=tmpTab[0][:10]
            tmpTab=common.parseDOM(url[i], "video:duration")
            if len(tmpTab)>0:
                duration=tmpTab[0]
            tmpTab=common.parseDOM(url[i], "video:view_count")
            if len(tmpTab)>0:
                views=tmpTab[0]
            tmpTab=common.parseDOM(url[i], "video:rating")
            if len(tmpTab)>0:
                rating=tmpTab[0]
            start = url[i].find('MasterPlugin.feedurl=')
            end = url[i].find('&amp;MasterPlugin.required=')
            video_url = url[i][start+21:end]
            descriptionTab=common.parseDOM(url[i], "video:description")
            if len(descriptionTab)>0:
                name=fix_text(descriptionTab[0])
                desc=fix_text(descriptionTab[0])
            picTab=common.parseDOM(url[i], "video:thumbnail_loc")
            if len(picTab)>0:
                image_url=picTab[0]
            infoLabels={ "Title": name,"Plot":desc,"Aired":date,"Duration": duration, "Year":date[:4]}   
            videos.append( [channel, video_url, name, image_url,infoLabels,'play'] )
    return videos
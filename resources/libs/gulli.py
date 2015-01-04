import urllib2
import CommonFunctions
common = CommonFunctions
import xml.dom.minidom
import re

# url_base='http://sslreplay.gulli.fr/replay/api?call=%7B%22api_key%22%3A%22andphone_72abef4bfc0c64d99b87b939ad32edf7%22%2C%22method%22%3A%22programme.getLatestEpisodes%22%2C%22params%22%3A%7B%22category_id%22%3A%22$$CATEG$$%22%2C%22episode_image_thumb%22%3A%5B285%2C213%5D%2C+%22episode_image_thumb_fiche%22%3A%5B0%2C0%5D%2C+%22program_image_thumb%22%3A%5B540%2C405%5D%2C+%22episode_image_fiche%22%3A%5B1080%2C810%5D%7D%7D'
# url_basf='http://sslreplay.gulli.fr/replay/api?call=%7B%22api_key%22%3A%22andphone_72abef4bfc0c64d99b87b939ad32edf7%22%2C%22method%22%3A%22programme.getLatestEpisodes%22%2C%22params%22%3A%7B%22category_id%22%3A%22emissions%22%2C%22episode_image_thumb%22%3A%5B285%2C213%5D%2C+%22episode_image_thumb_fiche%22%3A%5B0%2C0%5D%2C+%22program_image_thumb%22%3A%5B540%2C405%5D%2C+%22episode_image_fiche%22%3A%5B1080%2C810%5D%7D%7D'
# url_basd='http://sslreplay.gulli.fr/replay/api?call=%7B%22api_key%22%3A%22andphone_72abef4bfc0c64d99b87b939ad32edf7%22%2C%22method%22%3A%22programme.getLatestEpisodes%22%2C%22params%22%3A%7B%22category_id%22%3A%22series%22%2C%22episode_image_thumb%22%3A%5B285%2C213%5D%2C+%22episode_image_thumb_fiche%22%3A%5B0%2C0%5D%2C+%22program_image_thumb%22%3A%5B540%2C405%5D%2C+%22episode_image_fiche%22%3A%5B1080%2C810%5D%7D%7D'
WEBSITE = "http://replay.gulli.fr"
ALL_SHOWS = "http://replay.gulli.fr/AaZ"
debug_mode = False

def list_shows(channel,folder):
    shows=[]
    soup   = get_soup(WEBSITE) 
    html   = soup.decode("utf-8")
    smenu0 = common.parseDOM(html,"dd",attrs={"id":u"smenu0"}) [0]
    ul     = common.parseDOM(smenu0,"li")
    all_videos = 'Tous les replays'
    shows.append( [channel, ALL_SHOWS, all_videos.encode("utf-8"),'','shows'] )
    for  li in ul :
        if debug_mode :
            print "li :"+li.encode("utf-8")
        url_categorie_pattern  = common.parseDOM(li,"a",ret="href") [0]
        url_categorie          = url_categorie_pattern.encode("utf-8")            
        if debug_mode :
            print "URL : "+url_categorie
        name_categorie_pattern = common.parseDOM(li,"span",attrs={"class":u"btn_repeat"}) [0]
        name_categorie         = name_categorie_pattern.encode("utf-8")
        if debug_mode :
            print "NOM : "+name_categorie
        shows.append( [channel, url_categorie, name_categorie,'','shows'] )
    
    return shows

def getVideoURL(channel,url):
    embed_url  = get_embed_url(url)
    if embed_url :
        video_url = get_video_url(embed_url)
    return video_url

def get_embed_url(url):
    soup  = get_soup(url)
    html  = soup.decode("utf-8")
    src   = re.findall("""jQuery\(\'.flashcontent\'\)\.html\(\'<iframe src=\"(.+?)\"""",html)
    if src :
        return src[0]
    else :
        return False

def get_video_url(url):
    soup           = get_soup(url)
    html           = soup.decode("utf-8")
    file_url = re.findall("""file: '(.+?)',""", html)
    if file_url :
        return file_url[0]
    else :
        return False
        
def list_videos(channel,category):
    videos=[]
    soup                        = get_soup(category)
    html                        = soup.decode("utf-8")
    wrapper_pattern             = common.parseDOM(html,"div",attrs={"id":u"wrapper"}) [0]
    ul_liste_resultats_pattern  = common.parseDOM(wrapper_pattern,"ul",attrs={"class":"liste_resultats"})
    for ul in ul_liste_resultats_pattern :
        li_pattern_list = common.parseDOM(ul,"li")
        for li_pattern in li_pattern_list :
            image_url_pattern   = common.parseDOM(li_pattern,"img",ret="src") [0]
            image_url           = image_url_pattern.encode("utf-8")
            if debug_mode :
                print "image_url :"+image_url
            episode_url_pattern = common.parseDOM(li_pattern,"a",ret="href") [0]
            episode_url         = episode_url_pattern.encode("utf-8")
            if debug_mode :
                print "episode_url : "+episode_url
            titre1_pattern      = common.parseDOM(li_pattern,"strong") [0]
            titre1              = titre1_pattern.encode("utf-8")
            if debug_mode :
                print "titre1 :"+titre1
            p_list_pattern      = common.parseDOM(li_pattern,"p") [0]
            titre2_pattern      = common.parseDOM(p_list_pattern,"span") [0]
            titre2_tmp          = titre2_pattern.encode("utf-8")
            titre2_tmp          = "//".join(titre2_tmp.split("""<br/>"""))
            titre2_tmp          = "".join(titre2_tmp.split("\n"))
            titre2_tmp          = "".join(titre2_tmp.split("\s"))
            titre2_tmp          = "".join(titre2_tmp.split("\t"))
            titre2_tmp          = "".join(titre2_tmp.split("\r"))
            titre2_tmp          = "".join(titre2_tmp.split("\f"))
            titre2_tmp          = "".join(titre2_tmp.split("\v"))
            titre2              = " ".join(titre2_tmp.split("&nbsp;"))
            if debug_mode :
                print "titre2 : "+titre2                                
            titre_episode       = titre1 +" : "+ titre2
            if debug_mode :
                print "titre_episode :"+titre_episode
            infoLabels={ "Title": titre1,"Plot":titre_episode} 
            videos.append( [channel, episode_url, titre1, image_url,infoLabels,'play'] )
    return videos

def get_soup(url):
    req  = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 5.1; rv:15.0) Gecko/20100101 Firefox/15.0.1')           
    soup = urllib2.urlopen(req).read()
    if (debug_mode):
        print str(soup)
    return soup 
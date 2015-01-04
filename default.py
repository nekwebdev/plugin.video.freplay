import sys
import os, os.path
import urllib
import urlparse

import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon

import resources.libs.globalvar as globalvar
import resources.libs.utils as utils
import resources.libs.favourites as favourites

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def add_Channel(idChannel,nameChannel):
    url = build_url({'mode': 'folder', 'channel': idChannel, 'param':'none'})
    li = xbmcgui.ListItem(nameChannel, iconImage=os.path.join( globalvar.MEDIA, idChannel+".png"))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True)

def buildShowsList(videos):
    for chan,video_url, video_title, video_icon,infoLabels,video_mode in videos:
        li = xbmcgui.ListItem(video_title, iconImage=video_icon,thumbnailImage=video_icon,path=video_url)
        if video_mode=='play':
            li.setInfo( type='Video', infoLabels=infoLabels)            
            li.setProperty('IsPlayable', 'true')
            li.addContextMenuItems([ ('Download', 'XBMC.RunPlugin(%s?mode=dl&channel=%s&param=%s&name=%s)' % (sys.argv[0],200,video_url.encode('utf-8'),video_title)),
                     ], replaceItems=True)
        url = build_url({'mode': video_mode, 'channel': chan, 'param':video_url})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=False)
        xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.setPluginCategory(addon_handle, 'episodes' )
        xbmcplugin.setContent(addon_handle, 'episodes')
    xbmc.executebuiltin('Container.SetViewMode(' + globalvar.VIEWID + ')')
    if channel=='favourites' and param=='unseen':
        notify('Check/Uncheck "Hide Watched" in the left panel',0)
        
def notify(text,channel):
    time = 3000  #in miliseconds 
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('FReplay',text, time, os.path.join( globalvar.ADDON_DIR, "icon.png")))

    
mode = args.get('mode', None)

utils.init()

print xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Files.GetFileDetails", "params": { "file": "1" }, "id": 1}')

if mode is None:
    notify('Downloading Catalogs',1)
    utils.firstRun()
    for item in globalvar.ordered_channels:  
        add_Channel(item,globalvar.channels[item][0])
    
    xbmcplugin.endOfDirectory(addon_handle)
else:    
    channel = args['channel'][0]
    param = args['param'][0]
    print 'FReplay:'+'mode='+mode[0]+' | channel=' + str(channel)+' | param=' + param
    if mode[0]=='folder':
        if globalvar.channels[channel][2] and param=='none':
            url = build_url({'mode': 'Search', 'channel': channel,'param':'none'})
            li = xbmcgui.ListItem('Search','')
            li.addContextMenuItems([], replaceItems=True)
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True)
                
        for chan,folder_param, folder_title, folder_icon, mode in globalvar.channels[channel][1].list_shows(channel,param):
            url = build_url({'mode': mode, 'channel': chan, 'param':folder_param})
            li = xbmcgui.ListItem(folder_title, iconImage=folder_icon)
            #Contextual Menu
            li.addContextMenuItems([], replaceItems=True)
            if mode=='shows' and channel!='favourites':
                li.addContextMenuItems([ ('Add to FReplay Favourites', 'XBMC.RunPlugin(%s?mode=bkm&action=add&channel=%s&param=%s&display=%s)' % (sys.argv[0],chan,folder_param,folder_title)),
                         ], replaceItems=True)
            if mode=='shows' and channel=='favourites':
                li.addContextMenuItems([ ('Remove from Favourites', 'XBMC.RunPlugin(%s?mode=bkm&action=rem&channel=%s&param=%s&display=%s)' % (sys.argv[0],chan,folder_param,folder_title)),
                         ], replaceItems=True)
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True)
    elif mode[0]=='shows':
        buildShowsList(globalvar.channels[channel][1].list_videos(channel,param))
    elif mode[0]=='play':
        url=globalvar.channels[channel][1].getVideoURL(channel,param)
        item = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(addon_handle, True, item)  
    elif mode[0]=='Search':
        keyboard = xbmc.Keyboard('','Enter the search text')
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            buildShowsList(globalvar.channels[channel][1].list_videos(channel,keyboard.getText()))
    elif mode[0]=='bkm':
        if args['action'][0]=='add':#Add to Favourites
            display = args['display'][0]
            result=favourites.add_favourite(channel,param,display)
        else:
            result=favourites.rem_favourite(channel,param)
        notify(result,channel)
    elif mode[0]=='dl':
        notify('Not implemented yet',0)
    xbmcplugin.endOfDirectory( handle=int(addon_handle), succeeded=True, updateListing=False)
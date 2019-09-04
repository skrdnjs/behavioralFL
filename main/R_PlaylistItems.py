from BaseHandler import BaseHandler
from BehaveLog import Behavlog
from apiclient.errors import HttpError
from apiclient.discovery import build

import random
import google.oauth2.credentials

import Keys

class R_PlayListItems():

    session = None
    request = None
    def __init__(self, pSession, pRequest):
        self.session = pSession
        self.request = pRequest

    def get(self):
        try:

            log_query = Behavlog.query(Behavlog.remoaddr == str(self.request.remote_addr)).order(-Behavlog.startdate).fetch(1)

            thislog = None

            onlyone = True
            for alog in log_query:
                if onlyone:
                    thislog = alog
                    onlyone = False

            try:

                command = self.session['command']

                credentials = google.oauth2.credentials.Credentials(**self.session['credentials'])

                youtube = build(Keys.YOUTUBE_API_SERVICE_NAME,Keys.YOUTUBE_API_VERSION,credentials=credentials)

                if command == 'playlistitem':
                    # pPlaylistid = self.session['playlistId']
                    # plistitems = youtube.playlistItems().list(playlistId=pPlaylistid,part='id,snippet',maxResults=5).execute()

                    sel = self.session['sel']
                    
                    if sel == 0:

                        uploadsid = self.session['uploads']
                        plistitems = youtube.playlistItems().list(playlistId=uploadsid,part='id,snippet',maxResults=5).execute()
                        videos = []
                        itemids = []

                        for item in plistitems.get('items',[]):
                            if item.get('snippet').get('resourceId').get('kind') == 'youtube#video':
                                # print item.get('snippet').get('resourceId').get('videoId')
                                videos.append('%s' % (item.get('snippet').get('resourceId').get('videoId')))
                                itemids.append('%s' % (item.get('id')))

                        if len(itemids) > 0:
                            idx = random.randrange(0,len(itemids))
                            self.session['videoid'] = videos[idx]
                            self.session['playlistitemid'] = itemids[idx]
                            self.session['videomine'] = True
                            self.session['cstate'] = 4
                        else:
                            pass

                    elif sel == 1:

                        pPlaylistid = self.session['playlistId']
                        plistitems = youtube.playlistItems().list(playlistId=pPlaylistid,part='id,snippet',maxResults=5).execute()
                        videos = []
                        itemids = []
                        for item in plistitems.get('items',[]):
                            if item.get('snippet').get('resourceId').get('kind') == 'youtube#video':
                                # print item.get('snippet').get('resourceId').get('videoId')
                                videos.append('%s' % (item.get('snippet').get('resourceId').get('videoId')))
                                itemids.append('%s' % (item.get('id')))

                        if len(itemids) > 0:
                            idx = random.randrange(0,len(itemids))
                            self.session['videoid'] = videos[idx]
                            self.session['playlistitemid'] = itemids[idx]
                            self.session['videomine'] = False
                            self.session['cstate'] = 7
                        else:
                            pass

                    thislog.vector[2] = 1

                elif command == 'playlistitemin':

                    pPlaylistid = self.session['playlistId']
                    videoid = self.session['videoid']
                    body = {
                        'snippet' : {
                            'playlistId' : pPlaylistid, 
                            'resourceId' : {
                                'kind':'youtube#video',
                                'videoId':videoid
                            }
                        }
                    }

                    youtube.playlistItems().insert(part='snippet',body=body).execute()
                    self.session['cstate'] = 14

                    thislog.vector[3] = 1

                elif command == 'playlistitemdel':
                    playlistitemid = self.session['playlistitemid']
                    youtube.playlistItems().delete(id=playlistitemid).execute()

                    thislog.vector[12] = 1

                elif command == 'playlistitemupdate':
                    pPlaylistid = self.session['playlistId']
                    playlistitemid = self.session['playlistitemid']
                    videoid = self.session['videoid']

                    body = {
                        'id' : playlistitemid,
                        'snippet' : {
                            'playlistId' : pPlaylistid,
                            'resourceId' : {
                                'kind':'youtube#video',
                                'videoId': videoid 
                            },
                            'position' : 0
                        }
                    }

                    youtube.playlistItems().update(part='snippet',body=body).execute()

                    thislog.vector[11] = 1

            except HttpError, e:
                thislog.sflabel = True
                print(e)
                print("http error")
                raise HttpError
                #self.response.write('<html><body><p>http error</p></body></html>')
            finally:
                thislog.put()

        except KeyError:
            print("KeyError on plistitem")
            #self.response.status_int = 401
            #self.response.write('<html><body><p>401 unauthorized access</p></body></html>')
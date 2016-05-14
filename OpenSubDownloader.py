from os import remove
from base64 import b64decode
from subprocess import check_output
from xmlrpclib import Server
import gzip

# TODO code documentation/cleanup
# TODO support arguments (login, langage, ...)

# read in the file(s) for which subtitles are needed
series = check_output('cd ~/Downloads/Torrents/SERIES && zenity --file-selection --multiple',
                      shell=True).rstrip().split("|")

server = Server('http://api.opensubtitles.org/xml-rpc')
loginInfo = server.LogIn('', '', 'en', 'OSTestUserAgent')
token = loginInfo['token']
# TODO error handling
language = 'eng'  # TODO language input from user
# TODO directory handling (arg?)

for serie in series:
    name = serie.split('/')[-1]
    print 'name', name
    # TODO request personal uagent
    subResults = server.SearchSubtitles(token, [{'sublanguageid': language, 'query': name}])
    subs = ''
    i = 0
    print 'subresults', subResults
    for sub in subResults['data']:
        print 'found subtitles', sub
        subs += ' ' + str(i)
        subs += ' \'' + sub['SubFileName'] + '\''
        i += 1
    if i == 0 :
        check_output('zenity --error --text=\'No subtitles found for video file: <b>%s</b>\'' % name, shell=True)
    else:
        chosensub = 0
        # noinspection PyBroadException
        try:
            chosensub = int(check_output("cd ~/Downloads/Torrents/SERIES && zenity --text='Video file: <b>%s</b>' "
                                         "--height=570 --width=500 --list --column=ID --column=Subtitle%s" % (name, subs),
                                         shell=True).rstrip().split("|")[0])
        except:
            print 'canceled or other error'
            continue
        print chosensub
        b64zipdata = server.DownloadSubtitles(token, [subResults['data'][chosensub]['IDSubtitleFile']])  # TODO replace arguments with user input
        print b64zipdata
        if int(b64zipdata['status'].split(' ')[0]) != 200 :
            check_output('zenity --error --text=\'%s\'' % b64zipdata['status'])
            continue
            # TODO error handling sufficient?
        zipdata = b64decode(b64zipdata['data'][0]['data'])
        with open('%s.gz' % name[:-4], 'w') as zipfile:
            zipfile.write(zipdata)

        with gzip.open('%s.gz' % name[:-4], 'rb') as infile:
            with open('%s.srt' % name[:-4], 'w') as outfile:
                for line in infile:
                    outfile.write(line)

        remove('%s.gz' % name[:-4])


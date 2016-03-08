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
    # TODO change windows size
    chosensub = int(check_output('cd ~/Downloads/Torrents/SERIES && zenity --list --column=ID --column=Subtitle%s' % subs,
                             shell=True).rstrip().split("|")[0])
    print chosensub
    b64zipdata = server.DownloadSubtitles(token, [subResults['data'][chosensub]['IDSubtitleFile']])  # TODO replace arguments with user input
    # TODO error handling
    zipdata = b64decode(b64zipdata['data'][0]['data'])
    with open('%s.gz' % name[:-4], 'w') as zipfile:
        zipfile.write(zipdata)

    with gzip.open('%s.gz' % name[:-4], 'rb') as infile:
        with open('%s.srt' % name[:-4], 'w') as outfile:
            for line in infile:
                outfile.write(line)

    remove('%s.gz' % name[:-4])


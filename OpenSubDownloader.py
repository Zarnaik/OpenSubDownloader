from os import remove
from base64 import b64decode
from subprocess import check_output
from xmlrpclib import Server
import gzip

# TODO document code

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
    chosensub = int(check_output('cd ~/Downloads/Torrents/SERIES && zenity --list --column=ID --column=Subtitle%s' % subs,
                             shell=True).rstrip().split("|")[0])
    print chosensub
    b64zipdata = server.DownloadSubtitles(token, [subResults['data'][chosensub]['IDSubtitleFile']])  # TODO replace arguments with user input
    # TODO error handling
    print 'b64zipdata', b64zipdata
    zipdata = b64decode(b64zipdata['data'][0]['data'])
    # print 'zipdata', zipdata
    zipfile = gzip.open('%s.gz' % name[:-4], 'w')
    zipfile.write(zipdata)
    zipfile.close()
    zipfile = gzip.open('%s.gz' % name[:-4], 'r')
    filedata = zipfile.read()
    # print 'files', filedata
    subtitle = open('%s.srt' % name[:-4], 'w')
    subtitle.write(filedata)
    subtitle.close()
    zipfile.close()
    remove('%s.gz' % name[:-4])


# Temporary documentation

# array SearchSubtitles( $token, array(
# array('sublanguageid' => $sublanguageid, 'moviehash' => $moviehash,
# 'moviebytesize' => $moviesize, imdbid => $imdbid, query => 'movie name', "season" => 'season number',
# "episode" => 'episode number', 'tag' => tag ),array(...)), array('limit' => 500))

# array DownloadSubtitles( $token, array($IDSubtitleFile, $IDSubtitleFile,...) )

#!/usr/bin/python
from os import remove
from base64 import b64decode
from subprocess import check_output
from xmlrpclib import Server
import gzip

# TODO code documentation/cleanup
# TODO support arguments (login, langage, ...)

# read in the file(s) for which subtitles are needed
series = check_output('zenity --file-selection --multiple',
                      shell=True).rstrip().split("|")

server = Server('http://api.opensubtitles.org/xml-rpc')
loginInfo = server.LogIn('', '', 'en', '0penSubDL')
token = loginInfo['token']
# TODO error handling
language = 'eng'  # TODO language input from user
# TODO directory handling (arg?)

for serie in series:
    name = serie.split('/')[-1]
    saveName = serie[:-3]
    searchName = name
    print 'name', name

    while True:
        subResults = server.SearchSubtitles(token, [{'sublanguageid': language, 'query': searchName}])
        if len(subResults['data']) == 0 :
            try:
                check_output('zenity --question --text=\'No subtitles found for the query: <b>%s</b>\\n\\nContinue?\'' % searchName, shell=True)
                break
            except:
                searchName = check_output('zenity --entry --text=\'Please enter the name you would like to search with.\' --entry-text=%s' % name, shell=True)
                continue
        else:
            break;

    subs = ''
    i = 0
    print '#subs:', len(subResults['data']), ' *subresults', subResults
    for sub in subResults['data']:
        print 'found subtitles', sub
        subs += ' ' + str(i)
        subs += ' \'' + sub['SubFileName'] + '\''
        i += 1

    if i == 0:  # if no subs were found and the user chose to continue, don't show an empty list
        continue

    try:
        chosensub = int(check_output("zenity --text='Video file: <b>%s</b>' "
                                     "--height=570 --width=500 --list --column=ID --column=Subtitle%s" % (name, subs),
                                     shell=True).rstrip().split("|")[0])
    except:
        print 'Canceled or other error due to not selecting a subtitle before continuing'
        continue

    print chosensub
    b64zipdata = server.DownloadSubtitles(token, [subResults['data'][chosensub]['IDSubtitleFile']])  # TODO replace arguments with user input
    print b64zipdata
    if int(b64zipdata['status'].split(' ')[0]) != 200:
        check_output('zenity --error --text=\'%s\'' % b64zipdata['status'])
        continue
        # TODO error handling sufficient?
    zipdata = b64decode(b64zipdata['data'][0]['data'])
    with open('%sgz' % saveName, 'w') as zipfile:
        zipfile.write(zipdata)

    with gzip.open('%sgz' % saveName, 'rb') as infile:
        with open('%ssrt' % saveName, 'w') as outfile:
            for line in infile:
                outfile.write(line)

    remove('%sgz' % saveName)


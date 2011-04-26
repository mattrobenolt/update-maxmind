#!/usr/bin/env python

import sys
import urllib2
import datetime
import subprocess
from os.path import join, getmtime
from optparse import OptionParser

# blah blah blah
__version__ = "0.1.0"
__author__  = "Matt Robenolt <root@drund.com>"

# MaxMind GeoIP library urls
GEOIP_COUNTRY = "http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz"
GEOIP_CITY    = "http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz"

# Itty bitty class so we can make a HEAD request
class HeadRequest(urllib2.Request):
    def get_method(self): return "HEAD"
    
def now_str():
    fmt = "%d/%b/%Y %H:%M:%S"
    
    return "[%s] " % datetime.datetime.strftime(datetime.datetime.now(), fmt)

def main(install_dir):
    for url in (GEOIP_COUNTRY, GEOIP_CITY):
        dat_name = url.split("/")[-1]
        dat_name = dat_name.rstrip(".gz")
        dat_path = join(install_dir, dat_name)
        
        download = False # flag to determine if we need to download a new version or not
        
        # Let's first check the mtime of the current file to see when it was last modified
        try:
            mtime = getmtime(dat_path)
        except OSError:
            mtime = 0
            download = True
            print now_str()+"File [%s] does not exist!" % dat_path
        
        # if the file existed, let's check the Last-Modified timestamp of the remote file
        if mtime > 0:
            try:
                print now_str()+"Checking Last-Modified of %s..." % url
                response = urllib2.urlopen(HeadRequest(url))
                last_modified = response.info().getheader("last-modified")
                if last_modified:
                    last_modified = datetime.datetime.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")
                    if last_modified > datetime.datetime.fromtimestamp(mtime):
                        print now_str()+"There is a newer version on the remote server!!"
                        download = True
                else:
                    # Last-Modified header doesn't exist, download just to be safe.
                    download = True
            except urllib2.URLError:
                print now_str()+"Site broke. Skipping. :("
                continue
            
        if download:
            print now_str()+"Downloading new version..."
            
            try:
                uncompressed = urllib2.urlopen(url).read()
            except urllib2.URLError:
                print now_str()+"Can't download the file. Skipping. :("
                continue
            
            print now_str()+"Download complete."
            try:
                print now_str()+"Unpacking..."
                p = subprocess.Popen(["gunzip", "-f", "-c"], shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
                output = p.communicate(input=uncompressed)[0]
            except:
                print now_str()+"Error uncompressing data."
                continue
            
            try:
                print now_str()+"Saving..."
                fp = open(dat_path, 'wb')
                fp.write(output)
            except IOError:
                print now_str()+"Error saving file. :("
                continue
            finally:
                try:
                    fp.close()
                except:
                    pass
            
            print now_str()+"Updated %s successfully!" % dat_name
            
        else:
            print now_str()+"We have the latest version of %s, skipping." % dat_name

if __name__ == "__main__":
    parser = OptionParser(usage="%prog DIRECTORY", version=__version__)
    (opts, args) = parser.parse_args()
    
    # Require one, and only one argument. The directory to save the files into.
    if len(args) < 1 or len(args) > 1:
        parser.print_help()
    else:
        main(args[0])
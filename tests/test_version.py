import git
import os
import sys
from urllib.request import urlopen, URLError

selfhash = open("version.txt","r").readline()

def internet_on():
    try:
        response=urlopen('http://github.com/UCLHp/Spot_Analysis',timeout=20)
        return True
    except URLError as err: pass
    return False

if internet_on():
    g = git.cmd.Git()
    blob = g.ls_remote("https://github.com/UCLHp/Spot_Analysis").splitlines()
    for line in blob:
        if 'refs/heads/master' in line:
            githash = line[0:40]
    if not githash == selfhash:
        print('Please check latest version on GitHub')
    else:
        print("Version Confirmed")
else:
    print('No internet connection detected, cannot check latest release \n'
          'Please check you are using the correct executable version \n')

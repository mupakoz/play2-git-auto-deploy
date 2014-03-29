# This is a script for automated play application deploy.
# The script checks for the changes using git.
# If any new commit was pushed, the script loads 
# the application from /target/universal/ dir, unzips it and starts the app.
# To make it work you should deploy your app using 'play dist' command,
# and make sure the /target/universal/ directory is added to your repo.
# The script uses GitPython. 
from git import *
import sys, os, signal, errno, subprocess, os.path, glob, zipfile, shutil
import time
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('autoGitDeploy.conf')

DESTINATION_DIRECTORY = parser.get('app', 'destination_directory')
APP_DIRECTORY = parser.get('app', 'play_app_directory')
APP_NAME = parser.get('app', 'app_name')
repo = Repo(APP_DIRECTORY)
git = repo.git

# Main script loop
def main():
    while True:
        if isPullNeeded():
            print ('Pull needed')
            git.pull()
            killOldAppIfNeeded()
            print('Starting new application')
            unzipAndStartNew()
        else:
            print ('Pull not needed')
        time.sleep(5)

# Checks if changes in repo based on last commit hash
def isPullNeeded():
    local = git.rev_parse('HEAD')
    remote = git.ls_remote('-h','origin','master').split()[0]
    return local!=remote;

# Kills old app if running
def killOldAppIfNeeded():
    try:
        pid = runningPid()
        if pidAlive(pid):
            print('Closing application')
            os.kill(pid, signal.SIGTERM)
            #leave 3 seconds to terminate properly
            time.sleep(5)
            print('Killing application')
            os.kill(pid, signal.SIGKILL)
        else:
            # No running instance to term or kill
            if (isPidFile()):
                print('Removing pid file')
                # we need to remove the file if there is one, otherwise play will not start
                deletePidFile()
    except IOError as e:
        # No PID file found, no need to worry
        pass
    except OSError as e:
        print('No process to kill!')

# Is given pid running
def pidAlive(pid):
    try:
        os.kill(pid, 0)
    except OSError, err:
        if err.errno == errno.ESRCH:
            return False
    return True       

# Reads running application pid from file
def runningPid():
    file = open(DESTINATION_DIRECTORY+"RUNNING_PID", "r")
    content = file.read()
    pid = int(content)
    file.close()
    return pid

def isPidFile():
    return os.path.isfile(DESTINATION_DIRECTORY+"RUNNING_PID")

def deletePidFile():
    os.remove(DESTINATION_DIRECTORY+"RUNNING_PID")

# Unzips dist package and starts application
def unzipAndStartNew():
    cleanDestinationDirectory()
    dist_zip_name = findApplicationZip() 
    unzipApp(dist_zip_name)           
    print ('Starting play application')
    cmd = ['nohup', DESTINATION_DIRECTORY + 'bin/' + APP_NAME, '-Dhttp.port='+str(80)] #, '-mem', str(256), '-J-server']
    subprocess.Popen(cmd)

def cleanDestinationDirectory():
    print ('Cleaning dist directory')
    try:
        shutil.rmtree(DESTINATION_DIRECTORY)
    except:
        print 'Error when cleaning!'

# Finds the name of app dist zip package in /target/universal/
def findApplicationZip():
    os.chdir(APP_DIRECTORY + 'target/universal')
    newest = max(glob.iglob('*.zip'), key=os.path.getctime)
    newest = newest.replace('.zip','')
    print ('Found newest dist zip: ' + newest)
    return newest;

# Unzips the package and moves content to destination dir
def unzipApp(dist_zip_name):
    p = subprocess.Popen(['unzip', APP_DIRECTORY + 'target/universal/'+dist_zip_name+'.zip', '-d', DESTINATION_DIRECTORY])
    p.wait()
    move_over(DESTINATION_DIRECTORY+dist_zip_name, DESTINATION_DIRECTORY)

# Helper to move files
def move_over(src_dir, dest_dir):
    fileList = os.listdir(src_dir)
    for i in fileList:
        src = os.path.join(src_dir, i)
        dest = os.path.join(dest_dir, i)
        if os.path.exists(dest):
            if os.path.isdir(dest):
                move_over(src, dest)
                continue
            else:
                os.remove(dest)
        shutil.move(src, dest_dir)

main()


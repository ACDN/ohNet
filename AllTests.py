import os
import sys
import subprocess
import time
import shutil
import signal
import platform

def objPath():
    plat = 'Posix'
    if os.name == 'nt':
        plat = 'Windows'
    elif platform.system() == 'Darwin':
        if gMac64 == 1:
            plat = 'Mac-x64'
        elif gMacArm == 1:
            plat = 'Mac/arm'
        else:
            plat = 'Mac-x86'
    variant = 'Release'
    if gDebugBuild == 1:
        variant = 'Debug'
    path = os.path.join('Build', 'Obj', plat, variant)
    return path

def build(aTarget, aParallel=False):
    buildCmd = 'make '
    if aParallel:
        buildCmd += '-j4 '
    if os.name == 'nt':
        buildCmd = 'nmake -s -f OhNet.mak '
    buildCmd += aTarget
    if os.environ.has_key('CS_PLATFORM'):
        buildCmd += ' csplatform=' + os.environ['CS_PLATFORM']
    if gDebugBuild == 1:
        buildCmd += ' debug=1'
    if gMac64 == 1:
        buildCmd += ' mac-64=1'
    if gMacArm == 1:
        buildCmd += ' mac-arm=1'
    if gCore == 1:
        buildCmd += ' platform=' + gPlatform

    ret = os.system(buildCmd)
    if (0 != ret):
        print '\nBuild for ' + aTarget + ' failed, aborting'
        sys.exit(1)

def runBuilds():
    if gIncremental == 0:
        cleanCmd = ''
        if os.name == 'nt':
            cleanCmd = 'nmake /s /f OhNet.mak clean'
        else:
            cleanCmd = 'make clean'
        os.system(cleanCmd)
    if gParallel:
        build('copy_build_includes')
    if gCore == 1:
        build('ohNet TestFramework Shell', gParallel)
    else:
        build('all', gParallel)
    if (gRunJavaTests == 1):
        build('ohNetJavaAll', False)
    print '\nBuilds complete'

def runTests():
    testsToRun = list(gAllTests)
    if gFullTests != 1:
        # Suppress non-quick tests
        testsToRun = [test for test in testsToRun if test.quick]
    if gNativeTestsOnly == 1:
        # Suppress non-native tests
        testsToRun = [test for test in testsToRun if test.native]
    for test in testsToRun:
        print '\nTest: ' + test.name
        cmdLine = test.args
        cmdLine.insert(0, test.Path())
        if (not test.native and os.name != 'nt'):
            cmdLine.insert(0, 'mono')
        ret = subprocess.call(cmdLine)
        if ret != 0:
            print '\nTest ' + test.name + ' failed, aborting'
            sys.exit(1)
    if (gRunJavaTests == 1):
        testsToRun = list(gJavaTests)
        if gFullTests != 1:
            # Suppress non-quick tests
            testsToRun = [test for test in testsToRun if test.quick]
        for test in testsToRun:
            print '\nTest: ' + test.name
            cmdLine = []
            if os.name == 'nt':
                cmdLine.append(os.path.join(os.environ['JAVA_HOME'], 'bin', 'java'))
            else:
                cmdLine.append('java')
            cmdLine.append('-Djava.library.path=' + objPath())
            cmdLine.append('-classpath')
            cmdLine.append(objPath())
            cmdLine.append('-enableassertions')
            cmdLine.append(test.name)
            ret = subprocess.call(cmdLine)
            if ret != 0:
                print '\nTest ' + test.name + ' failed, aborting'
                sys.exit(1)

def runTestsValgrind():
    # clear any old output files
    outputDir = 'vgout'
    if os.path.exists(outputDir):
        shutil.rmtree(outputDir)
    os.mkdir(outputDir)
    failed = []
    testsToRun = [test for test in gAllTests if test.quick and test.native]
    if gFullTests == 1:
        testsToRun = [test for test in gAllTests if test.native]
    os.system('export GLIBCXX_FORCE_NEW')
    for test in testsToRun:
        print '\nTest: ' + test.name
        cmdLine = []
        cmdLine.append('valgrind')
        cmdLine.append('--leak-check=yes')
        cmdLine.append('--suppressions=ValgrindSuppressions.txt')
        cmdLine.append('--xml=yes')
        cmdLine.append('--xml-file=' + os.path.join(outputDir, test.name) + '.xml')
        cmdLine.append(test.Path())
        for arg in test.args:
            cmdLine.append(arg)
        ret = subprocess.call(cmdLine)
        if ret != 0:
            failed.append(test.name)
    if len(failed) > 0:
        print '\nERROR, the following tests failed:'
        for fail in failed:
            print '\t' + fail
        sys.exit(-1)

def runTestsHelgrind():
    # clear any old output files
    outputDir = 'hgout'
    if os.path.exists(outputDir):
        shutil.rmtree(outputDir)
    os.mkdir(outputDir)
    failed = []
    testsToRun = [test for test in gAllTests if test.quick and test.native]
    if gFullTests == 1:
        testsToRun = [test for test in gAllTests if test.native]
    os.system('export GLIBCXX_FORCE_NEW')
    for test in testsToRun:
        print '\nTest: ' + test.name
        cmdLine = []
        cmdLine.append('valgrind')
        cmdLine.append('--tool=helgrind')
        cmdLine.append('--xml=yes')
        cmdLine.append('--xml-file=' + os.path.join(outputDir, test.name) + '.xml')
        cmdLine.append(test.Path())
        for arg in test.args:
            cmdLine.append(arg)
        ret = subprocess.call(cmdLine)
        if ret != 0:
            failed.append(test.name)
    if len(failed) > 0:
        print '\nERROR, the following tests failed:'
        for fail in failed:
            print '\t' + fail
        sys.exit(-1)

gStartTime = time.strftime('%H:%M:%S')
gBuildsCompleteTime = ''
gBuildOnly = 0
gFullTests = 0
gIncremental = 0
gNativeTestsOnly = 0
gSilent = 0
gTestsOnly = 0
gValgrind = 0
gHelgrind = 0
gRunJavaTests = 0
gJsTests = 0
gDebugBuild = 0
gMac64 = 0
gMacArm = 0
try:
    gPlatform = os.environ['PLATFORM']
except KeyError:
    gPlatform = None
gCore = 0
gParallel = False
for arg in sys.argv[1:]:
    if arg == '-b' or arg == '--buildonly':
        gBuildOnly = 1
    elif arg == '--debug':
        gDebugBuild = 1
    elif arg == '-f' or arg == '--full':
        gFullTests = 1
    elif arg == '-i' or arg == '--incremental':
        gIncremental = 1
    elif arg == '--java':
        gRunJavaTests = 1
    elif arg == '--js':
        gJsTests = 1
    elif arg == '-n' or arg == '--native':
        gNativeTestsOnly = 1
    elif arg == '-s' or arg == '--silent':
        gSilent = 1
    elif arg == '-t' or arg == '--testsonly':
        gTestsOnly = 1
    elif arg == '-vg' or arg == '--valgrind':
        gValgrind = 1
        if os.name == 'nt':
            print 'ERROR - valgrind is only supported on linux'
            sys.exit(1)
    elif arg == '-hg' or arg == '--helgrind':
        gHelgrind = 1
        if os.name == 'nt':
            print 'ERROR - helgrind is only supported on linux'
            sys.exit(1)
    elif arg == '--mac-64':
        gMac64 = 1
        if platform.system() != 'Darwin':
            print 'ERROR - --mac-64 only applicable on Darwin'
            sys.exit(1)
    elif arg == '--mac-arm':
        gMacArm = 1
        if platform.system() != 'Darwin':
            print 'ERROR - --mac-arm only applicable on Darwin'
            sys.exit(1)
    elif arg == '--parallel':
        gParallel = True
    elif arg == '--core':
        gCore = 1
    else:
        print 'Unrecognised argument - ' + arg
        sys.exit(1)
    os.environ["ABORT_ON_FAILURE"] = "1"
    if gSilent != 0:
        os.environ["NO_ERROR_DIALOGS"] = "1"

class TestCase(object):
    def __init__(self, name, args, quick=False, native=True):
        self.name = name
        self.args = args
        self.quick = quick
        self.native = native
    def Path(self):
        path = objPath() + '/' + self.name
        if os.name == 'nt':
            path += '.exe'
        elif not self.native:
            os.environ['LD_LIBRARY_PATH'] = objPath()
            path += '.exe'
        else:
            path += '.elf'
        return path

gAllTests = [ TestCase('TestBuffer', [], True)
             ,TestCase('TestThread', [], True)
             ,TestCase('TestFifo', [], True)
             ,TestCase('TestFile', [], True)
             ,TestCase('TestQueue', [], True)
             ,TestCase('TestTextUtils', [], True)
             ,TestCase('TestNetwork', [], True)
             #,TestCase('TestTimer', [])
             ,TestCase('TestSsdpMListen', ['-d', '10'], True)
             ,TestCase('TestSsdpUListen', ['-t', 'av.openhome.org:service:Radio:1'], True)
             ,TestCase('TestDeviceList', ['-t', 'av.openhome.org:service:Radio:1', '-f'], True)
             ,TestCase('TestDeviceListStd', ['-t', 'av.openhome.org:service:Radio:1', '-f'], True)
             ,TestCase('TestDeviceListC', ['-t', 'av.openhome.org:service:Radio:1', '-f'], True)
             ,TestCase('TestInvocation', [])
             ,TestCase('TestInvocationStd', [])
             ,TestCase('TestSubscription', [])
             ,TestCase('TestProxyC', [])
             ,TestCase('TestDviDiscovery', ['-l'], True)
             ,TestCase('TestDviDeviceList', ['-l'], True)
             ,TestCase('TestDvInvocation', ['-l'], True)
             ,TestCase('TestDvSubscription', ['-l'], True)
             ,TestCase('TestDvDeviceStd', ['-l'], True)
             ,TestCase('TestDvDeviceC', [], True)
             ,TestCase('TestCpDeviceDv', [], True)
             ,TestCase('TestCpDeviceDvStd', [], True)
             ,TestCase('TestCpDeviceDvC', [], True)
             ,TestCase('TestProxyCs', [], False, False)
             ,TestCase('TestDvDeviceCs', [], True, False)
             ,TestCase('TestCpDeviceDvCs', [], True, False)
            ]
gJavaTests = [ TestCase('org.openhome.net.controlpoint.tests.TestProxy', [], False, False)
              ,TestCase('org.openhome.net.controlpoint.tests.TestCpDeviceDv', [], True, False)
              ,TestCase('org.openhome.net.device.tests.TestDvDevice', [], True, False)
               ]

class js_test():

    def write_dummy_results(self):
        if not os.path.exists("xout"):
            os.mkdir("xout")
        # write dummy XML that gets re-written by real XML if browser connects to node properly
        dummy_xml_read = open("OpenHome/Net/Bindings/Js/ControlPoint/Tests/dummyxml.xml", 'r')
        dummy_xml_write = open("xout/ProxyJsTest.xml", 'w')
        dummy_xml_write.writelines(dummy_xml_read)
        dummy_xml_write.close()

    def get_env(self,objpath):
        self.objpath = objpath
        program_files = os.environ.get('ProgramFiles')
        self.browser_location = os.path.join(program_files, 'Safari\Safari.exe')
        self.test_dir = os.path.join(os.getcwd(), 'Build\Include\OpenHome\Net\Private\Js\Tests')

    def find_device(self):
        self.test_testbasic = subprocess.Popen([os.path.join(self.objpath, 'TestDvTestBasic.exe'), '-l', '-c', self.test_dir])
        time.sleep(5)
        test_devfinder = subprocess.Popen([os.path.join(self.objpath, 'TestDeviceFinder.exe'), '-l', '-s', 'openhome.org:service:TestBasic:1'],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.launch_url = test_devfinder.communicate()[1].rstrip()
        print 'found device at ' + self.launch_url
        
    def run_browser(self):
        subprocess.call(["%s" %(self.browser_location), "%s" %(self.launch_url)])
        self.test_testbasic.terminate()

    def run_browser_jenkins(self):
        subprocess.call(["psexec", "-i", "2", "-u", "hudson-zapp", "-p", "temp123", "%s" %(self.browser_location), "%s" %(self.launch_url)])    
        self.test_testbasic.terminate()

def JsTests():
    objpath = objPath()
    do_jstest = js_test()
    do_jstest.write_dummy_results()
    do_jstest.get_env(objpath)
    do_jstest.find_device()
    # PsExec allows us to view JS tests under Jenkins
    # ...it also seems to cause most of the problems around JS tests so try ignoring it for now
    do_jstest.run_browser()
    #if os.getenv('JENKINS_COOKIE') is None:
    #    do_jstest.run_browser()
    #else:
    #    do_jstest.run_browser_jenkins()


if gTestsOnly == 0:
    runBuilds()
gBuildsCompleteTime = time.strftime('%H:%M:%S')
if gBuildOnly == 0:
    if gValgrind == 1:
        runTestsValgrind()
    if gHelgrind == 1:
        runTestsHelgrind()
    if gValgrind == 0 and gHelgrind == 0:
        runTests()
    if gJsTests == 1:
        JsTests()
    print '\nFinished.  All tests passed'
print 'Start time: ' + gStartTime
print 'Builds complete: ' + gBuildsCompleteTime
print 'End time: ' + time.strftime('%H:%M:%S')

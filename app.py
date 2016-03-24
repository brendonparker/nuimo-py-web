from webkit import WebView
import pygtk
pygtk.require('2.0')
import gtk, threading, time
from nuimo import NuimoScanner, Nuimo, NuimoDelegate

class App:
    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        sw = gtk.ScrolledWindow()
        self.view = WebView()
        sw.add(self.view)
        window.add(sw)
        self.loadUrls()
        window.fullscreen()
        window.show_all()
        self.view.open(self.urls[self.current])

    def loadUrls(self):
        self.current = 0
        try:
            with open('urls.csv') as f:
                self.urls = f.readlines()
                #remove empties
                self.urls = filter(None, self.urls)
        except:
            print 'failed to read urls.csv'
            self.urls = ['http://google.com']

    def next(self):
        self.current = (self.current + 1) % len(self.urls)
        self.view.open(self.urls[self.current])

    def previous(self):
        self.current = self.current - 1
        if self.current < 0:
            self.current = len(self.urls) - 1
        self.view.open(self.urls[self.current])

class CustomNuimoDelegate(NuimoDelegate):
    def __init__(self, nuimo, app):
        NuimoDelegate.__init__(self, nuimo)
        self.app = app
        
    def handleSwipe(self, data):
        NuimoDelegate.handleSwipe(self, data)
        if data == 1:
            gtk.idle_add(app.next)
        else:
            gtk.idle_add(app.previous)
            
    def handleButton(self, data):
        NuimoDelegate.handleButton(self, data)
        if data == 1:
            gtk.idle_add(app.next)

def showImagesOnNuimo(nuimo):
    nuimo.displayLedMatrix(
        "         " +
        " ***     " +
        " *  * *  " +
        " *  *    " +
        " ***  *  " +
        " *    *  " +
        " *    *  " +
        " *    *  " +
        "         ", 2.0)
    time.sleep(2)
    nuimo.displayLedMatrix(
        " **   ** " +
        " * * * * " +
        "  *****  " +
        "  *   *  " +
        " * * * * " +
        " *  *  * " +
        " * * * * " +
        "  *   *  " +
        "   ***   ", 20.0)

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    app = App()
            
    def nuimo_process():
        def foundDevice(addr):
            print 'found device: ' + addr
            nuimo = Nuimo(addr)
            nuimo.set_delegate(CustomNuimoDelegate(nuimo, app))
            nuimo.connect()
            showImagesOnNuimo(nuimo)
            while True:
                nuimo.waitForNotifications()

        while True:
            try:
                NuimoScanner().start(foundDevice)
            except Exception, e:
                print 'failed to connect to nuimo: %s' % e
                time.sleep(5)

    thread = threading.Thread(target=nuimo_process)
    thread.daemon = True
    thread.start()
    main()
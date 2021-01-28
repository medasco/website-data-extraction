
import time
import fileinput
from PyQt4 import QtCore
from wsm.downloader.dasco_pySmartDL import *
from wsm.config import *


class DownloadItem(SmartDL, QtCore.QObject):
    # Signals
    dl_progress = QtCore.pyqtSignal(tuple)

    def __init__(self, url=None, destination=None, index=0):
        SmartDL.__init__(self, url, destination, progress_bar=False, progress_signal=True, fix_urls=True, threads=5, logger=None, connect_default_logger=False)
        QtCore.QObject.__init__(self, parent=None)

        self.index = index

    def progress_ready(self, progress):

        self.dl_progress.emit((progress, self.index))


class DownloadManager(QtCore.QObject):
    # Signals
    progress_ready = QtCore.pyqtSignal(tuple)
    progress_list = []

    def __init__(self, download_list):
        super(DownloadManager, self).__init__()

        self.dl_list = download_list
        self.dl_item_list = []
        self.path_to_logfile = DOWNLOAD_PATH

    def activate(self):

        for item in self.dl_list:
            dl_item = DownloadItem(item[0], item[1], item[2])
            self.dl_item_list.append(dl_item)
            self.progress_list.append(0)

        for dl_item in self.dl_item_list:
            dl_item.start(blocking=False)
            dl_item.control_thread.progress_ready.connect(dl_item.progress_ready)
            dl_item.dl_progress.connect(self.send_progress)

    def send_progress(self, progress):
        self.progress_ready.emit(progress)
        self.log_progress(progress)

    # IbarretaI: TODO
    def is_finished(self):
        if not any(x == 0 for x in self.progress_list):
            return True

    def log_progress(self, progress):
        prog, idx = progress
        if prog >= 100:
            self.progress_list[idx] = prog

        if self.is_finished():
            print("Finished")
            self.create_log_file()

    def create_log_file(self):

        print(self.path_to_logfile)
        self.path_to_logfile = os.path.join(self.path_to_logfile, "Report")
        try:
            os.mkdir(self.path_to_logfile)
        except:
            pass
        self.path_to_logfile = os.path.join(self.path_to_logfile, "Download_Report.csv")

        with open(self.path_to_logfile, "w") as output:
            print("Filename, Status, Downloaded", file=output)
            for item, prog in zip(self.dl_list, self.progress_list):
                if prog == 100:
                    print(os.path.basename(item[1])+","+"Done,"+str(os.path.isfile(item[1])), file=output)
                else:
                    print(os.path.basename(item[1])+","+"Failed,"+str(os.path.isfile(item[1])), file=output)
            self.progress_list = []
        output.close()


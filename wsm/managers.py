
import os
import pandas as pd
import shutil
import zipfile

from wsm.config import *


class ChartManagerUSA:

    """ BluePrint of Chart Manager """

    # Constructor function
    def __init__(self):
        super(ChartManagerUSA, self).__init__()

        self.src = DOWNLOAD_PATH + 'USA' + '\\'
        self.dst = self.src + 'USA_Managed' + '\\'
        self.con = self.dst + 'Construction_DL'
        self.usEXCEL = REF_PATH + 'USA_List.xlsx'

    # Scan source folder
    def scan_folder(self, path):

        print('Checking Source Folder.')

        result = []
        for root, dirs, files in os.walk(path):
            for name in files:
                if name.endswith(('.pdf', '.PDF', 'AD.PDF', '_CMP.PDF')):
                    result.append(os.path.join(root, name))

        return result

    # Splitting pathname
    def extract_folder(self, result):

        # Splitting from 2nd to the last name
        return (result.split('\\')[-1]).split('.')[-2]

    # Read USA excel sheet
    def excel(self):

        print('Filtering Source Excel File.')

        df = pd.read_excel(self.usEXCEL, sheetname=0)
        df.columns = ['ICAO', 'Charts']

        return list(df['Charts'])

    # Comparing downloaded files of USA Folder to US charts(excel file)
    def compare(self):

        print('Comparing SRC Files to Excel File.')

        # assigning variables
        usa_folder = self.scan_folder(self.src)
        excel_list = self.excel()

        # constructing a list
        compared_list = []

        # iterate excel_chart inside readExcel, 332 files
        for excel_chart in excel_list:

            # iterate usa_chart inside scanFolder(USA), 17442 files
            for usa_chart in usa_folder:

                # constructing new variable for usa_chart through a function of extract_folder()
                extract_chart = self.extract_folder(usa_chart)

                # matching extruded files to excel files
                if extract_chart.split('_')[0] == excel_chart:

                    # every matched files from usa_chart will join into a constructed list(compared_list)
                    compared_list.append(usa_chart)

        for path in compared_list:
            shutil.copy(path, self.dst)

    # Compare/Move/Rename
    def move_rename(self):

        print('Yielding Matched Files...')

        # read the excel file and store in a DataFrame
        df = pd.read_excel(self.usEXCEL, sheetname=0)
        df.columns = ['ICAO', 'Charts']

        # transpose excel DataFrame to a list, data_frame[column][row], data_frame[0,1,2,3....][0,1,2,3...]
        data_frame = df.values.T.tolist()

        # change directory into a destination folder
        os.chdir(self.dst)

        # iterate through col1(columnB)(data_frame[1]) of excel list
        # range was used as the number of items inside certain length of a list
        for ad in range(len(data_frame[1])):

            # iterate pdf files in destination folder
            for file in os.listdir(self.dst):

                # split filename and extension name
                filename, pdf = os.path.splitext(file)

                # comparing filename versus col1(columnB) values
                if filename == data_frame[1][ad]:

                    # implicitly renaming .PDF
                    pdf = '.pdf'

                    # constructing new name from col0(columnA) value
                    port_name = data_frame[0][ad]
                    new_name = port_name + pdf

                    # creating directories according to .pdf items
                    os.makedirs(port_name)

                    # actual renaming
                    os.rename(file, new_name)

                    shutil.move(os.path.abspath(new_name), os.path.abspath(port_name))

    # Moving all construction charts
    def move_construction(self):

        print('Initializing Destination Folder.')

        # get Construction directory
        construction = os.path.abspath(self.con)

        # change directory into a destination folder
        os.chdir(construction)

        # assigning variables
        port_folders = os.listdir(self.dst)

        # iterate from a source path
        for cons_file in os.listdir(construction):

            for port in port_folders:

                if port == cons_file.split('_')[0]:

                    shutil.copy(os.path.abspath(cons_file), str(self.dst + port))

    # Matching all charts inside Compare folder to Excel file
    def ad_compare(self):

        print('Filtering Compared Files to Excel File.')

        # read the excel file and store in a DataFrame
        df = pd.read_excel(self.usEXCEL, sheetname=0)
        df.columns = ['ICAO', 'Charts']

        # transpose excel DataFrame to a list, data_frame[column][row]
        data_frame = df.values.T.tolist()

        new_path = self.dst + 'Compare'

        print('Creating ICAO Directories.')

        if not os.path.exists(new_path):
            os.makedirs(new_path)

        os.chdir(self.dst)

        print('Copying Matched Files...')

        for ad in range(len(data_frame[1])):

            # iterate pdf files in destination folder
            for file in os.listdir(self.dst):

                # split filename and extension trash
                filename, pdf = os.path.splitext(file)

                # comparing filename versus col1(columnB) values
                ad_cmp = filename.split('_')[0]

                # comparing filename versus col1(columnB) values
                if ad_cmp == data_frame[1][ad]:

                    # implicitly renaming PDF files
                    pdf = '.pdf'
                    com = '_cmp'

                    # constructing new trash from col0(columnA) value
                    port_name = data_frame[0][ad]
                    new_name = port_name + com + pdf

                    # actual renaming
                    os.rename(file, new_name)

                    # moving every new_name to a new folder 'Compare"
                    shutil.move(new_name, new_path)

        print('Finished Moving.')

    # Cleaning Construction folder
    def clean_construction(self):

        print('Initializing Destination Folder.')

        # get Construction directory
        cons = os.path.abspath(self.con)

        # change directory into a destination folder
        os.chdir(cons)

        cons_path = self.dst + 'Construction'

        if not os.path.exists(cons_path):
            os.makedirs(cons_path)

        # read the excel file and store in a DataFrame
        df = pd.read_excel(self.usEXCEL, sheetname=0)
        df.columns = ['ICAO', 'Charts']

        # transpose excel DataFrame to a list, b[column][row]
        excel = list(df['ICAO'])

        # assigning variables
        cons_pdf = os.listdir(cons)

        for pdf in cons_pdf:
            for port_excel in excel:

                file = pdf.split('_')[0]
                port = port_excel

                if file == port:
                    shutil.move(pdf, cons_path)

        print('Moved.')

        for remain in os.listdir('.'):
            os.remove(remain)

        # change directory into a destination folder
        os.chdir(self.dst)

        os.removedirs(self.con)

        print('Done Cleaning.')

    # Extraction of zip files
    def unzip(self):

        os.chdir(self.src)
        ext = '.zip'

        # loop through items in dir
        for item in os.listdir(self.src):

            # check for ".zip" extension
            if item.endswith(ext):

                # get full path of files
                file_name = os.path.abspath(item)
                zip_folder = self.src

                if not os.path.exists(zip_folder):
                    os.makedirs(zip_folder)

                # create zipfile object
                zip_ref = zipfile.ZipFile(file_name)

                # extract file to dir
                zip_ref.extractall(zip_folder)

                # close file
                zip_ref.close()

                # delete zipped file
                os.remove(file_name)

                print('Done Zipping files...')

    # Main
    def manage(self):
        print('Managing USA...')

        # Extraction of downloaded .zip folders
        self.unzip()

        # compare and copy match files (function 'scan_folder' and 'excel' was called)
        self.compare()

        # move and rename
        self.move_rename()

        # moving Construction files
        self.move_construction()

        # AD files compared and moved to Compare Folder
        self.ad_compare()

        # Cleaning Construction Folder
        self.clean_construction()

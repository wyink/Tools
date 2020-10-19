from ftplib import FTP
from urllib.parse import urlparse
import time
import os
from typing import List,

class NcbiFtp:
    '''NCBIのFTPから指定ファイルをダウンロード，解凍を行うクラス

    Member
    -------
    NCBI_FTP_PATH : str
        ncbiのftpのパス
    
    '''

    NCBI_FTP_PATH = "ftp://ftp.ncbi.nlm.nih.gov"

    def __init__(self, your_ftp_path:str) -> None:
        '''
        your_ftp_path : str
            NCBI(National Center for Biotechnology Information)の
            FTPパス[ftp://ftp.ncbi.nlm.nih.gov]を含むURL
            
            ex.
            ftp://ftp.ncbi.nlm.nih.gov/
                genomes/all/GCF/000/013/285/GCF_000013285.1_ASM1328v1

        '''
        #self.your_ftp_path =  your_ftp_path #type:str
        self.ftp = FTP(urlparse(NcbiFtp.NCBI_FTP_PATH).netloc).login
        self.ftp.login()

    def __del__(self):
        self.ftp.quit()
    
    def download(self,func=lambda upath:upath.rsplit('/',1)[1]):
        '''メンバ変数のファイルをダウンロード
        func : function
            個々のファイル名前を指定もしくは切り出して指定
            default-func(upath)->str:
                引数のupathはurlのパス
                識別子としての役割を果たすと期待される
                長いurlをスラッシュで区切った際の最も左の文字列
                返却後の文字列はダウンロード後のファイル名に指定
                
        '''

        for file in self.files:
            print(file)

            #LogIn
            ftp = FTP(urlparse(NcbiFtp.NCBI_FTP_PATH).netloc)
            ftp.login()

            webcudir = urlparse(file).path
            ftp.cwd(webcudir)  
            files = ftp.nlst('.') #current dir

            #一時ディレクトリ作成
            #tmp_dir = webcudir.rsplit('/',1)[1]
            dir = f'resources/strain_data/{tmp_dir}'
            #
            os.mkdir(dir)

            #store
            tx,gz = [],[] 

            for file in files:
                if file[-3:] =='txt':
                    tx.append(file)
                elif file[-3:] == '.gz':
                    gz.append(file)
                else:
                    print(file)

            #output
            file=''
            for file in tx:
                with open(f'{dir}/{file}','w') as f:
                    def print_space(line):
                        f.write(line+'\n')
                    ftp.retrlines(f'RETR {file}',callback=print_space)

            for file in gz:
                with open(f'{dir}/{file}','bw') as f:
                    ftp.retrbinary(f'RETR {file}',f.write)

            ftp.quit()
            time.sleep(5)




def dl_from_ncbi(dl_text_list:List[str]):
    '''
    ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/013/285/GCF_000013285.1_ASM1328v1
    gbftp=[] #the location of Genbank FTP
    with open('resources/prokaryotes.txt') as f:
        f.readline() #skip header!
        for l in f:
            gbftp.append(l.split('\t')[14])
    '''


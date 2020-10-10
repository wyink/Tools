import requests
from bs4 import BeautifulSoup
from typing import Dict,List
import re


class BioProject:
    '''Bioprojectのデータを扱うクラス

    Static Members
    --------------
    PLOJECT_URL : str
        利用するプロジェクトのurlの定数部分

    Members
    --------
    _soup : BeautifulSoup
        引数で与えられたProjectIdのwebページ内容を部分オブジェクトにもつ
        BeautifulSoupクラスのインスタンス
        
    '''

    PLOJECT_URL = "https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?study="

    def __init__(self,srp,samn=False): 
        '''コンストラクタ
        Parameters
        -----------
        srp : str
            BioProjectID
        samn : bool
            True  : https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?study={srp}
                    ページにRelated Files Tableが存在するかどうか
                    存在する場合はそのテーブルのリンクから解析ファイルおよびSampleに関する
                    情報を取得することになる。
            False : https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?study=//
                    ページにはAbstractまでしか情報が記載されていない場合。
                    この場合各サンプルの情報はExperiment->Send Toのリンクからまとめて取得可能
                    この処理は手動で十分事足りるため、ここでは扱わない。

        '''

        self._soup = BeautifulSoup(
                requests.get(self.PLOJECT_URL + srp ).content,
                "html.parser"
            ) #type:BeautifulSoup

        if samn:
            self._soup_samns = self._soup.find_all("tr","altrow") 

    def abstract(self)->str:
        '''project_urlのページから研究概要を取得

        Returns
        -------
        str : 研究概要を示す文字列

        '''
        abstract = "" #type:str
        
        s =self._soup.find_all(class_="row")
        abstract = s[2].text.strip()
        return abstract

    def bioproject_id(self)->str:
        '''project_urlのページからBioProjectIDを取得

        Returns
        -------
        str : BioProjectIDを示す文字列

        '''
        projectid = "" #type:str

        s = self._soup.find_all(class_="row")
        projectid = s[0].find("a").text
        return projectid

    @staticmethod
    def _sra_name_get(soup:BeautifulSoup)->str:
        '''SRAから始まるIDを取得

        Parameters
        ----------
        soup : BeautifuSoup
            https://www.ncbi.nlm.nih.gov//biosample/SAMN12644116へ
            Getでアクセスした際に得たcontentを部分オブジェクトとして保持

        Returns 
        --------
        sraname : str
            SRAから始まるID
        
        '''

        sra=[]
        srahref = ""
        sra = soup.find_all("a","dblinks") 
        srahref = sra[1].get("href")

        #SRAリンクへgetでアクセス (https://www.ncbi.nlm.nih.gov/sra?LinkName=biosample_sra&from_uid=xxxxxxx)
        p = requests.get(f"https://www.ncbi.nlm.nih.gov/{srahref}") 
        sra = BeautifulSoup(p.content,"html.parser") 
        sraname = sra.find("tbody").find("a").string

        return sraname

    def biosample_info(self, select:Dict[str, str]):
        '''BioSampleに関する情報を取得
        URL : https://www.ncbi.nlm.nih.gov//biosample/SAMNxxxxxxx
        のページのAttribute情報を取得する。
        引数

        Parameters
        ----------
        select : Dict[str,str]
            key : Attribute
            val : Attributeに対応する値
            この辞書にはフィルターとして利用したいAttributeセット
            が登録されている。
        
        Returns
        -------
        List[List[str]]
            [["http://www~SAMN",SRR[\\d+],"host Equus|host_neutered Yes|..."],[],[]...]

        '''

        c_tr=[]
        retlist = [] #type:List[List[str]]

        samn = ""     #type:str
        all_attr = "" #type:str
        column = ""   #type:str
        value = ""    #type:str
        flag = 0      #type:int

        for tag in self._soup_samns: 
            samn = tag.find("a").get("href") 
            html = requests.get(f"{samn}")                   #type:requests.models.Response
            soup = BeautifulSoup(html.content,"html.parser") #type:BeautifulSoup
            c_tr = soup.find("table","docsum").find_all("tr")

            for i in c_tr:
                column = i.th.string #attribute_key
                value  = i.td.string.strip() #attribute_value
                all_attr = all_attr+column+"\t"+value+"|"  #ex host Equus|host_neutered Yes|...
                
                #引数の辞書の条件を満たすとカウントを増やす
                if column in select and re.search(select[column],value,re.IGNORECASE):
                    flag += 1

            #引数の辞書の条件を全て満たす場合
            if flag == len(select):
                sraname = self._sra_name_get(soup)
                retlist.append([samn,sraname,all_attr])
                
        return retlist 

class BioPjtList:
    '''下記のURLで表示される各BioProjectの情報を取得するクラス
    URL：
    https://trace.ncbi.nlm.nih.gov/Traces/sra/
    sra.cgi?view=studies&f=study&go=Go&term={SEARCH_WORD}

    Static Members
    ------------------
    BIO_PJT_URL : str
        上記URLの定数部分
    
    Member
    ------
    _bio_bjp_url : str
        作成された上記URLの文字列
    
    '''

    BIO_BJT_URL = \
        "https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?view=studies&f=study&go=Go&term="

    def __init__(self,search_word):
        self._bio_pjt_url = self.BIO_BJT_URL + '+'.join(search_word)

    def list_of_study(self)->List[List[str]]:
        '''Projectについての情報を取得する
        以下の形式で出力
        --------------------------------------
        SRPxxxxxx
        PRJNAxxxxxxx
        Short Introduction about this project!
        Abstract: about this project!
        --------------------------------------

        Returns
        -------
        List[List[str]] 
            それぞれのProjectの情報は上記の形式の文字列として管理
            され、この返却値のリストの一つの要素として構成される。

            補足：
            このリストにはself._bio_pjt_urlで検索された全てのProject
            の情報を管理する。
         
        '''

        ht = requests.get(self._bio_pjt_url)
        soup = BeautifulSoup(ht.content,"html.parser").find_all("tr")
        soup.pop(0) #skip header

        srp = ""   #type:str
        bpjid = "" #type:str
        title = "" #type:str
        abst = ""  #type:str
        list = []  #List[List[str]]
        
        for i in soup:
            title  = (i.find_all("td")[2]).text.strip()
            href = i.find("a").get("href") #href = "?study=SRP~"
            srp = href.split('=')[1]    
            bpj = BioProject(srp)       #type:BioProject       
            abst = bpj.abstract()            
            bpjid = bpj.bioproject_id() 
            list.append([srp,bpjid,title,abst])

        return list


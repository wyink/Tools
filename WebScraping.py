import requests
from bs4 import BeautifulSoup
from typing import Dict
import re


class BioProject:
    '''Bioprojectのデータを扱うクラス

    Static Members
    --------------
    PLOJECT_URL : str
        利用するプロジェクトのurlの定数部分

    Members
    --------
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
    PLOJECT_URL = "https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?study="

    def __init__(self,srp,samn=False): 
        self._srp = requests.get(self.PLOJECT_URL + srp )
        self._soup = BeautifulSoup(self._srp.content,"html.parser")

        if samn:self._soup_samns = self._soup.find_all("tr","altrow")

    def abstract(self):
        '''project_urlのページから研究概要を取得

        Returns
        -------
        str : 研究概要を示す文字列

        '''
        abstract,s = "",""
        s =self._soup.find_all(class_="row")
        abstract = s[2].text.strip()
        return abstract

    def bioproject_id(self):
        '''project_urlのページからBioProjectIDを取得

        Returns
        -------
        str : BioProjectIDを示す文字列

        '''
        projectid,s = "",""
        s = self._soup.find_all(class_="row")
        projectid = s[0].find("a").text
        return projectid

    @staticmethod
    def _sra_name_get(soup):
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
        retlist = [] 
        tag,samn,html,soup= "","","","" 
        column,value,str,i = "","","","" 
        flag:int = 0 

        for tag in self._soup_samns:
            samn = tag.find("a").get("href") #http://www~SAMN
            html = requests.get(f"{samn}")
            soup = BeautifulSoup(html.content,"html.parser") 
            c_tr = soup.find("table","docsum").find_all("tr")

            for i in c_tr:
                column = i.th.string #attribute_key
                value  = i.td.string.strip() #attribute_value
                str = str+column+"\t"+value+"|"  #ex host Equus|host_neutered Yes|...the lists goes on
                
                #引数の辞書の条件を満たすとカウントを増やす
                if column in select and re.search(select[column],value,re.IGNORECASE):
                    flag += 1

            #引数の辞書の条件を全て満たす場合
            if flag == len(select):
                sraname = self._sra_name_get(soup)
                retlist.append([samn,sraname,str])
                
        return retlist 

class BioPjtList:
    '''下記のURLで表示される各BioProjectの情報を取得するクラス
    URL：https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?view=studies&f=study&term={SEARCH_WORD}&go=Go

    '''
    
    def __init__(self,view_studies):
        self._view_studies = view_studies
    
    def list_of_study(self):
        ht = requests.get(self._view_studies)
        soup = BeautifulSoup(ht.content,"html.parser").find_all("tr")
        soup.pop(0) #skip header
        list = []
        for i in soup:
            title  = (i.find_all("td")[2]).text.strip()
            href = i.find("a").get("href") #href = "?study=SRP~"
            srp = href.split('=')[1]
            bpj = BioProject(srp) #instance;
            abst = bpj.abstract() #abstract of srp
            bpjid = bpj.bioproject_id() #bioproject-id of srp
            list.append([srp,bpjid,title,abst])
        return list


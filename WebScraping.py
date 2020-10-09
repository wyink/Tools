import urllib.request
import requests
from bs4 import BeautifulSoup
import re
import os
import sys


class BioProject:
    #constructor
    def __init__(self,srp,atrb_key="host",atrb_value="horse",samn="exists"): 
        self._atrb_key = atrb_key
        self._atrb_value = atrb_value
        self._srp = requests.get(f"https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?study={srp}")
        self._soup = BeautifulSoup(self._srp.content,"html.parser")

        #_soup_samns=[BioSamples of each BioProject/SAMN[\d+]...]
        if samn == "exists":
            self._soup_samns = self._soup.find_all("tr","altrow")

    def abstract(self):
        abstract,s = "",""
        s =self._soup.find_all(class_="row")
        abstract = s[2].text.strip()
        return abstract

    def bioproject_id(self):
        projectid,s = "",""
        s = self._soup.find_all(class_="row")
        projectid = s[0].find("a").text
        return projectid

    def sra_name_get(self,soup):
        #local variable
        sra=[]
        srahref = ""
        sra = soup.find_all("a","dblinks") #sra[1] -->sra_num_included site
        srahref = sra[1].get("href")
        p=requests.get(f"https://www.ncbi.nlm.nih.gov/{srahref}") #sraname=>a object but relative pass;
        sra = BeautifulSoup(p.content,"html.parser") #sra overwrite $sra(variable)
        sraname = sra.find("tbody").find("a").string
        return sraname

    def biosample_info(self): #certain BioProject,collect 'all' BioSample Data(url,sample_infomation)
        #local variable
        c_tr=[]
        retlist = []
        tag,samn,html,soup= "","","","" #str
        column,value,str,i = "","","","" #str
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
                if column == self._atrb_key and re.search(self._atrb_value,value,re.IGNORECASE):
                    flag=1
            if flag==1:
                sraname = self._sra_name_get(soup)
                retlist.append([samn,sraname,str])
                str,flag = "",0
        return retlist #[["http://www~SAMN",SRR[\d+],"host Equus|host_neutered Yes|..."],[],[]...]

class BioPjtList:
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


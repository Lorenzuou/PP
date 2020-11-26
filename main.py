import requests 
import json
from bs4 import BeautifulSoup
import psycopg2
import datetime as dt 
import pandas as pd


class Celular: 
    def __init__(self,nome,menorValor,maiorValor): 
        self.nome = nome
        self.menorValor = menorValor
        self.maiorValor = maiorValor


#estabele conexão com o Banco de dados PostGrees 
def conexaoBD():
    try:
        con =  psycopg2.connect(host='localhost', database='celulares',user='postgres', password='admin',port='5432')
      
    except (Exception, psycopg2.Error) as error :
        print("Falha ao conectar com o banco: ",error)
    return con 

#Retorna os produtos do site da Magazine luiza
def getProdutos(): 
    pagina = requests.get("https://www.magazineluiza.com.br/smartphone/celulares-e-smartphones/s/te/tcsp?sort=type%3AsoldQuantity%2Corientation%3Adesc").content
    sopa = BeautifulSoup(pagina, 'html.parser')

    conteudo = sopa.findChildren('body')

    conteudo = sopa.find('ul',attrs={'role':'main'})
    produtos = sopa.find_all(name='script',attrs={'type': 'application/ld+json'}); 
    return produtos 


#Insere os produtos em uma tabela no BD
def inserirBD(celular,con): 
    try:
        cursor = con.cursor()

        sql = """ INSERT INTO celular (nome,menorValor,maiorValor) VALUES (%s,%s,%s)"""
        valores = (celular.nome,celular.menorValor,celular.maiorValor)
        cursor.execute(sql, valores)

        con.commit()
    except (Exception, psycopg2.Error) as error :
        if(con):
            print("Falha ao inserir: ", error)

#Insere, no BD, a posição relativa de cada celular no ranking de mais vendidos 
def inserirPosicao(con,posicao):
    sql = "SELECT * FROM celular"
    cursor = con.cursor()
    cursor.execute(sql)
    tabela = pd.DataFrame(cursor.fetchall())
    colunaNova = {}

    for celular,row in tabela.iterrows(): 
        colunaNova[celular]=(tabela.index[celular] % 30)+1

    tabela["posicao"] = colunaNova

    for p in colunaNova: 
        sql ="UPDATE celular SET posicao = %s WHERE id = %s"
        cursor.execute(sql,(colunaNova[p],posicao[0][0]+1+p))
        con.commit()


        



#requisita os produtos
produtosBrutos = getProdutos()
lista_produtos = []

#Adiciona cada produto na lista, ignorando o primeiro elemento (que não é um produto)
for p in produtosBrutos[1:31]: 
    p = json.loads(p.string) 
    lista_produtos.append(p)
    
lista_celulares = []
#Filtra os dados desejados para a lista de celulares
for p in lista_produtos: 
    preco = str(p['offers'])
    preco = str(preco).replace("'", '"') #tratamento do texto para converter em json
    preco = json.loads(preco)
    lista_celulares.append(Celular(p['name'],preco['lowPrice'],preco['highPrice']))






con = conexaoBD()
cursor = con.cursor() 
cursor.execute("SELECT * FROM celular ORDER BY id DESC LIMIT 1") #selecionar o ultimo elemento da tabela
resultado = cursor.fetchall()


if(resultado[0][4].date() < dt.date.today() ): #verifica se a requisicao de hoje ja aconteceu
    for p in lista_celulares: 
        inserirBD(p,con)    
    inserirPosicao(con,resultado)    

con.close() #fecha conexao




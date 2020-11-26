import matplotlib.pyplot as plt
import matplotlib.dates as dt
from datetime import datetime
import pandas as pd 
import psycopg2
import math
import numpy as np
con = psycopg2.connect(host='localhost', database='celulares',user='postgres', password='admin',port='5432')
cursor = con.cursor() 
sql = "SELECT nome FROM celular group by id,nome ORDER BY id LIMIT 10  "
cursor.execute(sql)
nomes = pd.DataFrame(cursor.fetchall()) 
print(nomes)

sql = "SELECT nome,data,posicao FROM celular ORDER BY  data,posicao   "
cursor.execute(sql)
tabela = pd.DataFrame(cursor.fetchall()) 
con.close()

fig = plt.figure(figsize=(10, 12))
#print(tabela.loc[tabela[0]=='batata'])

for p in nomes[0]: 
    data = pd.to_datetime(tabela[1].loc[tabela[0]==p],format='’%Y-%m-%d' )
    plt.plot(data,tabela[2].loc[tabela[0]==p],marker="o",label=p)
print(tabela[1])
          
plt.ylabel('Posicao')
plt.yticks(np.arange(1,11))
#plt.xticks(tabela[1])            
plt.title("Celulares mais vendidos do Magazine Luiza")

plt.legend( bbox_to_anchor=(0.5,-0.1),loc='center',fancybox=True, shadow=True, ncol=3,prop={'size': 6})
plt.gca().invert_yaxis()
plt.show()






# fig, ax = plt.subplots()
# datas = pd.to_datetime(tabela[4])

# ax.plot(datas,tabela['posicao'])

# plt.show()
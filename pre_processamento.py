import numpy as np

# Checar se a matriz de tempo e ordem esta com as dimensoes corretas
def jsp_checar_tempo_ordem(_tempo, _ordem):
    tempo_n_linha, tempo_n_coluna = len(_tempo), len(_tempo[0])
    ordem_n_linha, ordem_n_coluna = len(_ordem), len(_ordem[0])
    
    if tempo_n_linha!=ordem_n_coluna or tempo_n_coluna!=ordem_n_linha:
        print("Erro: \n \t Tempo: ", (tempo_n_linha, tempo_n_coluna)
                    ,"\n \t Ordem: ", (ordem_n_linha, ordem_n_coluna))
        return False
    return True

def read_instance_from_taillard(nome_arquivo):
        
    instancias = []
    i = 0
    tempo=[]
    ordem=[]
    
    fl_tempo = False
    fl_ordem = False
    fl_instancia = False
    
    f = open("instancias/"+nome_arquivo, "r")
    
    for l in f:
        termos = l.split()
        if fl_ordem and len(termos) > 0 and termos[0] not in ("Machines", "Times", "Nb"):
            ordem.append([int(t) for t in termos])
        if fl_tempo and len(termos) > 0 and termos[0] not in ("Machines", "Times", "Nb"):
            tempo.append([int(t) for t in termos])
        if fl_instancia == True and len(tempo)>0:
            
            instancias.append({"id":i
                       ,"tempo":np.transpose(np.array(tempo))
                       ,"ordem":np.array(ordem)-1
                       ,"lista_ub":[0]})
            i = i+1
            tempo = []
            ordem = []
            fl_tempo = False
            fl_ordem = False
            fl_instancia = False
            
            
        if termos[0] == "Nb":
            fl_tempo = False
            fl_ordem = False
            fl_instancia = True
        elif termos[0]=="Times":
            fl_tempo = True
            fl_ordem = False
            fl_instancia = False
        elif termos[0]=="Machines":
            fl_tempo = False
            fl_ordem = True
            fl_instancia = False
            
    

    instancias.append({"id":i
                       ,"tempo":np.transpose(np.array(tempo))
                       ,"ordem":np.array(ordem)-1
                       ,"lista_ub":[0]})

    f.close()

    
    return instancias

def criar_instancias():
    instancias = []
    
    # n=4, m=3
    tempo = np.array([[1, 5, 5, 10],
                      [3, 8, 8, 6],
                      [2, 10, 4, 4]])
    ordem = np.array([[0, 1, 2], 
                      [1, 0, 2],
                      [0, 2, 1],
                      [2, 0, 1]])
    if jsp_checar_tempo_ordem(tempo, ordem):
        instancias.append({"id":0, "tempo": tempo, "ordem": ordem, "lista_ub":[0]})
    
    #n=5, m=3
    tempo = np.array([[1, 5, 5, 10, 7],
            		  [3, 8, 8, 6, 8], 
            		  [2, 10, 4, 4, 3]])
    ordem = np.array([[0, 1, 2],
            		  [1, 0, 2],
            		  [0, 2, 1],
            		  [2, 0, 1], 
            		  [1, 2, 0]])    
    if jsp_checar_tempo_ordem(tempo, ordem):
        instancias.append({"id":0, "tempo": tempo, "ordem": ordem, "lista_ub":[0]})
        
    arquivos_tai = ["tai15_15.txt", "tai20_15.txt", "tai20_20.txt", "tai30_15.txt", "tai50_15.txt", "tai50_20.txt", "tai100_20.txt"]

    for arq in arquivos_tai:
        instancias_tai = read_instance_from_taillard(arq)
        for tai in instancias_tai:
            if jsp_checar_tempo_ordem(tai["tempo"], tai["ordem"]):
                instancias.append(tai)
    id= 1
    for j in range(len(instancias)):
        instancias[j]["id"] = id
        id = id +1        
        
    return instancias

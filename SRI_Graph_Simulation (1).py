import networkx as nx
from networkx.generators.lattice import hexagonal_lattice_graph
from networkx.generators.lattice import triangular_lattice_graph
from networkx.classes.function import number_of_nodes
import sys
import numpy as np
import matplotlib.pyplot as plt
import random
from matplotlib.animation import FuncAnimation
from copy import deepcopy


class SRI_Vacc():

    def __init__(self,G_type,m,n,p_vac,p_inf,p_rec,p_rep,p_death,steps):
        if G_type=='Triangular':
            self.G=triangular_lattice_graph(m, n, periodic=False, with_positions=True, create_using=None)
        elif G_type=='Hexagonal':
            self.G=hexagonal_lattice_graph(m, n, periodic=False, with_positions=True, create_using=None)
        else:
            print('Please pass G_type either Triangular or Hexagonal')
            
        self.p_vac=int(p_vac*100)
        self.p_inf=int(p_inf*100)
        self.p_rec=int(p_rec*100)
        self.p_rep=int(p_rep*100)
        self.p_death=int(p_death*100)
        self.steps=steps
        
        self.n=number_of_nodes(self.G)
        
        self.inf_count_list=[]
        self.vac_count_list=[]
        self.sus_count_list=[]
        self.rec_count_list=[]
        self.death_count_list=[]
        self.birth_count_list=[]
        self.births=0
    
        nx.set_node_attributes(self.G,'S','State')
        nx.set_node_attributes(self.G,'y','Color')
        
        self.color_mapping_record=[]
        
        self.c=0
    
    def infection_init(self):
        vac_Chance=list(np.random.randint(1,100,self.n))
        inf_Chance=list(np.random.randint(1,100,self.n))
        for k,i,j in zip(self.G.nodes,vac_Chance,inf_Chance):
            if i<=self.p_vac:
                self.G.node[k]['State']='V'
                self.G.node[k]['Color']='g'
            elif j<=self.p_inf:
                self.G.node[k]['State']='I'
                self.G.node[k]['Color']='r'
                
            else:
                self.G.node[k]['State']='S'
                self.G.node[k]['Color']='y'
        self.update_state_counts()
        
    def update_state_counts(self):
        state_list=list(nx.get_node_attributes(self.G,'State').values())
        self.inf_count_list.append(state_list.count('I'))
        self.vac_count_list.append(state_list.count('V'))
        self.sus_count_list.append(state_list.count('S'))
        self.rec_count_list.append(state_list.count('R'))
        self.death_count_list.append(state_list.count('D'))
        self.birth_count_list.append(self.births)
        self.record_color_mapping()
        #return
    def reproduction(self,node):
        self.births+=1
        i,j=random.randint(0,100),random.randint(0,100)
        if i<=self.p_vac:
            self.G.node[node]['State']='V'
            self.G.node[node]['Color']='g'
        elif j<=self.p_inf:
            self.G.node[node]['State']='I'
            self.G.node[node]['Color']='r'
            
        else:
            self.G.node[node]['State']='S'
            self.G.node[node]['Color']='y'

    def spread_step(self):
        self.births=0
        for i in self.G.nodes:
            if self.G.node[i]['State']=='I':
                for nbr in self.G.neighbors(i):
                    if self.G.node[nbr]['State']=='S':
                        if random.randint(0,100)<=self.p_inf:
                            self.G.node[nbr]['State']='I'
                            self.G.node[nbr]['Color']='r'
                            
                if random.randint(0,100) <= self.p_rec:
                    self.G.node[i]['State'] = 'R'
                    self.G.node[i]['Color']='c'
                elif random.randint(0,100) <= self.p_death:
                    self.G.node[i]['State'] = 'D'
                    self.G.node[i]['Color']='w'
            if random.randint(0,100) <= self.p_rep:
                self.reproduction(i)


        self.update_state_counts()
    
    def simulate_spreading(self):
        self.__init__(G_type,m,n,p_vac,p_inf,p_rec,p_rep,p_death,steps)
        self.infection_init()
        for i in range(0,self.steps):
            self.spread_step()
        
            
    def record_color_mapping(self):
        color_map=[]
        for i in self.G.nodes:
            color_map.append(self.G.node[i]['Color'])
        self.color_mapping_record.append(color_map)



mult=3
pic_size=(mult*6,mult*4)
node_size= 60
G_type="Triangular"
m=60
n=120
p_vac=.9
p_inf=.2
p_rec=0.1
p_rep=0.05
p_death=0.01
steps=100
plague=SRI_Vacc(G_type,m,n,p_vac,p_inf,p_rec,p_rep,p_death,steps)
plague.simulate_spreading()
G=plague.G
pos = nx.get_node_attributes(G, 'pos')
color_map_list=plague.color_mapping_record
fig, ax = plt.subplots(figsize=pic_size)
fig.set_facecolor('k')
print('Green~Vaccinated\nYellow~Susceptible\nRed~Infected\nWhite~Dead\nCyan~Recovered\n')

def update(num):
    ax.clear()
    fig.set_facecolor('k')
    nx.draw(G, pos=pos, node_color=color_map_list[num], node_size=node_size,ax=ax, edge_color="gray")
    #ax.legend(labels=['Green~Vaccinated','Yellow~Susceptible','Red~Infected','White~Dead','Cyan~Recovered'])
    fig.set_facecolor('k')
#matplotlib.animation.
ani = FuncAnimation(fig, update, frames=len(color_map_list), interval=100, repeat=False)
plt.show()

ax.clear()
x=list(range(0,steps+1))
plt.plot(x,plague.inf_count_list,color='r',label='Infected')
plt.plot(x,plague.vac_count_list,color='g',label='Vaccinated')
plt.plot(x,plague.sus_count_list,color='y',label='Susceptible')
plt.plot(x,plague.rec_count_list,color='c',label='Recovered')
plt.plot(x,plague.death_count_list,color='k',label='Deaths')
plt.plot(x,plague.birth_count_list,color='m',label='Births')
plt.legend()
plt.xlabel('steps')
#title='# Trials='+ str(N_avg)+ ' Nodes='+str(N)+ ' P(Infect)='+str(pInfect)+ ' P(Vac)='+str(pVac)
#plt.title(title)
plt.ylabel('# People')
#plt.ylim(0,1)
plt.show()
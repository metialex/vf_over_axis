from glob import glob
from icecream import ic
from func import read_part_pos,calc_vf_global, set_domain, set_user_params
import matplotlib.pyplot as plt
from tqdm import tqdm
ic.disable()

#Standard input parameters parameters
div = 100 #number of divisions 
axis="x"
input_dir = './input_files/'
files_name = 'Particle*'
R_new = 0.5

#User defined variables
div,axis,input_dir,files_name,R_new = set_user_params(div,axis,input_dir,files_name,R_new)

#Main procedure
h5_files=glob(input_dir + files_name)

for h5_file in tqdm(h5_files):
    domain = set_domain(h5_file,div,axis)
    part_list=read_part_pos(h5_file,R_new)
    x,y = calc_vf_global(part_list,domain)
    plt.plot(x,y, color='blue',alpha=0.3) #(x,y,marker='o')
    ic(h5_file.split("/")[-1] + ' phi = ' + str(sum(y)/len(y))) #prints volume averaged phi
plt.show()

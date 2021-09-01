import pandas as pd
from icecream import ic
import numpy as np
import h5py
import argparse

def set_domain(path,n_div,axis):
    f = h5py.File(path, 'r')
    x_min=f.get('domain').get('xmin')[0]
    x_max=f.get('domain').get('xmax')[0]
    y_min=f.get('domain').get('ymin')[0]
    y_max=f.get('domain').get('ymax')[0]
    z_min=f.get('domain').get('zmin')[0]
    z_max=f.get('domain').get('zmax')[0]
    domain = {(x_min,x_max,y_min,y_max,z_min,z_max,n_div,axis)}
    domain = pd.DataFrame(domain, columns=['x_min', 'x_max', 'y_min','y_max','z_min', 'z_max', 'n_div','axis'])
    #test domain
    #domain = {(0.0,1.0,0.0,1.0,0.0,1.0,n_div,axis)}
    #domain = pd.DataFrame(domain, columns=['x_min', 'x_max', 'y_min','y_max','z_min', 'z_max', 'n_div','axis'])
    return domain

def read_part_pos(path,R_new):
    f = h5py.File(path, 'r')

    pos_fixed = f["fixed"]["X"][()]
    pos_mobile = f["mobile"]["X"][()]
    pos = np.concatenate((pos_fixed,pos_mobile))
    pos = pd.DataFrame(pos, columns=['xPos', 'yPos', 'zPos'])

    if (R_new == 0.0):
        R_fixed = f["fixed"]["R"][()]
        R_mobile = f["mobile"]["R"][()]
        R = np.concatenate((R_fixed,R_mobile))
        R = pd.DataFrame(R, columns=['R'])
    else:
        R = []
        R = [R_new for i in range(len(pos))]
        R = pd.DataFrame(R, columns=['R']) 
    part_list = pos.merge(R, left_index=True, right_index=True, how='inner')
    #test list
    #part_list={(0.5,0.5,0.25,0.5)}
    #part_list = pd.DataFrame(part_list, columns=['xPos', 'yPos', 'zPos','R'])
    return part_list

def set_axis(axis):
    if (axis =='y'):
        main_axis = ['y','x','z']
    elif (axis =='x'):
        main_axis = ['x','y','z']
    elif (axis =='z'):
        main_axis = ['z','y','x']
    return main_axis

def calc_vf_global(part_list,domain):
    pos=[]
    vf=[]
    ic(domain)
    axis = set_axis(domain['axis'][0])
    for dim in range(domain['n_div'][0]+1):
        plane = (domain[axis[0]+'_max'][0]-domain[axis[0]+'_min'][0])*(dim/domain['n_div'][0])
        pos.append(plane)
        vf.append(calc_vf_plane(part_list,domain,plane,axis))
    return pos,vf

def calc_vf_plane(part_list,domain,plane_pos, axis):
    cross_section_area = (domain[axis[1]+'_max'][0]-domain[axis[1]+'_min'][0])*(domain[axis[2]+'_max'][0]-domain[axis[2]+'_min'][0])
    particles_area = 0.0
    for index, particle in part_list.iterrows():
        R_eff =  R_eff_calc(plane_pos,particle,domain,axis)
        if (R_eff != 0.0):
            particles_area += np.pi*R_eff*R_eff
    return particles_area/cross_section_area

def R_eff_calc(plane_pos,particle,domain,axis):
    R_eff=0.0
    length=domain[axis[0]+'_max'][0]-domain[axis[0]+'_min'][0]
    if(abs(plane_pos-particle[axis[0]+'Pos']) <= particle['R']):
        cathetus = abs(plane_pos-particle[axis[0]+'Pos'])
        R_eff = np.sin(np.arccos(cathetus/particle['R']))*particle['R']
    elif(abs(plane_pos-particle[axis[0]+'Pos']+length) <= particle['R']):
        cathetus = abs(plane_pos-particle[axis[0]+'Pos']+length)
        R_eff = np.sin(np.arccos(cathetus/particle['R']))*particle['R']
    elif(abs(plane_pos-particle[axis[0]+'Pos']-length) <= particle['R']):
        cathetus = abs(plane_pos-particle[axis[0]+'Pos']-length)
        R_eff = np.sin(np.arccos(cathetus/particle['R']))*particle['R']
    return R_eff

def set_user_params(div,axis,input_dir,files_name,R_new):
    parser = argparse.ArgumentParser(description='Averagin parameters')
    parser.add_argument('-d', '--divisions', type=int,required=False, help='Number of planes over selected axis')
    parser.add_argument('-a', '--axis', type=str,required=False, help='The axis of averaging')
    parser.add_argument('-inp', '--input', type=str,required=False, help='The directory for input .h5 files')
    parser.add_argument('-f', '--files', type=str,required=False, help='The name patern of input files')
    parser.add_argument('-r', '--radius', type=float,required=False, help='New value of particles radii')

    args = parser.parse_args()
    if args.divisions:
        div=args.divisions
    if args.axis:
        axis=args.axis
    if args.input:
        input_dir=args.input
    if args.files:
        files_name=args.files
    if args.radius:
        R_new=args.radius
    return div,axis,input_dir,files_name,R_new
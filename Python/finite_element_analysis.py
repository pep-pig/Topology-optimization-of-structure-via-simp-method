import subprocess
import numpy as np
from numpy import *
import re
import global_variable


class FiniteElementAnalysis(object):
    """
    ANSYS 求解器

    Parameters
    ----------
    各路径的说明:
    cwd:存储ANSYS_APDL脚本，与ANSYS日志文件
    awd: 此目录为ANSYS的工作目录，所有需要在APDL中读入或输入的文件都在此目录下
    ANSYS_APDL读取文件与写入文件命名规范:
    读取文件:
    material.txt:材料文件,对于各向同性材料：Nx2，第一列杨氏模量，第二列泊松比，N为单元数
    写入文件:
    elements_nodes_counts.txt:单元数与节点数，1x2第一行单元数，第二行节点数
    elements_stiffness.out:未经处理的单元刚度矩阵文件
    elements_nodes.txt: 各单元对应的节点编号,Nx(k+1),N为单元数，第一列单元编号，剩下k列为节点编号
    elements_centers.txt: 各单元的中心坐标，Nx4，N为单元数，第一列为单元编号，其余三列为中心坐标值，（x,y,z)
    elements_volumn.txt: 各单元的体积，Nx2，N为单元数，第一列单元编号，第二列体积
    nodal_solution_u.txt: 节点位移，3列分别表示X,Y,Z方向位移
    nodal_solution_stress.txt: 节点应力，Vonmiss应力，一列，行数等于节点数
    nodal_solution_strain.txt: 节点应变，一列，行数等于节点数
    """
    def __init__(self):
        # 输入文件(APDL)和输出文件都将在cwd目录中，而ANSYS需要的其他输入数据或输出数据的路径，将由ANSYS的APDL指定


        if global_variable.TYPE == 'cantilever_benchmark':
        #---------------实验室台式机路径--------------------
            # self.meshdata_cmd = ["E:\Program Files\ANSYS Inc\\v170\ANSYS\\bin\winx64\MAPDL.exe", '-b', '-i',
            #        'H:\MaterThesis\ANSYS_SD\ANSYS_GUI\cantilever_benchmark\cantilever_benchmark_minf.txt', '-o', 'H:\MaterThesis\ANSYS_SD\ANSYS_GUI\cantilever_benchmark\cantilever_benchmark_minf.out']
            # self.result_cmd = ["E:\Program Files\ANSYS Inc\\v170\ANSYS\\bin\winx64\MAPDL.exe", '-b', '-i',
            #        'H:\MaterThesis\ANSYS_SD\ANSYS_GUI\cantilever_benchmark\cantilever_benchmark_rinf.txt', '-o', 'H:\MaterThesis\ANSYS_SD\ANSYS_GUI\cantilever_benchmark\cantilever_benchmark_rinf.out']
            # self.awd = 'H:/MaterThesis/ANSYS_SD/ANSYS_GUI/cantilever_benchmark/cantilever/'
            # self.dim = global_variable.DIM

        # ---------------工作站路径----------------
            # self.meshdata_cmd = ["D:\Program Files\ANSYS2017\ANSYS17.0\ANSYS Inc\\v170\ANSYS\\bin\winx64\MAPDL.exe", '-b', '-i',
            #        'D:\Fengjb\TopologyOptimization\SIMP\get_meshmodel_data.txt', '-o', 'D:\Fengjb\TopologyOptimization\SIMP\get_meshmodel_data.out']
            # self.result_cmd = ["D:\Program Files\ANSYS2017\ANSYS17.0\ANSYS Inc\\v170\ANSYS\\bin\winx64\MAPDL.exe", '-b', '-i',
            #        'D:\Fengjb\TopologyOptimization\SIMP\get_result_data.txt', '-o', 'D:\Fengjb\TopologyOptimization\SIMP\get_result_data.out']
            # self.awd = 'D:/Fengjb/TopologyOptimization/SIMP/'
            # self.dim = global_variable.DIM

        # ---------------pc路径----------------
            self.meshdata_cmd = ["F:\ANSYS 17.0\ANSYS Inc\\v170\ANSYS\\bin\winx64\MAPDL.exe", '-b', '-i',
                   'G:\Research\GitProject\Topology Optimization for Both Structure and Material\cantilever_benchmark\cantilever_benchmark_minf.txt', '-o', 'G:\Research\GitProject\Topology Optimization for Both Structure and Material\cantilever_benchmark\cantilever_benchmark_minf.out']
            self.result_cmd =   ["F:\ANSYS 17.0\ANSYS Inc\\v170\ANSYS\\bin\winx64\MAPDL.exe", '-b', '-i',
                   'G:\Research\GitProject\Topology Optimization for Both Structure and Material\cantilever_benchmark\cantilever_benchmark_rinf.txt', '-o', 'G:\Research\GitProject\Topology Optimization for Both Structure and Material\cantilever_benchmark\cantilever_benchmark_rinf.out']
            self.awd = 'G:/Research/MasterThesis/ANSYS_SD/ANSYS_GUI/cantilever_benchmark/cantilever/'
            self.dim = global_variable.DIM


        if global_variable.TYPE == 'complex2D_benchmark':
        # ---------------实验室台式机路径--------------------
        #     self.meshdata_cmd = ["E:\Program Files\ANSYS Inc\\v170\ANSYS\\bin\winx64\MAPDL.exe", '-b', '-i',
        #            'H:\MaterThesis\ANSYS_SD\ANSYS_GUI\complex2D_benchmark\complex2D_benchmark_minf.txt', '-o', 'H:\MaterThesis\ANSYS_SD\ANSYS_GUI\complex2D_benchmark\complex2D_benchmark_minf.out']
        #     self.result_cmd = ["E:\Program Files\ANSYS Inc\\v170\ANSYS\\bin\winx64\MAPDL.exe", '-b', '-i',
        #            'H:\MaterThesis\ANSYS_SD\ANSYS_GUI\complex2D_benchmark\complex2D_benchmark_rinf.txt', '-o', 'H:\MaterThesis\ANSYS_SD\ANSYS_GUI\complex2D_benchmark\complex2D_benchmark_rinf.out']
        #     self.awd = 'H:/MaterThesis/ANSYS_SD/ANSYS_GUI/complex2D_benchmark/complex2D/'
        #     self.dim = global_variable.DIM

        # ---------------pc路径----------------
            self.meshdata_cmd = ["F:\ANSYS 17.0\ANSYS Inc\\v170\ANSYS\\bin\winx64\MAPDL.exe", '-b', '-i',
                   'G:\Research\GitProject\Topology Optimization for Both Structure and Material\complex2D_benchmark\complex2D_benchmark_minf.txt', '-o', 'G:\Research\\GitProject\Topology Optimization for Both Structure and Material\complex2D_benchmark\complex2D_benchmark_minf.out']
            self.result_cmd =   ["F:\ANSYS 17.0\ANSYS Inc\\v170\ANSYS\\bin\winx64\MAPDL.exe", '-b', '-i',
                   'G:\Research\\GitProject\Topology Optimization for Both Structure and Material\complex2D_benchmark\complex2D_benchmark_rinf.txt', '-o', 'G:\Research\GitProject\Topology Optimization for Both Structure and Material\complex2D_benchmark\complex2D_benchmark_rinf.out']
            self.awd = 'G:/Research//MasterThesis/ANSYS_SD/ANSYS_GUI/complex2D_benchmark/complex2D/'
            self.dim = global_variable.DIM

        if global_variable.TYPE == 'complex3D_benchmark':
        # ---------------实验室台式机路径--------------------
        #     self.meshdata_cmd = ["E:\Program Files\ANSYS Inc\\v170\ANSYS\\bin\winx64\MAPDL.exe", '-b', '-i',
        #            'H:\MaterThesis\ANSYS_SD\APDL_Script\ANSYS_GUI\\versatile_simp\get_3D_benchmark_minf.txt', '-o', 'H:\MaterThesis\ANSYS_SD\APDL_Script\ANSYS_GUI\\versatile_simp\get_3D_benchmark_minf.out']
        #     self.result_cmd = ["E:\Program Files\ANSYS Inc\\v170\ANSYS\\bin\winx64\MAPDL.exe", '-b', '-i',
        #            'H:\MaterThesis\ANSYS_SD\APDL_Script\ANSYS_GUI\\versatile_simp\get_3D_benchmark_rinf.txt', '-o', 'H:\MaterThesis\ANSYS_SD\APDL_Script\ANSYS_GUI\\versatile_simp\get_3D_benchmark_rinf.out']
        #     self.awd = 'H:/MaterThesis/ANSYS_SD/APDL_Script/ANSYS_GUI/versatile_simp/cantilever'
        #     self.dim = global_variable.DIM

        # ---------------pc路径----------------
            self.meshdata_cmd = ["F:\ANSYS 17.0\ANSYS Inc\\v170\ANSYS\\bin\winx64\MAPDL.exe", '-b', '-i',
                   'G:\Research\GitProject\Topology Optimization for Both Structure and Material\complex3D_benchmark\complex3D_benchmark_minf.txt', '-o', 'G:\Research\\GitProject\Topology Optimization for Both Structure and Material\complex3D_benchmark\complex3D_benchmark_minf.out']
            self.result_cmd =   ["F:\ANSYS 17.0\ANSYS Inc\\v170\ANSYS\\bin\winx64\MAPDL.exe", '-b', '-i',
                   'G:\Research\\GitProject\Topology Optimization for Both Structure and Material\complex3D_benchmark\complex3D_benchmark_rinf.txt', '-o', 'G:\Research\GitProject\Topology Optimization for Both Structure and Material\complex3D_benchmark\complex3D_benchmark_rinf.out']
            self.awd = 'G:/Research//MasterThesis/ANSYS_SD/ANSYS_GUI/complex3D_benchmark/complex3D/'
            self.dim = global_variable.DIM
        if global_variable.TYPE == 'complex3D_benchmark_hex':
        # ---------------pc路径----------------
            self.meshdata_cmd = ["F:\ANSYS 17.0\ANSYS Inc\\v170\ANSYS\\bin\winx64\MAPDL.exe", '-b', '-i',
                   'G:\Research\GitProject\Topology Optimization for Both Structure and Material\\NewAlgorithm\complex3D_benchmark_hex_minf.txt', '-o', 'G:\Research\\GitProject\Topology Optimization for Both Structure and Material\\NewAlgorithm\complex3D_benchmark_hex_minf.out']
            self.result_cmd =   ["F:\ANSYS 17.0\ANSYS Inc\\v170\ANSYS\\bin\winx64\MAPDL.exe", '-b', '-i',
                   'G:\Research\\GitProject\Topology Optimization for Both Structure and Material\\NewAlgorithm\complex3D_benchmark_hex_rinf.txt', '-o', 'G:\Research\GitProject\Topology Optimization for Both Structure and Material\\NewAlgorithm\complex3D_benchmark_hex_rinf.out']
            self.awd = 'G:/Research//MasterThesis/ANSYS_SD/ANSYS_GUI/NewAlgorithm/'
            self.dim = global_variable.DIM

    def boot(self):
        subprocess.call(self.meshdata_cmd)

    def get_counts(self,element_nodes_file):
        """
        获取单元数和节点数

        Parameters
        ----------
        element_nodes_file:存储单元数和节点数的文件

        Returns
        ----------
        返回单元数和节点数
        """
        counts = loadtxt(element_nodes_file,dtype = int)
        return counts[0],counts[1]


    def generate_material_properties(self,x):
        """
        将OC方法获得的x生成新的材料文件，对于各向异性的点阵材料而言，其材料属性文件将由子类实现

        Parameters
        ----------
        x : 单元密度
        penal : 惩罚因子

        Returns
        ----------
        将生成的材料文件存入material.txt
        """
        nu = global_variable.NU * np.ones((global_variable.ELEMENT_COUNTS))
        ex = (x**global_variable.PENAL)*(global_variable.E)
        material = np.array([nu, ex]).T
        np.savetxt(self.awd+"material.txt", material, fmt=' %-.7E', newline='\n')


    def get_meshmodel_data(self):
        """
        获取有限元模型相关数据,这些数据在迭代计算中属于不变量，只需单独调用该函数一次

        Parameters
        ----------
        dim:单元刚度矩阵的维度

        Returns
        ----------
        k:单元刚度矩阵集合
        element_attributes:单元对应的节点编号
        centers:单元的中心坐标
        v:单元体积
        """

        element_attributes = loadtxt(self.awd+'elements_nodes.txt', dtype=int)
        centers = loadtxt(self.awd+'elements_centers.txt')
        v = loadtxt(self.awd+'elements_volumn.txt')
        node_coordinates =loadtxt(self.awd+'node_coordinates.txt')
        return element_attributes,centers,v,node_coordinates


    def get_result_data(self,x):
        """
        更新材料密度，进行有限元分析并获取结果数据文件
        """
        self.generate_material_properties(x)
        subprocess.call(self.result_cmd)
        u = loadtxt(self.awd+'nodal_solution_u.txt',dtype=float)
        stress = loadtxt(self.awd+'nodal_solution_stress.txt',dtype = float)
        strain = loadtxt(self.awd+'nodal_solution_strain.txt',dtype = float)
        return u,stress[:,1],strain[:,1]

#单元测试
if __name__=='__main__':
    global_variable.initialize_global_variable(DIM = 24)
    x = 0.4 * np.ones(global_variable.ELEMENT_COUNTS)
    ansys_solver = FiniteElementAnalysis(dim = 24)
    ansys_solver.get_result_data(x=x,penal=3)







from finite_element_analysis import *
from postprocessor import *
from numpy import *


global ELEMENT_COUNTS,ELEMENT_ATTRIBUTES,NODE_COORDINATES,NODE_COUNTS,CENTERS,V,K


def initialize_global_variable(DIM):
    '''
    以待求解的有限元模型座位输入，产生全局变量
    Parameter
    ----------
    DIM:单元刚度矩阵的维度

    Returns
    ----------
    在整个计算过程中不发生改变的全局变量

    '''
    global ELEMENT_COUNTS, ELEMENT_ATTRIBUTES, NODE_COORDINATES, NODE_COUNTS, CENTERS, V, K
    ANSYS_SOLVER = FiniteElementAnalysis(DIM)
    ELEMENT_COUNTS, NODE_COUNTS = ANSYS_SOLVER.get_counts(ANSYS_SOLVER.awd + 'elements_nodes_counts.txt')
    K, ELEMENT_ATTRIBUTES, CENTERS, V, NODE_COORDINATES = ANSYS_SOLVER.get_meshmodel_data()


from finite_element_analysis import *
from postprocessor import *
from numpy import *


global ELEMENT_COUNTS,ELEMENT_ATTRIBUTES,NODE_COORDINATES,NODE_COUNTS,CENTERS,V,DIM,GRID_TYPE,TYPE
global R, E, NU, PENAL, MOVE,VOLFAC

def hyperparameter(r,penal,volfac,move,e,nu):
    global R, E, NU, PENAL, MOVE,VOLFAC
    R=r
    PENAL=penal
    MOVE=move
    E=e
    NU=nu
    VOLFAC = volfac

def initialize_global_variable(type):
    '''
    以待求解的有限元模型座位输入，产生全局变量
    Parameter
    ----------
    DIM:单元刚度矩阵的维度

    Returns
    ----------
    在整个计算过程中不发生改变的全局变量

    '''
    global ELEMENT_COUNTS, ELEMENT_ATTRIBUTES, NODE_COORDINATES, NODE_COUNTS, CENTERS, V, K,DIM,GRID_TYPE,TYPE
    TYPE = type
    if TYPE =='top2d':
        DIM = 8
        GRID_TYPE = 'Polygon'
    if TYPE =='top3d':
        DIM = 24
        GRID_TYPE = 'Hexahedron'
    ANSYS_SOLVER = FiniteElementAnalysis()
    # ANSYS_SOLVER.boot()
    ELEMENT_COUNTS, NODE_COUNTS = ANSYS_SOLVER.get_counts(ANSYS_SOLVER.awd + 'elements_nodes_counts.txt')
    ELEMENT_ATTRIBUTES, CENTERS, V, NODE_COORDINATES = ANSYS_SOLVER.get_meshmodel_data()



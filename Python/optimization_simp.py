from numpy import *
import numpy as np
import global_variable
from finite_element_analysis import *
from postprocessor import *
from traits.api import HasTraits, Instance, Property, Enum,Range,on_trait_change,Int
import  time

from mayavi import mlab
class Simp(HasTraits):
    """
    函数中各个parameter:

    Parameters
    ----------
    需要从ANSYS获得以及需要用户输入的数据：
    U:  NxL列向量，节点解，N为节点数,L为坐标轴数，2D对应x,y.3D对应x,y,z
    stress:Nx2数组，第一列节点编号，第二列修匀后的节点应力
    strain:Nx2数组，第一类节点编号，第二列修匀后的节点应变
    K: ExRxL数组,单元刚度矩阵汇总，E为单元数,R、L为单元刚度矩阵的行和列
    ELEMENT_ATTRIBUTES:  ExN数组，单元信息，E是单元数，N为单元节点编号
    CENTERS: Ex3数组，单元中心坐标, E单元数目，每行3列分别为中心x、y、z坐标
    V:1xE数组，单元体积，E单元数目
    penal: 标量，simp法的密度惩罚因子
    volfrac:  标量，体积减少百分比
    rmin: 标量，SIMP法棋盘格现象抑制范围，与结构最小杆件的尺寸将与rmin接近

    SIMP法需要的arguments：ue，k0，center,v,penal,volfrac,rmin,xe
    Ue:各个单元的节点解
    Ke:各个单元刚度矩阵
    center:各个单元的中心坐标
    Ve:各个单元的体积
    penal: 标量，simp法的密度惩罚因子
    volfrac:  标量，体积减少百分比
    rmin:标量，SIMP法棋盘格现象抑制范围，与结构最小杆件的尺寸将与rmin接近
    x:  1xE数组，各个单元的相对密度，也是simp法求解的目标
    """

    loop = Int(0)#以loop作为图形更新的监听对象
    def __init__(self):
        #初始化所需要的数据
        self.resultdata = ResultData()
        self.ansys_solver = FiniteElementAnalysis()
        self.strain_energy = []
        self.finished = False
    
    # A new algorithm
    def get_distance_table(self):
        neibors = np.loadtxt(self.ansys_solver.awd+'neibors.txt', dtype=int)
        neiborslist = []
        for i in range(neibors.shape[0]):
            index = neibors[i, np.where(neibors[i, :] > 0)]
            neiborslist.append(index-1)

        coordinates = np.loadtxt(self.ansys_solver.awd+'elements_centers.txt', dtype=float)[:, 1:]
        weights = []
        i = 0
        for neibor in neiborslist:
            b = coordinates[neibor[:]]
            distance = np.sqrt(np.sum((coordinates[neibor,:] - coordinates[i,:]) ** 2, axis=-1))
            weight = (global_variable.R-distance)
            weight[np.where(weight<0)] = 0
            # weight = (global_variable.R) * np.max(distance) - distance
            weights.append(weight)
            i = i+1
        return neiborslist,weights

    def de_checkboard(self,x, dc):
        corrected_dc = []
        i = 0
        x = np.array(x)
        dc = np.array(dc)
        index = np.where(dc<0)
        print('old_index:',index)
        j = 0
        for _ in dc:
            corrected_dc_demonimator = 0.0
            corrected_dc_numerator = 0.0
            elements =self.neiborslist[j].tolist()[0]
            corrected_dc_demonimator = np.sum(self.weights[j])
            corrected_dc_numerator = np.sum(self.weights[j] * x[elements[:]] * dc[elements[:]])
            corrected_dc.append(corrected_dc_numerator / (x[j] * corrected_dc_demonimator))
            j=j+1
        index = np.where(array(corrected_dc)<0)
        print('index:',index)
        return corrected_dc

    def oc(self, x, volfrac, corrected_dc):
        """
        优化准则法
        """
        lambda1 = 0; lambda2 = 100000; move = global_variable.MOVE
        while(lambda2-lambda1>1e-4):
            lambda_mid = 0.5*(lambda2+lambda1)
            #index = np.where(array(corrected_dc)<0)
            B = x*sqrt((array(corrected_dc,dtype = float))/(lambda_mid * global_variable.V[:,1]))
            xnew = maximum(0.001, maximum(x-move, minimum(1.0, minimum(x + move,B))))#由里到外，先比上界，再比下界
            if sum(xnew*global_variable.V[:,1])-volfrac*sum(global_variable.V[:,1])>0:
                lambda1 = lambda_mid
            else:
                lambda2 = lambda_mid
        return xnew

   

    def simp(self):
        """
        SIMP优化算法
        """
        #初始化数据
        penal = global_variable.PENAL
        volfrac = global_variable.VOLFAC
        rmin = global_variable.R
        self.neiborslist,self.weights = self.get_distance_table()
        x = volfrac*np.ones(global_variable.ELEMENT_COUNTS)
        change_c = change_x = 1;
        c_total= 0
        Emin = 1e-9
        #开始迭代
        while change_x > 0.05 and self.loop<30:
            c_old =c_total
            xold = x;
            U, stress, strain = self.ansys_solver.get_result_data(x)
            c = np.loadtxt(self.ansys_solver.awd+'strain_energy.txt',dtype = float).reshape(global_variable.ELEMENT_COUNTS,1)*2
            uku = c/(x.reshape((global_variable.ELEMENT_COUNTS,1))**penal)
            dc = (penal*(x.reshape((global_variable.ELEMENT_COUNTS,1))** (penal-1)))*uku
            c_total = sum(c, axis=0)[0]
            dc = dc[:,0].tolist()
            #更新每个单元应变能对与密度的敏度：消除棋盘格现象的敏度过滤算法
            corrected_dc = self.de_checkboard(x, dc)
            #OC优化准则发对密度进行更新
            x = self.oc(x, volfrac, corrected_dc)
            change_x = abs(max(x-xold))
            change_c = abs(c_old - c_total)
            self.strain_energy.append(c_total)
            print("change_c:",change_c,"    change_x:",change_x,"    c：",c_total,"    loop:",self.loop)
            #更新每一次迭代的结果，整个内存只保存了当前迭代结果
            self.resultdata.undate_ansys_date(U, stress, strain, x)
            #将每一步的迭代结果写入本地内存，以为后续生成动画
            self.resultdata.write_unstructured_data(loop=self.loop)
            self.loop = self.loop + 1

            # if self.loop>3:
            #     break
        self.finished = True
        return x

#单元测试
if __name__=='__main__':
    global_variable.initialize_global_variable(DIM = 8)
    simp_solver = Simp(dim = 8)
    density = simp_solver.simp()

    # x = simp_solver.x_axis
    y = simp_solver.strain_energy
    # z = simp_solver.z_axis
    l = mlab.plot3d(x, y, z, representation='surface')
    # l = mlab.plot3d()
    mlab.show()








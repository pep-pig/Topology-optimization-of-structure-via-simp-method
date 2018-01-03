from numpy import *
import numpy as np
from finite_element_analysis import *


class SIMP(object):
    """
    函数中各个parameter:

    Parameters
    ----------
    需要从ANSYS获得以及需要用户输入的数据：
    U:  1xN列向量，节点解，N为节点数
    K: ExRxL数组,单元刚度矩阵汇总，E为单元数,R、L为单元刚度矩阵的行和列
    element_attributes:  ExN数组，单元信息，E是单元数，N为单元节点编号
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
    def __init__(self,dim = 8):
        #初始化所需要的数据
        #单元刚度矩阵的维度
        self.ansys_solver = FEA()
        self.element_counts = self.ansys_solver.element_counts
        self.node_counts = self.ansys_solver.node_counts
        self.K, self.element_attributes, self.CENTERS, self.V = self.ansys_solver.get_meshmodel_data(dim)
        self.distance = self.get_distance_table()


    def get_distance_table(self):
        """
        生成单元中心之间的距离表格distance

        Returns
        ----------
        distance:单元中心之间的距离

        Examples
        ----------
        distance[3][4]:表示3号与4号单元之间的距离

        """
        length = self.CENTERS.shape[0]
        distance = zeros(shape = (length, length))
        for i in range(length):
            for j in range(i+1,length):
                distance[i,j] = np.linalg.norm(self.CENTERS[i,1:]-self.CENTERS[j,1:])
        distance+=distance.T
        return distance


    def de_checkboard(self,rmin, x, dc):
        """
        更新每个单元应变能对与密度的敏度,消除棋盘格现象与网格不独立现象的敏度过滤算法

        Parameters
        ----------
        rmin:最小过滤半径
        x:单元密度
        dc:没有过滤的敏度

        Returns
        ----------
        corrected_dc:过滤之后的敏度
        """
        a = array(dc,dtype = float)
        corrected_dc = []
        i = 0
        for _ in dc:
            corrected_dc_demonimator = 0.0
            corrected_dc_numerator = 0.0
            #寻找对当前单元满足条件 rmin-distance>0的elements
            satisfied_elements,delta = self.find_satisfied_elements(i,rmin)
            j=0
            for element in satisfied_elements[0]:
                Hf =self.V[element,1]*delta[j]
                corrected_dc_demonimator = corrected_dc_demonimator+Hf
                corrected_dc_numerator = corrected_dc_numerator + Hf * x[element] * dc[element]
                j=j+1
            corrected_dc.append(corrected_dc_numerator/(x[i]*corrected_dc_demonimator))
            i = i+1
        return corrected_dc


    def find_satisfied_elements(self,i,rmin):
        """
        寻找当前单元i周围中心距离在rmin以内的单元

        Returns
        ----------
        satisfied_elements:在过滤半径之内的单元
        delta:距离差
        """
        result = rmin -self.distance[i]
        satisfied_elements = np.argwhere(result>0).T
        delta = result[satisfied_elements[0].tolist()]
        return satisfied_elements,delta


    def OC(self,x, volfrac, corrected_dc):
        """
        优化准则法
        """
        lambda1 = 0; lambda2 = 100000; move = 0.2
        while(lambda2-lambda1>1e-4):
            lambda_mid = 0.5*(lambda2+lambda1)
            B = x*sqrt(array(corrected_dc,dtype = float)/(lambda_mid * self.V[:,1]))
            xnew = maximum(0.001, maximum(x-move, minimum(1.0, minimum(x + move,B))))#由里到外，先比上界，再比下界
            if sum(xnew*self.V[:,1])-volfrac*sum(self.V[:,1])>0:
                lambda1 = lambda_mid
            else:
                lambda2 = lambda_mid
        return xnew


    def simp(self,penal = 3, volfrac = 0.4, rmin = 1.2):
        """
        SIMP优化算法
        """
        #初始化数据
        x = volfrac*np.ones(self.element_counts)
        loop = 0;
        change = 1;
        #开始迭代
        while change > 0.01:
            loop = loop+1;
            xold = x;
            U, stress, strain = self.ansys_solver.get_result_data(x,penal)
            #目标函数与敏度分析
            c = 0     #总应变能
            i = 0
            dc = []
            for xe in  x:
                nodes_number = self.element_attributes[i]
                Ue = []
                for node_number in nodes_number:
                    Ue.append(U[node_number-1][0])
                    Ue.append(U[node_number-1][1])
                Ue = array(Ue)
                k = self.K[i]
                c = c + (xe**penal)*matrix(Ue)*matrix(self.K[i])*matrix(Ue).T
                dc.append((penal*(xe**(penal-1))*(matrix(Ue)*matrix(self.K[i])*matrix(Ue).T))[0,0])
                i = i+1
            #更新每个单元应变能对与密度的敏度：消除棋盘格现象的敏度过滤算法
            corrected_dc = self.de_checkboard( rmin, x, dc)
            #OC优化准则发对密度进行更新
            x = self.OC(x, volfrac, corrected_dc)
            change = max(abs(x-xold))
            print("change:",change,"    c：",c[0,0],"    loop:",loop)
        return U,stress,strain,x
#单元测试
if __name__=='__main__':
    simp_solver = SIMP()
    U,stress,strain,x = simp_solver.simp()






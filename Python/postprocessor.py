#standard import
import numpy as np
from numpy import *

#user defined pakages import
import global_variable

#enthought import
from tvtk.api import tvtk
from mayavi import mlab
from mayavi.sources.vtk_data_source import VTKDataSource


class ResultData(object):
    #定义写入类
    #tvtk的写入类，与vtk的写入类很类似，在mayavi中，不能直接用vtk类，而要用由python 对vtk封装后的 tvtk,如果需要读数据，也可以用类似的API
    writer =tvtk.XMLUnstructuredGridWriter()
    def __init__(self):
        '''
        初始化结果数据，为画图做准备
        以unstrgrid开头的数据属于 vtk的非结构网格数据，这种数据可以保存到本地，但是不能直接用来绘图
        需要通过VTKDataSource 作为接口，生成mayavi可以渲染的数据源
        以vtkdatasource开头的数据属于经过了VTKDataSource函数处理过的数据，可以被mayavi渲染
        '''
        self.index = []
        self.U = np.zeros((global_variable.NODE_COUNTS,1))
        self.stress = np.zeros((global_variable.NODE_COUNTS,1))
        self.strain = np.zeros((global_variable.NODE_COUNTS,1))
        self.density = np.ones((global_variable.ELEMENT_COUNTS,1))



        #unstructuredgrid 类型数据
        self.unstrgrid_mesh = None
        self.unstrgrid_density = None
        self.unstrgrid_stress = None
        self.unstrgrid_strain = None
        self.unstrgrid_displacement = None
        #vtksource类型数据
        self.vtkdatasource_mesh = None
        self.vtkdatasource_displacement = None
        self.vtkdatasource_stress = None
        self.vtkdatasource_strain = None
        self.vtkdatasource_density = None
        #初始化unstructuredgrid 与 vtkdatasource
        self.initialize()

    #以用户自定义值 初始化#初始化unstructuredgrid 与 vtkdatasource
    def initialize(self):
        self.unstrgrid_mesh = self.generate_unstrgrid_mesh()
        self.unstrgrid_density = self.generate_unstrgrid_mesh()
        self.unstrgrid_stress = self.generate_unstrgrid_mesh()
        self.unstrgrid_strain = self.generate_unstrgrid_mesh()
        self.unstrgrid_displacement = self.generate_unstrgrid_mesh()
        self.write_unstructured_data()
        self.vtkdatasource()

    def undate_ansys_date(self, U, stress, strain, x):
        self.U = U
        self.stress= stress
        self.strain = strain
        self.density = x

    #生成非结构网格数据
    def write_unstructured_data(self, loop = -1):
        '''
        设置if条件语句是为了第一次初始化的结果不写入本地文件
        '''
        # 存储位移数据
        self.update_unstrgrid_displacement(self.U, 0.05, 0)
        if loop!=-1:
            name = 'displacement_0'+str(loop+1)+'.vti'
            #设置写入的文件
            self.writer.set_input_data(self.unstrgrid_displacement)
            #设置写入文件的名称
            self.writer.file_name = 'Displacement\\'+name
            #开始写入
            self.writer.write()

        # 应力数据
        self.update_unstrgrid_stress(self.stress)
        if loop!=-1:
            name = 'stress_0'+str(loop)+'.vti'
            self.writer.set_input_data(self.unstrgrid_stress)
            self.writer.file_name = 'Stress\\'+name
            self.writer.write()



        # 应变数据
        self.update_unstrgrid_strain(self.strain)
        if loop!=-1:
            name = 'strain_0'+str(loop)+'.vti'
            self.writer.set_input_data(self.unstrgrid_strain)
            self.writer.file_name = 'Strain\\'+name
            self.writer.write()


        # 密度数据
        self.update_unstrgrid_density(self.density)
        if loop!=-1:
            name = 'density_0'+str(loop)+'.vti'
            self.writer.set_input_data(self.unstrgrid_density)
            self.writer.file_name = 'Density\\'+name
            self.writer.write()

    #生成vtkdata类型数据
    def vtkdatasource(self):
        self.vtkdatasource_mesh = VTKDataSource(data=self.unstrgrid_mesh, name='Geometry')
        self.vtkdatasource_displacement = VTKDataSource(data=self.unstrgrid_displacement, name='DisplacementData')
        self.vtkdatasource_stress = VTKDataSource(data=self.unstrgrid_stress, name='StessData')
        self.vtkdatasource_strain = VTKDataSource(data=self.unstrgrid_strain, name='StrainData')
        self.vtkdatasource_density = VTKDataSource(data=self.unstrgrid_density, name='DensiytData')

    #生成网格数据，filter参数是为了过滤我们不想显示的密度单元，1表示全部显示，0表示全部不显示
    def generate_unstrgrid_mesh(self, filter = 1):
        points = global_variable.NODE_COORDINATES
        self.index = where(self.density>=(1.0-filter))[0].tolist()
        cells = (global_variable.ELEMENT_ATTRIBUTES[self.index,:]-1)
        cell_tpye = tvtk.Polygon().cell_type
        rectangle = tvtk.UnstructuredGrid(points = points)
        rectangle.set_cells(cell_tpye,cells)
        return  rectangle

    #生成密度数据
    def update_unstrgrid_density(self, density):

        self.unstrgrid_density.cell_data.scalars = density[self.index]
        self.unstrgrid_density.cell_data.scalars.name = 'density'


    #生成位移数据，scale1表示单纯位移图形的位移缩放因子，scale2用于应力、应变、密度图形的位移缩放
    def update_unstrgrid_displacement(self, U, scale1 = 0.05, scale2 = 0):
        if U.shape[1] == 2:
            U=np.column_stack((U,zeros(U.shape[0])))
        self.unstrgrid_displacement.points = global_variable.NODE_COORDINATES + scale1 * U
        self.unstrgrid_displacement.point_data.scalars = sqrt(sum(U ** 2, axis = 1))
        self.unstrgrid_displacement.point_data.scalars.name = 'USUM'
        self.unstrgrid_density.points = global_variable.NODE_COORDINATES + scale2 * U
        self.unstrgrid_strain.points = global_variable.NODE_COORDINATES + scale2 * U
        self.unstrgrid_stress.points = global_variable.NODE_COORDINATES + scale2 * U


    #生成应力数据
    def update_unstrgrid_stress(self, stress):
        self.unstrgrid_stress.point_data.scalars = stress
        self.unstrgrid_stress.point_data.scalars.name = 'stress'


    #生成应变数据
    def update_unstrgrid_strain(self, strain):
        self.unstrgrid_strain.point_data.scalars = strain
        self.unstrgrid_strain.point_data.scalars.name = 'strain'




if __name__=='__main__':
    mymodel = ResultData()


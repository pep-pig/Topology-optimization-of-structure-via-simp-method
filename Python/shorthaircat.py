# -*- coding: utf-8 -*-

# Standard imports.
import numpy as np
from numpy import e
import threading
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import matplotlib.ticker as ticker

#user defined pakages import
from optimization_simp import Simp
from postprocessor import ResultData
import global_variable
from vtu2stl import *

# Enthought imports.
from traits.api import HasTraits, Instance, Property, Enum,Range,on_trait_change,Button,ToolbarButton#导入所需要的类型HasTraits：基类，Instance：实例类型 Property: Enum:枚举类型
from traitsui.api import View, Item, Group,HSplit, VSplit, InstanceEditor,RangeEditor#导入traits属性的可视化api
from tvtk.pyface.scene_editor import SceneEditor#导入场景配置api
from mayavi.core.api import PipelineBase,Engine
from mayavi.sources.vtk_data_source import VTKDataSource
from mayavi.modules.api import Surface , Volume
from mayavi.core.ui.engine_view import EngineView#导入引擎可视化模块
from mayavi.core.ui.mayavi_scene import MayaviScene
from mayavi.tools.mlab_scene_model import MlabSceneModel#导入mlab 绘图窗口的可视化模型
from mayavi import mlab

######################################################################
class ShorthairCat(HasTraits):
    '''
    所有拥有traits属性的类都需要从HasTraits类继承
    '''
    density_filter = Range(0.0,1.0,0.5)

    calculate_button = ToolbarButton('Calculate')

    initial_button = Button('initialize')
    animate_button = Button('animate')

    # The scene model.
    scene  = Instance(MlabSceneModel,())#此处进行了初始化
    scene0 = Instance(MlabSceneModel,())#位移场景
    scene1 = Instance(MlabSceneModel,())#应力场景
    scene2 = Instance(MlabSceneModel,())#应变场景
    scene3 = Instance(MlabSceneModel,())#密度场景
    scene4 = Instance(MlabSceneModel,())#动图场景

    plot = Instance(PipelineBase)#生成动画的实例

    # The mayavi engine view.
    engine_view = Instance(EngineView)

    # The current selection in the engine tree view.
    current_selection = Property

    ######################
    main_view = View(
                Group(
                              Group(HSplit(HSplit(VSplit(
                              Item(name='engine_view',
                                   style='custom',
                                   resizable=True,
                                   height =500,
                                   width = 200,
                                   show_label=False

                                   ),
                                     ),
                              Item(name='current_selection',
                                   editor=InstanceEditor(),
                                   enabled_when='current_selection is not None',
                                   style='custom',
                                   resizable = True,
                                   height = 500,
                                   width = 200,
                                   springy=True,
                                   show_label=False),
                                   )),label = 'Settings',show_border = False),
                              Group(
                                  Group(

                                      Item(name = 'density_filter',editor = RangeEditor()),
                                      '_',
                                      HSplit(
                                      Item('initial_button', show_label=False),

                                      Item('calculate_button', show_label=False),
                                      Item('animate_button', show_label=False))

                                  ),
                                  Group(
                                       Item(name='scene',
                                            editor=SceneEditor(),
                                            show_label=False,
                                            resizable=True,
                                            springy = True,
                                            height=600,
                                            width=600,
                                            label = 'mesh'
                                            ),
                                      Item(name='scene0',
                                           editor=SceneEditor(),
                                           show_label=False,
                                           resizable=True,
                                           springy=True,
                                           height=600,
                                           width=600,
                                           label='displacement'
                                           ),
                                       Item(name='scene1',
                                            editor=SceneEditor(),
                                            show_label=False,
                                            resizable=True,
                                            springy=True,
                                            height=600,
                                            width=600,
                                            label = 'stress'
                                            ),
                                       Item(name='scene2',
                                            editor=SceneEditor(),
                                            show_label=False,
                                            resizable=True,
                                            springy=True,
                                            height=600,
                                            width=600,
                                            label = 'strain'
                                            ),
                                      Item(name='scene3',
                                           editor=SceneEditor(),
                                           show_label=False,
                                           resizable=True,
                                           springy=True,
                                           height=600,
                                           width=600,
                                           label='density'
                                           ),
                                      Item(name='scene4',
                                           editor=SceneEditor(),
                                           show_label=False,
                                           resizable=True,
                                           springy=True,
                                           height=600,
                                           width=600,
                                           label='animating'
                                           ),
                                      layout = 'tabbed'),

                                  orientation = 'vertical'),
                    orientation = 'horizontal'
                ),
                height = 600,
                width = 760,
                resizable=True,
                # scrollable=True,
                title = 'ShorthairCat',
                )

    #**traits 表示传入参数的个数不确定
    def __init__(self,type,r,penal,move,e,nu,volfac,**traits):

        HasTraits.__init__(self, **traits)
        self.scene.mayavi_scene.name = 'Geometry'
        self.scene.foreground = (1,170/255,0)
        self.scene0.mayavi_scene.name = 'Displacement'
        self.scene1.mayavi_scene.name = 'Stress'
        self.scene2.mayavi_scene.name = 'Strain'
        self.scene3.mayavi_scene.name = 'Density'
        self.scene4.mayavi_scene.name = 'Animate'

        #初始化enine_view
        self.engine_view = EngineView(engine=self.scene.engine)

        #对current_selection 进行动态监听，如果current_selection的值发生变化就调用 self._selection_change

        self.scene.engine.on_trait_change(self._selection_change,name = 'current_selection')
        self.simp_solver = None
        self.type = type
        self.r = r
        self.penal = penal
        self.move = move
        self.e = e
        self.nu = nu
        self.volfac = volfac
        self.address = 'H:\GitHub\Topology-optimization-of-structure-via-simp-method'
        self.i = 1
    def _initial_button_fired(self):
        self.initial_thread = threading.Thread(target = self._initial,args=(),name='Thread-1')
        self.initial_thread.daemon = True
        self.initial_thread.start()

    def _initial(self):
        global_variable.hyperparameter(r=self.r,move=self.move,e=self.e,penal=self.penal,nu=self.nu,volfac=self.volfac)
        global_variable.initialize_global_variable(type =self.type)
        self.simp_solver = Simp()
        self._mayavi()
        self.simp_solver.on_trait_change(self._update_vtkdatasource,name = 'loop')
        self.simp_solver.on_trait_change(self._save_fig, name='loop',dispatch = 'ui')
    def _save_fig(self):
        path = 'H:\GitHub\Topology-optimization-of-structure-via-simp-method\\fig\\'
        fname = path + 'density' + str(self.simp_solver.loop) + '.png'
        self.scene3.mayavi_scene.scene.save(fname)





    def _calculate_button_fired(self):
        #监听loop，一改变立刻更新曲线，同时建立background thread ,在后台进行有限元计算
        # self.simp_solver.on_trait_change(self._plot_convergence_curve, name='loop', dispatch='new')#TODO 发现如果用dispatch = 'ui' 有很大几率卡死,但是这个模式会报错，不过不影响使用
        #self.simp_solver.on_trait_change(self._plot,name = 'loop')

        self.computation_thread = threading.Thread(target=self.simp_solver.simp,args=(),name= 'Thread-2')
        self.computation_thread.daemon = True
        self.computation_thread.start()

        self.plot_thread = threading.Thread(target = self._plot_convergence_curve,args = (),name = 'Thread-3')
        self.plot_thread.daemon = True
        self.plot_thread.start()




    def _animate_button_fired(self):
        #创建一个background thread 不停的显示动画
        animate_thread = threading.Thread(target= self._animate(),args=())
        animate_thread.daemon = True
        animate_thread.start()

    # 静态监听密度过滤器
    def _density_filter_changed(self):
        print('the density is :',self.density_filter)
        self.simp_solver.resultdata.unstrgrid_density = self.simp_solver.resultdata.generate_unstrgrid_mesh(self.density_filter)
        self.simp_solver.resultdata.update_unstrgrid_density(self.simp_solver.resultdata.density)
        self.simp_solver.resultdata.vtkdatasource_density.data = self.simp_solver.resultdata.unstrgrid_density
        self.simp_solver.resultdata.vtkdatasource_density.update()

        self.simp_solver.resultdata.unstrgrid_stress = self.simp_solver.resultdata.generate_unstrgrid_mesh(self.density_filter)
        self.simp_solver.resultdata.update_unstrgrid_stress(self.simp_solver.resultdata.stress)
        self.simp_solver.resultdata.vtkdatasource_stress.data = self.simp_solver.resultdata.unstrgrid_stress
        self.simp_solver.resultdata.vtkdatasource_stress.update()


    #初始化场景
    def _mayavi(self):
        """Shows how you can generate data using mayavi instead of mlab."""
        print('updating mayavi')

        e = self.scene.engine

        #网格scene配置
        e.current_scene = self.scene.mayavi_scene
        e.add_source(self.simp_solver.resultdata.vtkdatasource_mesh)
        e.add_module(Surface(name = 'mesh_wireframe'))
        e.current_scene.children[0].children[0].children[0].actor.property.representation = 'wireframe'
        e.current_scene.children[0].children[0].children[0].actor.property.color = (0,0,0)
        e.current_scene.children[0].children[0].children[0].actor.property.line_width = 1.0
        e.add_module(Surface(name='mesh_solid'))

        #位移scene配置
        e.current_scene = self.scene0.mayavi_scene
        e.add_source(self.simp_solver.resultdata.vtkdatasource_displacement)
        e.add_module(Surface(name = 'displacement'))
        self.scene.engine.current_scene.children[0].children[0].children[0].enable_contours = True
        self.scene.engine.current_scene.children[0].children[0].children[0].contour.filled_contours = True
        self.scene.engine.current_scene.children[0].children[0].children[0].module_manager.scalar_lut_manager.show_legend = True

        #应力scene配置
        e.current_scene = self.scene1.mayavi_scene
        e.add_source(self.simp_solver.resultdata.vtkdatasource_stress)
        e.add_module(Surface(name = 'stress'))
        self.scene.engine.current_scene.children[0].children[0].children[0].enable_contours = True
        self.scene.engine.current_scene.children[0].children[0].children[0].contour.filled_contours = True
        self.scene.engine.current_scene.children[0].children[0].children[0].module_manager.scalar_lut_manager.show_legend = True

        #应变scene配置
        e.current_scene = self.scene2.mayavi_scene
        e.add_source(self.simp_solver.resultdata.vtkdatasource_strain)
        e.add_module(Surface(name = 'strain'))
        self.scene.engine.current_scene.children[0].children[0].children[0].enable_contours = True
        self.scene.engine.current_scene.children[0].children[0].children[0].contour.filled_contours = True
        self.scene.engine.current_scene.children[0].children[0].children[0].module_manager.scalar_lut_manager.show_legend = True

        #密度scene配置
        e.current_scene = self.scene3.mayavi_scene
        e.add_source(self.simp_solver.resultdata.vtkdatasource_density)
        e.add_module(Surface(name = 'density'))
        self.scene.engine.current_scene.children[0].children[0].children[0].module_manager.scalar_lut_manager.show_legend = True
     
       
    def _update_vtkdatasource(self,old,new):
        self.simp_solver.loop

        filter = 0
        print('updating vtkdatasource')
        if 0< self.simp_solver.loop < 10:
            filter = 0.85
        if self.simp_solver.loop >= 10:
            filter = 1/np.e**(self.i) + 0.5
            self.i = self.i+1
        self.simp_solver.resultdata.vtkdatasource_displacement.data = self.simp_solver.resultdata.unstrgrid_displacement
        self.simp_solver.resultdata.vtkdatasource_displacement.update()

        self.simp_solver.resultdata.vtkdatasource_stress.data = self.simp_solver.resultdata.unstrgrid_stress
        self.simp_solver.resultdata.vtkdatasource_stress.update()

        self.simp_solver.resultdata.vtkdatasource_strain.data = self.simp_solver.resultdata.unstrgrid_strain
        self.simp_solver.resultdata.vtkdatasource_strain.update()
        print(filter)
        self.simp_solver.resultdata.unstrgrid_density = self.simp_solver.resultdata.generate_unstrgrid_mesh(filter=filter)
        self.simp_solver.resultdata.update_unstrgrid_density(self.simp_solver.resultdata.density)
        self.simp_solver.resultdata.vtkdatasource_density.data = self.simp_solver.resultdata.unstrgrid_density
        self.simp_solver.resultdata.vtkdatasource_density.update()

        print('updating done')

    #动态监听currentselection
    def _selection_change(self, old, new):
         self.trait_property_changed('current_selection', old, new)

    def _get_current_selection(self):
         return self.scene.engine.current_selection

    def _plot_convergence_curve(self):

        plt.close()  # clf() # 清图  cla() # 清坐标轴 close() # 关窗口

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.axis("auto")
        # ax.xaxis()# 设置图像显示的时候XY轴比例
        plt.grid(True)  # 添加网格
        plt.ion()  # interactive mode on
        try:
            while 1:
                ax.plot(self.simp_solver.strain_energy,c='b')
                ax.set_xlabel('steps')
                ylabel = 'Strain_energy/Iteration: '+str(self.simp_solver.loop)
                ax.set_ylabel(ylabel)
                ax.set_title('convergence curve of strain energy')
                plt.pause(1)
                if self.simp_solver.finished:
                    break
            ax.plot(self.simp_solver.strain_energy,c = 'b')
            plt.savefig('Convergence_curve.png')
            plt.pause(36000)

        except Exception as err:
            print(err)
        # plt.plot(self.simp_solver.strain_energy)H:\GitHub\Topology-optimization-of-structure-via-simp-method\Python
        # ylabel = 'strain_energy/iteration: '+str(self.simp_solver.loop)
        # plt.ylabel(ylabel)
        # plt.xlabel('steps')
        # plt.title('convergence curve of strain energy')
        # plt.show()



    def _plot(self):
        pass
    def _animate(self):

        self.scene.engine.current_scene = self.scene4.mayavi_scene
        src = mlab.pipeline.open((self.address+'\density\density_00.vtu'))
        src.play = False
        src.add_module(Surface(name='animate_density'))
        # self.scene.engine.current_scene.children[0].children[0].children[0].enable_contours=True
        # self.scene.engine.current_scene.children[0].children[0].children[0].contour.filled_contours=True
        self.scene.engine.current_scene.children[0].children[0].children[0].module_manager.scalar_lut_manager.show_legend=True


if __name__ == '__main__':
    #for cantilever_benchmark     e = 1,         nu = 0.3
    #for complex2D_benchmark      e = 2.1*50000 ,nu = 0.3
    #for complex3D_benchmark_hex  e = 2.1E11,    nu = 0.15
    #for complex3D_benchmark      e = 2.1E11,    nu = 0.15
    #for cantilever the ex = 2.1,   for complex2D the EX = 2.1*50000, for complex3D the ex = 2.1e11

    m = ShorthairCat(type='top2d',e =1, nu=0.3, r = 1.2, penal = 3, move = 0.2,volfac = 0.4)
    m.configure_traits()
    try:
        vtu2stl()
    except:
        print('an error occured,please check your vtu file named as :top3d ')




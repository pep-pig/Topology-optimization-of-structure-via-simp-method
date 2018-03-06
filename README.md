# Topology-optimizer

This project contains topology optimization of structure with SIMP ,the codes are written by Python and used the FEA solver api provided by ANSYS.<br>

## python environment configuration
This app is developed in python 3.6 and require packages as follows :
* trait 4.6.0
* traitsui 5.1.0
* mayavi 4.5.0
* vtk 8.1.0
* PyQt 4.11 (this is very important ,if you use PyQt 4.12 ,the app will not work)

## vertion info
All vertion information are discribed as follows:

### vertion 1.0.0
* This is a basic optimization frame.<br>
* The benchmark is a 2D rectangular cantilever , contains two modules: optimization and finite element analysis.The next release will contain data visualization of stress, strain,and displacement.<br>

### vertion 1.1.0
This version contains postprocessor to visualize the optimization results．<br>
Mainly include:<br>
* Show the stress, strain, and displacement timely.<br>
* Show the convergence curve timely.<br>
* Animate the results and make movie.<br> 
The SDK is Mayavi+traits+traitsUI+tvtk.<br>
  
### vertion 1.2.0
This version is versatile,it can optimize 2D and 3D structure no matter using what kind of grid to mesh the geometry.<br>
And,this vertion is more much more efficient as I replaced the for loop by vectorizing.

### vertion 1.3.0
this version used a new algorithm to restrain checkerboard and mesh independence, And no longer computing strain energy in every iteration step ,instead we getting strain energy from ANSYS directly.This improvement can enhance the robust and efficiency of the optimizer.<br>

## GUI exhibition
The app named as shorthaircat.<br>
Shorthaircat could show convergency curve and displacement, stress ,strain ,density in time.<br>
we choose some GUI figures exhibited here:
<p align="center">
<img src="REASULTS/GUI.png" width="192"/>
<img src="REASULTS/GUI_stress.png" width="192"/>
<img src="REASULTS/converge.png" width="192"/>
</p>

## Algorithm，hyperparameters 

* Algorithm <br>
The algorithm is simp method , and the filter is the same with 'top99 lines matlab codes'. The iteration method is OC.<br>
Algorithm we used need some finite analysis data which we all extract from ANSYS <br>
Including: displacement,stress ,strain ,element strain energy , element volume ,element center coordinates ,element's nodes number , each element's adjacent elements which used in filter.<br>

* Hyperparameter <br>
There are two kind of hyperparameter in the algorithm:<br>
material properties: Young's module and Poisson rate<br>
If the total strain energy is too small ,you can increase Young's module so the algorithm will much more robust
simp methond's hyperparameter : Rmin and move<br>
Rmin is a pretty important hyperparameter which can determine your final results. As mentioned in sigmund's PHD thesis , Rmin is approximately the same as the minimun dimention in the toplogy<br>

## Benchmarks gallary
we choose some benchmarks tested on our program and exihibit the results:<br>
* cantilever 2D:
<p align="center">
<img src="REASULTS/cantilever2D.gif" width="512"/>
</p>

* 3D cantilever with center load
<p align="center">
<img src="REASULTS/center_load.gif" width="512"/>

<img src="REASULTS/center_load_density.png" width="512"/>
<img src="REASULTS/center_load_stl.png" width="512"/>
</p>

* L_shape problem
<p align="center">
<img src="REASULTS/L_shape.gif" width="512"/>

<img src="REASULTS/L_shape_density.png" width="512"/>
<img src="REASULTS/L_shape_stl.png" width="512"/>
</p>

* MBB
<p align="center">
<img src="REASULTS/MBB.gif" width="512"/>
<img src="REASULTS/MBB_stl.png" width="512"/>
</p>

* complex2D
<p align="center">
<img src="REASULTS/complex2D.gif" width="512"/>
<img src="REASULTS/complex2D_stress.png" width="512"/>
</p>




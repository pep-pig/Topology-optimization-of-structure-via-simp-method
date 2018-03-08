# Topology-optimizer

This project contains topology optimization of structure with SIMP ,the codes are written by Python and used the FEA solver api provided by ANSYS.<br>

## python environment configuration
This app is developed in python 3.6 and require packages as follows :
* trait 4.6.0
* traitsui 5.1.0
* mayavi 4.5.0
* vtk 8.1.0
* PyQt 4.11 (this is very important ,if you use PyQt 4.12 ,the app will not work)

## version info
All version information are discribed as follows:

### version 1.0.0
* This is a basic optimization frame.<br>
* The benchmark is a 2D rectangular cantilever , contains two modules: optimization and finite element analysis.The next release will contain data visualization of stress, strain,and displacement.<br>

### version 1.1.0
This version contains postprocessor to visualize the optimization results．<br>
Mainly include:<br>
* Show the stress, strain, and displacement timely.<br>
* Show the convergence curve timely.<br>
* Animate the results and make movie.<br> 
The SDK is Mayavi+traits+traitsUI+tvtk.<br>
  
### version 1.2.0
This version is versatile,it can optimize 2D and 3D structure no matter using what kind of grid to mesh the geometry.<br>
And,this vertion is more much more efficient as I replaced the for loop by vectorizing.

### version 1.3.0
this version used a new algorithm to restrain checkerboard and mesh independence, And no longer computing strain energy in every iteration step ,instead we getting strain energy from ANSYS directly.This improvement can enhance the robust and efficiency of the optimizer.<br>

### version 1.4.0
* For robust ,use the same filter as mentioned in "top99"
* save pictures and make movie by ffmpeg
* transfer topology results formated by vtu to stl format which can be used to 3D printing

## GUI exhibition
The app named as shorthaircat.<br>
Shorthaircat could show convergency curve and displacement, stress ,strain ,density in time.<br>
we choose some GUI figures exhibited here:
<p align="center">
<img src="REASULTS/GUI.png" width="802">
<img src="REASULTS/GUI_stress.png" width="802">
</p>
<p align="center">
<img src="REASULTS/converge.png" width="520" />
</p>



## Algorithm，hyperparameters 

* Algorithm <br>
The algorithm is simp method , and the filter is the same with 'top99 lines matlab codes'. The iteration method is OC.<br>
Algorithm we used need some finite analysis data which we all extract from ANSYS <br>
*Including*:
displacement,stress ,strain ,element strain energy , element volume ,element center coordinates ,element's nodes number , each element's adjacent elements which used in filter.<br>

*Objective function*:
<p align="center">
<img src="REASULTS/objective_function.png" width="400"/>
</p>

*Updating scheme*:
<p align="center">
<img src="REASULTS/updating_scheme.png" width="400"/>
</p>
Where Be and sensitivity are calculated by the fomulas below:
<p align="center">
<img src="REASULTS/Be.png" width="200"/>
<img src="REASULTS/sensitivity.png" width="460"/>  
</p>

*Filter(used to eliminate checkerboard and mesh-independent)*
<p align="center">
<img src="REASULTS/filter.png" width="400"/>
</p>
where the weight factor Hf is calculated as follows:
<p align="center">
<img src="REASULTS/weight_factor.png" width="400"/>
</p>

* Hyperparameter <br>
There are two kind of hyperparameter in the algorithm:<br>
material properties: Young's module and Poisson rate<br>
If the total strain energy is too small ,you can increase Young's module so the algorithm will much more robust
simp methond's hyperparameter : Rmin and move<br>
* `--Rmin`:a pretty important hyperparameter which can determine your final results. As mentioned in sigmund's PHD thesis , Rmin is approximately the same as the minimun dimention in the toplogy<br>
* `--move`:If your convergence curve vibrates you could decrease the value of move  

## gallery and benchmarks
we choose some benchmarks tested on our program and exihibit the results:<br>
* cantilever 2D:
<p align="center">
<img src="REASULTS/cantilever2D.gif" width="360"/>
</p>

* 3D cantilever with center load
<p align="center">
<img src="REASULTS/center_load.gif" width="360"/>
</p>
<p align="center">
<img src="REASULTS/center_load_density.png" width="360" height ="300"/>
<img src="REASULTS/center_load_stl.png" width="360"  height ="300"/>
</p>

* L_shape problem
<p align="center">
<img src="REASULTS/L_shape.gif" width="360"/>
</p>
<p align="center">
<img src="REASULTS/L_shape_density.png" width="360"  height ="300"/>
<img src="REASULTS/L_shape_stl.png" width="360"  height ="300" />
</p>

* MBB
<p align="center">
<img src="REASULTS/MBB.gif" width="360"/>
<img src="REASULTS/MBB_stl.png" width="360"/>
</p>

* complex2D
<p align="center">
<img src="REASULTS/complex2D.gif" width="360"/>
<img src="REASULTS/complex2D_stress.png" width="360"/>
</p>

* complex3D
<p align="center">
<img src="REASULTS/complex3D.gif" width="360"/>
</p>



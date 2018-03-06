# Topology-optimizer
　　This project contains topology optimization of structure with SIMP and multiscale opitimization of both structure and materials with AH ,the programming language is Python and the FEA solver is ANSYS MAPDL.<br>

## vertion 1.0.0
　　This is a basic optimization frame.<br>
　　The benchmark is a 2D rectangular cantilever , contains two modules: optimization and finite element analysis.The next release will contain data visualization of stress, strain,and displacement.<br>

## vertion 1.1.0
　　This version contains postprocessor to visualize the optimization results．<br>
Mainly include:<br>
　　1.Show the stress, strain, and displacement timely.<br>
　　2.Show the convergence curve timely.<br>
　　3.Animate the results and make movie.<br> 
　　The SDK is Mayavi+traits+traitsUI+tvtk.<br>
  
## vertion 1.2.0
　　This version is versatile,it can optimize 2D and 3D structure no matter using what kind of grid to mesh the geometry.<br>
　　And,this vertion is more much more efficient as I replaced the for loop by vectorizing.

## vertion 1.3.0
　　this version used a new algorithm to restrain checkerboard and mesh independence, And no longer computing strain energy in every iteration step ,instead we getting strain energy from ANSYS directly.This improvement can enhance the robust and efficiency of the optimizer.<br>



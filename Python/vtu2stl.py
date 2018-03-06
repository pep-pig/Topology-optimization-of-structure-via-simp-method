#!/usr/bin/env python

"""Convert UnstructuredGrid in .vtk files to STL files."""
from tvtk.api import tvtk


def vtu2stl():
    reader = tvtk.XMLUnstructuredGridReader()
    reader.file_name="top3d.vtu"


    surface_filter = tvtk.DataSetSurfaceFilter()
    surface_filter.set_input_connection(reader.output_port)

    triangle_filter = tvtk.TriangleFilter()
    triangle_filter.set_input_connection(surface_filter.output_port)

    writer = tvtk.STLWriter()
    writer.file_name='top3d.stl'
    writer.set_input_connection(triangle_filter.output_port)
    writer.write()

# import sys
# import vtk

# reader = vtk.vtkUnstructuredGridReader()
# reader.SetFileName('L_shape.vtu')
#
# surface_filter = vtk.vtkDataSetSurfaceFilter()
# surface_filter.SetInputConnection(reader.GetOutputPort())
#
# triangle_filter = vtk.vtkTriangleFilter()
# triangle_filter.SetInputConnection(surface_filter.GetOutputPort())
#
# writer = vtk.vtkSTLWriter()
# writer.SetFileName('L_shape.stl')
# writer.SetInputConnection(triangle_filter.GetOutputPort())
# writer.Write()
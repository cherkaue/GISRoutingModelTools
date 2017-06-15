# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# ComputeManningN.py
# Created on: 2016-10-14 15:06:09.00000
#   (generated by ArcGIS/ModelBuilder)
# Usage: ComputeManningN <ShreveStreamOrder> <LandUseMap> <LandUseRemapTable> <ManningGrid> <maxStreamOrder> <minStreamOrder> <maxManningN> <minManningN> 
# Description: 
# Computes values of Manning's N along the stream channel and across the 
# hillslopes.  Channel values are scaled based on the Shreve Stream Order 
# number between the provided minimum and maximum Manning's N values.  
# Hillslope values are based on the land use class, with values stored in the 
# table landuse_remap.dbf.  Land use map must be the same resolution as the
# DEM used for routing model setup, and must be reclasssified to the classes
# required for the routing model before this step can be completed.  The "VIC
# Land Use Tools" can be used to help with this process.
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy

# Script arguments
ShreveStreamOrder = arcpy.GetParameterAsText(0)
if ShreveStreamOrder == '#' or not ShreveStreamOrder:
    ShreveStreamOrder = "ShreveOrder" # provide a default value if unspecified

LandUseMap = arcpy.GetParameterAsText(1)
if LandUseMap == '#' or not LandUseMap:
    LandUseMap = "landuse" # provide a default value if unspecified

ManningRemapTable = arcpy.GetParameterAsText(2)
if ManningRemapTable == '#' or not ManningRemapTable:
    ManningRemapTable = "Y:\\apps\\ArcGIS_toolboxes\\LandUseTools.gdb\\IGBP2GISrouting" # provide a default value if unspecified

#maxStreamOrder = arcpy.GetParameterAsText(3)
#if maxStreamOrder == '#' or not maxStreamOrder:
#    maxStreamOrder = "50" # provide a default value if unspecified
#maxStreamOrder = float(maxStreamOrder)

#minStreamOrder = arcpy.GetParameterAsText(4)
#if minStreamOrder == '#' or not minStreamOrder:
#    minStreamOrder = "1" # provide a default value if unspecified
#minStreamOrder = float(minStreamOrder)

maxManningN = arcpy.GetParameterAsText(3)
if maxManningN == '#' or not maxManningN:
    maxManningN = "0.075" # provide a default value if unspecified
maxManningN = float(maxManningN)

minManningN = arcpy.GetParameterAsText(4)
if minManningN == '#' or not minManningN:
    minManningN = "0.035" # provide a default value if unspecified
minManningN = float(minManningN)

RoutingLayers = arcpy.GetParameterAsText(5)
if RoutingLayers == '#' or not RoutingLayers:
    RoutingLayers = "RoutingLayers" # provide a default value if unspecified

# Build file names and local variables
TempGrid1 = "tmpGrid1"
TempGrid1Path = "%s\\%s" % ( RoutingLayers, TempGrid1 )
TempSurfaceN = "tmpSurfaceN"
TempSurfaceNPath = "%s\\%s" % ( RoutingLayers, TempSurfaceN )
TempChannelN = "tmpChannelN"
TempChannelNPath = "%s\\%s" % ( RoutingLayers, TempChannelN )
ManningN = "manningN"
ManningNLayer = "%s_lyr" % ManningN
ManningNPath = "%s\\%s" % ( RoutingLayers, ManningN )
arcpy.AddMessage("Calculating land and stream slopes creating raster %s" % ( ManningNPath))

# check for existing file
if arcpy.Exists(TempGrid1Path):
    arcpy.Delete_management(TempGrid1Path)
if arcpy.Exists(TempSurfaceNPath):
    arcpy.Delete_management(TempSurfaceNPath)
if arcpy.Exists(TempChannelNPath):
    arcpy.Delete_management(TempChannelNPath)
if arcpy.Exists(ManningNPath):
    arcpy.Delete_management(ManningNPath)
if arcpy.Exists(ManningNLayer):
    arcpy.Delete_management(ManningNLayer)

# set environment variables
arcpy.env.workspace = RoutingLayers
arcpy.env.extent = ShreveStreamOrder
arcpy.env.cellsize = ShreveStreamOrder

# Process: Reclass Land Use Map Using Surface Manning's N Values
arcpy.ReclassByTable_3d(LandUseMap, ManningRemapTable, "CATEGORY", "CATEGORY", "MANNING", TempGrid1Path, "NODATA")

# Process: Compute Manning N for hillslopes
ptrTempSurfaceN = arcpy.sa.Raster( TempGrid1Path ) / 100.
ptrTempSurfaceN.save( TempSurfaceNPath )
#arcpy.BuildRasterAttributeTable_management(TempSurfaceNPath)

# Process: Compute Manning N for Channels using highest Mannings N for lowest order stream
statResult = arcpy.GetRasterProperties_management( ShreveStreamOrder, "MAXIMUM" )
arcpy.AddMessage( statResult )
maxStreamOrder = float( statResult.getOutput(0) )
minStreamOrder = 1.
ptrTempChannelN = ( ( arcpy.sa.Raster(ShreveStreamOrder) - minStreamOrder ) / (maxStreamOrder - minStreamOrder) * (minManningN - maxManningN) + maxManningN )
ptrTempChannelN.save( TempChannelNPath )
#arcpy.BuildRasterAttributeTable_management(TempChannelNPath)

# Process: Combine Hillslope and Channel Manning N
ptrManningN = arcpy.sa.Con(arcpy.sa.IsNull(ShreveStreamOrder), TempSurfaceN, TempChannelN )
ptrManningN.save( ManningNPath )
#arcpy.BuildRasterAttributeTable_management(ManningNPath)

# Add layer to the display
mxd = arcpy.mapping.MapDocument("CURRENT")
dataFrame = arcpy.mapping.ListDataFrames(mxd, "*")[0]
result = arcpy.MakeRasterLayer_management(ManningNPath, ManningNLayer)
addLayer = result.getOutput(0)
arcpy.mapping.AddLayer(dataFrame,addLayer)

# remove temporary file when done
if arcpy.Exists(TempGrid1Path):
    arcpy.Delete_management(TempGrid1Path)
if arcpy.Exists(TempSurfaceNPath):
    arcpy.Delete_management(TempSurfaceNPath)
if arcpy.Exists(TempChannelNPath):
    arcpy.Delete_management(TempChannelNPath)

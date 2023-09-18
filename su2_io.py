import vtk
from su2_json import *
from datetime import date

from pathlib import Path
BASE = Path(__file__).parent

# remove empty lists from dictlist object
def remove_empty_lists(d):
  final_dict = {}
  for a, b in d.items():
     if b:
       if isinstance(b, dict):
         final_dict[a] = remove_empty_lists(b)
       elif isinstance(b, list):
         final_dict[a] = list(filter(None, [remove_empty_lists(i) for i in b]))
       else:
         final_dict[a] = b
  return final_dict

########################################################################################
# create the json entries for the boundaries using BCDictList
########################################################################################
def createjsonMarkers():
  print("creating json entry for inlet")
  marker_inlet=[]
  marker_isothermal=[]
  marker_heatflux=[]
  marker_heattransfer=[]
  marker_symmetry=[]
  marker_farfield=[]
  marker_outlet=[]
  # PRESSURE_OUTLET or MASS_FLOW_OUTLET
  marker_inc_outlet_type=[]
  # PRESSURE_INLET or VELOCITY_INLET
  marker_inc_inlet_type=[]

  # loop over the boundaries and construct the markers
  for bcdict in state.BCDictList:
    print("bcdict = ",bcdict)
    # ##### WALL BOUNDARY CONDITIONS #####
    if bcdict['bc_subtype']=="Temperature":
        marker = [bcdict['bcName'], bcdict['bc_temperature']]
        marker_isothermal.append( marker )
    elif bcdict['bc_subtype']=="Heat flux":
        marker = [bcdict['bcName'], bcdict['bc_heatflux']]
        marker_heatflux.append( [bcdict['bcName'], bcdict['bc_heatflux']] )
    elif bcdict['bc_subtype']=="Heat transfer":
        marker = [bcdict['bcName']]
        marker.extend(bcdict['bc_heattransfer'])
        print("heat transfer marker=",marker)
        marker_heattransfer.append( marker )
    # ##### OUTLET BOUNDARY CONDITIONS #####
    elif bcdict['bc_subtype']=="Target mass flow rate":
        marker = [bcdict['bcName'], bcdict['bc_massflow']]
        marker_outlet.append( marker )
        marker_inc_outlet_type.append("MASS_FLOW_OUTLET")
    elif bcdict['bc_subtype']=="Pressure outlet":
        marker = [bcdict['bcName'], bcdict['bc_pressure']]
        marker_outlet.append( marker )
        marker_inc_outlet_type.append("MASS_FLOW_OUTLET")
    # ##### INLET BOUNDARY CONDITIONS #####
    elif bcdict['bc_subtype']=="Velocity inlet":
        # note that temperature is always saved.
        marker = [bcdict['bcName'], bcdict['bc_temperature'], bcdict['bc_velocity_magnitude']]
        marker.extend(bcdict['bc_velocity_normal'])
        marker_inlet.append( marker )
        marker_inc_inlet_type.append("VELOCITY_INLET")
    elif bcdict['bc_subtype']=="Pressure inlet":
        marker = [bcdict['bcName'], bcdict['bc_temperature'], bcdict['bc_pressure']]
        marker.extend(bcdict['bc_velocity_normal'])
        marker_inlet.append( marker )
        marker_inc_inlet_type.append("PRESSURE_INLET")
    # ##### SYMMETRY BOUNDARY CONDITIONS #####
    elif bcdict['bc_subtype']=="Symmetry":
        marker = [bcdict['bcName']]
        marker_symmetry.append( marker )
    # ##### FARFIELD BOUNDARY CONDITIONS #####
    elif bcdict['bc_subtype']=="Far-field":
        marker = [bcdict['bcName']]
        marker_farfield.append( marker )

  # ##### WALL #####
  state.jsonData['MARKER_ISOTHERMAL']=marker_isothermal
  state.jsonData['MARKER_HEATFLUX']=marker_heatflux
  state.jsonData['MARKER_HEATTRANSFER']=marker_heattransfer
  # ##### OUTLET #####
  state.jsonData['MARKER_OUTLET']=marker_outlet
  state.jsonData['INC_OUTLET_TYPE']=marker_inc_outlet_type

  state.jsonData['MARKER_SYM']=marker_symmetry
  state.jsonData['MARKER_FAR']=marker_farfield

  state.jsonData['MARKER_INLET']=marker_inlet
  state.jsonData['INC_INLET_TYPE']=marker_inc_inlet_type

  print("marker_isothermal=",state.jsonData['MARKER_ISOTHERMAL'])
  print("marker_heatflux=",state.jsonData['MARKER_HEATFLUX'])
  print("marker_heattransfer=",state.jsonData['MARKER_HEATTRANSFER'])
  print("marker_outlet=",state.jsonData['MARKER_OUTLET'])
  print("marker_inc_outlet_type=",state.jsonData['INC_OUTLET_TYPE'])
  print("marker_symmetry=",state.jsonData['MARKER_SYM'])
  print("marker_far=",state.jsonData['MARKER_FAR'])
  print("marker_inlet=",state.jsonData['MARKER_INLET'])
  print("marker_inc_inlet_type=",state.jsonData['INC_INLET_TYPE'])

  print(state.jsonData)
  # all empty markers will be removed for writing
  myDict = {key:val for key, val in state.jsonData.items() if val != []}
  print(myDict)
  state.jsonData = myDict

########################################################################################
# Export the new json configuration file as .json and as .cfg #
# TODO: why do all the states get checked at startup?
# TODO: when we click the save button, the icon color changes
########################################################################################
def nijso_list_change(filename_json_export,filename_cfg_export):
    print("exporting files")
    print("write config file ",filename_json_export),
    print("write config file ",filename_cfg_export),
    state.counter = state.counter + 1
    print("counter=",state.counter)
    if (state.counter==2):
      print("counter=",state.counter)

    # first, construct the boundaries using BCDictList
    createjsonMarkers()
    #
    ########################################################################################
    # ##### save the json file
    ########################################################################################
    with open(BASE / filename_json_export,'w') as jsonOutputFile:
        json.dump(state.jsonData,jsonOutputFile,sort_keys=True,indent=4,ensure_ascii=False)
    ########################################################################################

    ########################################################################################
    # ##### convert json file to cfg file and save
    ########################################################################################
    with open(BASE / filename_cfg_export,'w') as f:
      f.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
      f.write("%                                                                              %\n")
      f.write("% SU2 configuration file                                                       %\n")
      f.write("% Case description:                                                            %\n")
      f.write("% Author:                                                                      %\n")
      s = "% Date: " \
        + str(date.today()) \
        + "                                                             %\n"
      f.write(s)
      f.write("% SU2 version:                                                                 %\n")
      f.write("%                                                                              %\n")
      f.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
      #for k in state.jsonData:
      for attribute, value in state.jsonData.items():
        print(attribute, value)
        # convert boolean
        if isinstance(value, bool):
            if value==True:
                value="YES"
            else:
                value="NO"
        # we can have lists or lists of lists
        # we can simply flatten the list, remove the quotations,
        # convert square brackets to round brackets and done.
        if isinstance(value, list):

          flat_list = []
          for sublist in value:
            #print(sublist)
            if isinstance(sublist,list):
              #print("sublist=",sublist)
              for num in sublist:
                flat_list.append(num)
                #print("flatlist=",flat_list)
            else:
              flat_list.append(sublist)


          flatlist = ', '.join(str(e) for e in flat_list)
          # put the list between brackets
          value = "(" + flatlist + ")"


        filestring=str(attribute) + "= " + str(value) + "\n"
        f.write(filestring)



########################################################################################
# ##### export internal vtk multiblock mesh to an su2 file
# ##### exports single block .su2 mesh with boundary conditions only
########################################################################################
def export_files(multiblock,su2_export_filename):
    print(type(multiblock))
    print("export files:","clicked")
    # export an su2 file
    # first, get the dimensions. If the z-dimension is smaller than 1e-6, we assume 2D

    # Set some initial values
    #MARKER_TAG = "1"
    #MARKER_ELEMS = 1

    print("saving su2 mesh file")
    #global mb1
    #print(type(mb1))
    #print(dir(mb1))
    #print("nr of blocks inside block = ",mb1.GetNumberOfBlocks())

    internalBlock = multiblock.GetBlock(0)
    if (internalBlock==None):
        print("no internal block, exiting")
        return

    boundaryBlock = multiblock.GetBlock(1)
    #print("nr of blocks inside internal block = ",internalBlock.GetNumberOfBlocks())
    #print("nr of blocks inside block = ",boundaryBlock.GetNumberOfBlocks())

    print(dir(internalBlock))
    # nr of data in internal block
    NELEM = internalBlock.GetNumberOfCells()
    NPOINT = internalBlock.GetNumberOfPoints()
    BOUND=[0,0,0,0,0,0]
    internalBlock.GetBounds(BOUND)
    dz = BOUND[5] - BOUND[2]
    #print("dz=",dz)
    if (dz<1e-12):
        print("case is 2D")
        NDIME= 2
    else:
        print("dz > 0, case is 3D")
        NDIME= 3

    pts = vtk.vtkIdList()
    for i in range(internalBlock.GetNumberOfBlocks()):
        #print("number of internal elements = ", i+1," / ", internalBlock.GetNumberOfBlocks() )
        data = internalBlock.GetBlock(i)
        celldata = data.GetCells()
        #print("data type=",type(data))
        #print("data type=",dir(data))
        #print("celldata type=",type(celldata))
        #print("celldata type=",dir(celldata))

        for i in range(NELEM):
            #print(i," ",celldata.GetCellSize(i))
            celldata.GetCellAtId(i,pts)
            #print("number of ids = ",pts.GetNumberOfIds())
            #print("cell type =",data.GetCellType(i))
            #for j in range(pts.GetNumberOfIds()):
            #    print(pts.GetId(j))


    for i in range(internalBlock.GetNumberOfBlocks()):
        #print("number of internal elements = ", i+1," / ", internalBlock.GetNumberOfBlocks() )
        data = internalBlock.GetBlock(i)
        #for p in range(NPOINT):
        #    print(p," ",data.GetPoint(p))


    with open(su2_export_filename, 'w') as f:
      # write dimensions
      s = "NDIME= " + str(NDIME) + "\n"
      f.write(s)
      # write element connectivity
      s = "NELEM= " + str(NELEM) + "\n"
      f.write(s)

      # write element connectivity
      for i in range(NELEM):
        s = str(data.GetCellType(i)) + " "
        #print(i," ",celldata.GetCellSize(i))
        celldata.GetCellAtId(i,pts)
        #print("number of ids = ",pts.GetNumberOfIds())
        for j in range(pts.GetNumberOfIds()):
            #print(pts.GetId(j))
            s += str(pts.GetId(j)) + " "
        s += str(i) + "\n"
        f.write(s)

      # write point coordinates
      s = "NPOIN= " + str(NPOINT) + "\n"
      f.write(s)
      for i in range(NPOINT):
          p = data.GetPoint(i)
          if (NDIME==3):
            s = str(p[0]) + " " + str(p[1]) + " " + str(p[2]) + " " + str(i) + "\n"
          else:
            s = str(p[0]) + " " + str(p[1]) + " " + str(i) + "\n"
          f.write(s)
      # write markers
      NMARK = boundaryBlock.GetNumberOfBlocks()
      s = "NMARK= " + str(NMARK) + "\n"
      f.write(s)
      for i in range(NMARK):
        #print("i = ",i," / ",NMARK)
        data = boundaryBlock.GetBlock(i)
        celldata = data.GetCells()
        name = boundaryBlock.GetMetaData(i).Get(vtk.vtkCompositeDataSet.NAME())
        s = "MARKER_TAG= " + str(name) + "\n"
        f.write(s)
        #print("metadata block name = ",name)
        #print(type(data))
        NCELLS = data.GetNumberOfCells()
        #print("Npoints = ", data.GetNumberOfPoints())
        s = "MARKER_ELEMS= " + str(NCELLS) + "\n"
        f.write(s)
        for i in range(NCELLS):
            s = str(data.GetCellType(i)) + " "
            celldata.GetCellAtId(i,pts)
            for j in range(pts.GetNumberOfIds()):
              s += str(pts.GetId(j)) + " "
            s += "\n"
            f.write(s)
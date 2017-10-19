# Import arcpy module
import arcpy
import numpy
import math

coords_file = r"Path/to/csv/file"

with open(coords_file) as f:
    lines = f.read().splitlines()
    for l in range(0, len(lines) - 2):
        x1 = float(lines[l].split(',')[0])
        y1 = float(lines[l].split(',')[1])

        x2 = float(lines[l + 1].split(',')[0])
        y2 = float(lines[l + 1].split(',')[1])

        x3 = float(lines[l + 2].split(',')[0])
        y3 = float(lines[l + 2].split(',')[1])

        xCoefficientArray = [x2 - x1, y2 - y1]
        yCoefficientArray = [x3 - x1, y3 - y1]

        coefficientArray = numpy.array([xCoefficientArray,yCoefficientArray])
        constantArray = numpy.array([(pow(x2,2) + pow(y2,2) - pow(x1,2) - pow(y1,2))/2, (pow(x3,2) + pow(y3,2) - pow(x1,2) - pow(y1,2))/2])

        try:
            center = numpy.linalg.solve(coefficientArray, constantArray)

            arcpy.AddMessage(math.sqrt(pow(x1-center[0],2) + pow(y1-center[1],2)))
            arcpy.AddMessage(math.sqrt(pow(x2-center[0],2) + pow(y2-center[1],2)))
            arcpy.AddMessage(math.sqrt(pow(x3-center[0],2) + pow(y3-center[1],2)))
            arcpy.AddMessage("------------------------------------------------")
        except:
            arcpy.AddMessage("It's a straight line")
            arcpy.AddMessage("------------------------------------------------")

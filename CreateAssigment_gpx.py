#-------------------------------------------------------------------------------
# Name:        CreateAssignments_gpx.py
# Purpose:     Create Task Assignment Forms from selected rows in the
#              Assignments data layer.  New TAFs are stored by Task ID in the
#              Assignments folder
#
# Author:      Don Ferguson
#
# Created:     01/25/2012
# Copyright:   (c) Don Ferguson 2012
# Licence:
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  The GNU General Public License can be found at
#  <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------

# Take courage my friend help is on the way
import arcpy, time
from arcpy import env

# Set overwrite option
arcpy.env.overwriteOutput = True

output = arcpy.GetParameterAsText(0)
AssignNumber = arcpy.GetParameterAsText(1)

output = output.replace("'\'","/")

#######
#Automate map production - July 27, 2012
mxd=arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd)[0]

fc4 = "Search Segments"
fc5 = "Hasty_Points"
fc6 = "Hasty_Line"
fc7 = "Hasty_Segments"

clearLyrs = [fc4, fc5, fc6, fc7]
lyrvis = [0,0,0,0]
disView = mxd.activeView

kk=0
for clearLyr in clearLyrs:
    lyr = arcpy.mapping.ListLayers(mxd, clearLyr,df)[0]
    arcpy.SelectLayerByAttribute_management(lyr, "CLEAR_SELECTION")
    if lyr.visible == True:
        lyrvis[kk]=1
    else:
        lyrvis[kk]=0
    kk+=1
    lyr.visible = False

del kk

###############
fc1="Incident_Info"
rows = arcpy.SearchCursor(fc1)
row = rows.next()
arcpy.AddMessage("Get Incident Info")

try:
    while row:
        # you need to insert correct field names in your getvalue function
        Incident_Name = row.getValue("Incident_Name")
        MapDatum = row.getValue("MapDatum")
        MagDec = row.getValue("MagDec")
        MapCoord = row.getValue("MapCoord")
        Base_Phone = row.getValue("Base_PhoneNumber")
        Base_Freq = row.getValue("Comms_Freq")
        row = rows.next()
    del rows
    del row
except:
    Incident_Name = "Incident_Name"
    MapDatum = "MapDatum"
    MagDec = "MagDec"
    MapCoord = "MapCoord"
    Base_Phone = "Base_PhoneNumber"
    Base_Freq = "Comms_Freq"


arcpy.AddMessage("  ")
fc2="Assignments"
fc3 = "Operation_Period"
fc8 = "Teams"
fc9 = "Team_Members"

field1 = "Assignment_Number"
whereField = '"Assignment_Number" = '
fname = True

rows0 = arcpy.SearchCursor(fc2, "","","Assignment_Number")
row0 = rows0.next
for row0 in rows0:
    if not row0.Assignment_Number:
        field1 = "Planning_Number"
        whereField = '"Planning_Number" = '
        fname = False
del rows0, row0

AssignNum = AssignNumber.split(";")

for AssNum in AssignNum:
    where2 = whereField + "'" + AssNum + "'"

    rows = arcpy.SearchCursor(fc2, where2)
    row = rows.next()
    while row:
        # you need to insert correct field names in your getvalue function
        TaskInstruct = row.getValue("Description")
        PlanNo = row.getValue("Planning_Number")
        if not PlanNo:
            PlanNo = " "
        ResourceType = row.getValue("Resource_Type")
        try:
            Priority = row.getValue("Priority")
        except:
            Priority = "High"

        TaskNo = row.getValue("Assignment_Number")
        if not TaskNo:
            TaskNo = " "
        PreSearch = row.getValue("Previous_Search")
        TaskMap = row.getValue("Area_Name")
        if fname == True:
            arcpy.AddMessage("Task Assignment Number " + str(TaskNo))
        else:
            arcpy.AddMessage("Planning Number " + str(PlanNo))

        mapScale = row.getValue("Map_Scale")
        if mapScale > 0:
            pScaler = row.getValue("Map_Scale")
            df.scale = int(pScaler)
        else:
            df.scale = 24000

    ################
    ## Added a joint safety note for the TAF that includes Safety note from Op
    ## Period and any specific safety note from Assignment
        Assign_Safety = row.getValue("Safety_note")

        try:
            OpPeriod = row.getValue("Period")
            where3 = '"Period"= %d' % (OpPeriod)
            rows3 = arcpy.SearchCursor(fc3, where3)
            row3 = rows3.next()
            while row3:
                Op_Safety = row3.getValue("Safety_Message")
                row3 = rows3.next()
            del row3
            del rows3
        except:
            OpPeriod = ""
            Op_Safety = ""

        Notes = "Specific Safety: " + str(Assign_Safety) + "     General Safety: " + \
            str(Op_Safety)
    ################
        PrepBy = row.getValue("Prepared_By")
        del Assign_Safety
        del Op_Safety
        del OpPeriod

        if fname == True:
            filename = output + "/" + str(TaskNo) + ".fdf"
        else:
            filename = output + "/" + str(PlanNo) + ".fdf"
        #

        txt= open (filename, "w")
        txt.write("%FDF-1.2\n")
        txt.write("%????\n")
        txt.write("1 0 obj<</FDF<</F(TAF_Page1_Task.pdf)/Fields 2 0 R>>>>\n")
        txt.write("endobj\n")
        txt.write("2 0 obj[\n")
        txt.write ("\n")
        txt.write("<</T(topmostSubform[0].Page1[0].MissNo[0])/V(" + str(Incident_Name) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].TeamFreq[0])/V(" + str(Base_Freq) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].MagDec[0])/V(" + str(MagDec) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].TaskInstruct[0])/V(" + str(TaskInstruct) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].PlanNo[0])/V(" + str(PlanNo) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].MapDatum[0])/V(" + str(MapDatum) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].MapCoord[0])/V(" + str(MapCoord) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].ResourceType[0])/V(" + str(ResourceType) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].Priority[0])/V(" + str(Priority) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].TaskNo[0])/V(" + str(TaskNo) + ")>>\n")


    ################
    ## Added team names
        TeamID = row.getValue("Team")
        if TeamID:
            txt.write("<</T(topmostSubform[0].Page1[0].TeamId[0])/V(" + str(TeamID) + ")>>\n")

            where8 = '"Team_Name" = ' + "'" + TeamID + "'"
            rows3 = arcpy.SearchCursor(fc8, where8)
            row3 = rows3.next()
            while row3:
                TeamLead = row3.getValue("Leader")
                Medic = row3.getValue("Medic")
                row3 = rows3.next()
            del row3
            del rows3

            txt.write("<</T(topmostSubform[0].Page1[0].TeamLead[0])/V(" + str(TeamLead) + ")>>\n")
            txt.write("<</T(topmostSubform[0].Page1[0].Medic[0])/V(" + str(Medic) + ")>>\n")

            rows4 = arcpy.SearchCursor(fc9, where8)
            row4 = rows4.next()
            k=1
            while row4:
                if k <=12:
                    Respond = row4.getValue("Name")
                    SARTeam =row4.getValue("Originating_Team")
                    if Respond == TeamLead:
                        txt.write("<</T(topmostSubform[0].Page1[0].TeamLeadAg[0])/V(" + str(SARTeam) + ")>>\n")
                    elif Respond == Medic:
                        txt.write("<</T(topmostSubform[0].Page1[0].MedicAg[0])/V(" + str(SARTeam) + ")>>\n")
                    else:
                        txt.write("<</T(topmostSubform[0].Page1[0].Respond" + str(k) + "[0])/V(" + str(Respond) + ")>>\n")
                        txt.write("<</T(topmostSubform[0].Page1[0].Respond" + str(k) + "Ag[0])/V(" + str(SARTeam) + ")>>\n")
                        k+=1
                    del Respond
                    del SARTeam
                else:
                    arcpy.AddWarning("No more than 14 on a team")
                row4 = rows4.next()
            del row4
            del rows4
            del TeamID
            del TeamLead
            del Medic
            del k


        txt.write("<</T(topmostSubform[0].Page1[0].TaskMap[0])/V(" + str(TaskMap) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].PreSearch[0])/V(" + str(PreSearch) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].Phone_Base[0])/V(" + str(Base_Phone) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].Notes[0])/V(" + str(Notes) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].PrepBy[0])/V(" + str(PrepBy) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].Table2[0].Row1[1].TactFreq1[0])/V(" + str(TactFreq1) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].EquipIssued[0])/V(" + str(EquipIssued) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].Phone_Team[0])/V(" + str(Phone_Team) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].GPSIdOut[0])/V(" + str(GPSIdOut) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].BriefBy[0])/V(" + str(BriefBy) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].DateOut[0])/V(" + str(DateOut) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].TimeOut[0])/V(" + str(TimeOut) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].GPSDatumOut[0])/V(" + str(GPSDatumOut) + ")>>\n")
        txt.write("]\n")
        txt.write("endobj\n")
        txt.write("trailer\n")
        txt.write("<</Root 1 0 R>>\n")
        txt.write("%%EO\n")
        txt.close ()

######
        del TaskInstruct
        del ResourceType
        del Priority

        del PreSearch
        del PrepBy
        del Notes

        fc_lyr = "none"
        fc = "none"
        where4 = '"Area_Name" = ' + "'" + TaskMap + "'"
        try:
            if arcpy.Exists(fc4):
                rows4 = arcpy.UpdateCursor(fc4, where4)
                for row4 in rows4:
                    if fc != "none":
                        arcpy.AddWarning("Another feature has the same name")
                    else:
                        fc = fc4
                        symbologyLayer = arcpy.mapping.ListLayers(mxd,"Search Boundary",df)[0]
                        #row4.Status = "Planned"
                        #pSearch = row4.getValue("Searched")
                        #row4.Searched = pSearch + 1
                        #rows4.updateRow(row4)


            if arcpy.Exists(fc5):
                rows4 = arcpy.SearchCursor(fc5, where4)
                for row4 in rows4:
                    if fc != "none":
                        arcpy.AddWarning("Another feature has the same name")
                    else:
                        fc = fc5
                        symbologyLayer = arcpy.mapping.ListLayers(mxd,"Hasty_Points",df)[0]


            if arcpy.Exists(fc6):
                rows4 = arcpy.SearchCursor(fc6, where4)
                for row4 in rows4:
                    if fc != "none":
                        arcpy.AddWarning("Another feature has the same name")
                    else:
                        fc = fc6
                        symbologyLayer = arcpy.mapping.ListLayers(mxd,"Hasty_Line",df)[0]


            if arcpy.Exists(fc7):
                rows4 = arcpy.SearchCursor(fc7, where4)
                for row4 in rows4:
                    if fc != "none":
                        arcpy.AddWarning("Another feature has the same name")
                    else:
                        fc = fc7
                        symbologyLayer = arcpy.mapping.ListLayers(mxd,"Hasty_Segments",df)[0]


##    ##Automate map production - July 27, 2012
        except:
            arcpy.AddError("failed to get feature layer")
##
        try:
            PrintMap = row.getValue("Create_Map")
            if PrintMap == 'Yes':
                arcpy.AddMessage("Creating task map for Assignment Number: " +str(AssNum))

                if fc == "none":
                    arcpy.AddWarning("No features had this area name and No map created.")
                else:
                    try:
                        reMoveLyr = arcpy.mapping.ListLayers(mxd,"FgTrzG",df)[0]
                        arcpy.mapping.RemoveLayer(df,reMoveLyr)
                        del reMoveLyr
                    except:
                        pass

                    arcpy.RefreshTOC()
                    arcpy.RefreshActiveView()

                    arcpy.MakeFeatureLayer_management (fc, "FgTrzG", where4)
                    mkLyr = arcpy.mapping.Layer("FgTrzG")
                    arcpy.mapping.AddLayer(df,mkLyr,"TOP")
                    updateLayer = arcpy.mapping.ListLayers(mxd,"FgTrzG",df)[0]
                    arcpy.mapping.UpdateLayer(df,updateLayer,symbologyLayer,True)
                    selectLayer = arcpy.mapping.ListLayers(mxd,"FgTrzG",df)[0]
                    arcpy.SelectLayerByAttribute_management (selectLayer, "NEW_SELECTION", where4)

                    mapLyr=arcpy.mapping.ListLayers(mxd, "MGRSZones_World",df)[0]
                    arcpy.SelectLayerByLocation_management(mapLyr,"INTERSECT",selectLayer)
                    UTMZn=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "UTMZone")[0]
                    USNGZn=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "USNGZone")[0]
                    rows7=arcpy.SearchCursor(mapLyr)
                    row7 = rows7.next()
                    UTMZn.text = row7.getValue("GRID1MIL")
                    USNGZn.text = row7.getValue("GRID100K")
                    arcpy.AddMessage("UTM Zone is " + UTMZn.text + " and USNG Grid is " + USNGZn.text + "\n")

                    arcpy.SelectLayerByAttribute_management (mapLyr, "CLEAR_SELECTION")

                    try:
                        del mapLyr
                        del UTMZn
                        del USNGZn
                        del row7
                        del rows7
                    except:
                        pass

                    arcpy.SelectLayerByAttribute_management (selectLayer, "NEW_SELECTION", where4)
                    df.zoomToSelectedFeatures()
                    arcpy.RefreshActiveView()
                    arcpy.SelectLayerByAttribute_management (selectLayer, "CLEAR_SELECTION")

                    mxd.activeView='PAGE_LAYOUT'

                    mapScale = row.getValue("Map_Scale")

                    if mapScale > 0:
                        pScaler = row.getValue("Map_Scale")
                        df.scale = pScaler*1.0
                    else:
                        df.scale = 24000.0

                    del symbologyLayer
                    del mkLyr
                    del updateLayer
                    del mapScale
                    del pScaler

                    try:
                        cIncident=arcpy.GetCount_management("Incident_Information")
                        if int(cIncident.getOutput(0)) > 0:
                            mapLyr = arcpy.mapping.ListLayers(mxd, "Incident_Information")[0]
                            MagDeclin=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "MagDecl")[0]
                            rows8=arcpy.SearchCursor(mapLyr)
                            row8 = rows8.next()
                            MD=row8.getValue("MagDec")
                            if not MD:
                                arcpy.AddWarning("No Magnetic Declination provided in Incident Information")
                            else:
                                MagDeclin.text = row8.getValue("MagDec")
                            del rows8
                            del row8
                            del MagDeclin
                        else:
                            arcpy.AddWarning("No Magnetic Declination provided in Incident Information")
                    except:
                        arcpy.AddMessage("Error: Update Magnetic Declination Manually\n")




                    if TaskMap:
                        MapName=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "MapName")[0]
                        MapName.text = "  " + TaskMap
                    if PlanNo:
                        PlanNum=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "PlanNum")[0]
                        PlanNum.text = "  " + PlanNo
                    if AssNum:
                        TaskNum=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "AssignNum")[0]
                        TaskNum.text = "  " + AssNum

                    if fname == True:
                        outFile = output + "/" + str(TaskNo) + "_map.pdf"
                    else:
                        outFile = output + "/" + str(PlanNo) + "_map.pdf"



##                    if fname == True:
##                        outFile = output + "/" + str(TaskNo) + "_aerial.pdf"
##                    else:
##                        outFile = output + "/" + str(PlanNo) + "_aerial.pdf"




                    try:
                        arcpy.mapping.ExportToPDF(mxd, outFile)
                    except:
                        arcpy.AddWarning("  ")
                        arcpy.AddWarning("Unable to produce map for Assignment: " + str(AssNum))
                        arcpy.AddWarning("Problem with ExportToPDF")
                        arcpy.AddWarning("  ")

                    reMoveLyr = arcpy.mapping.ListLayers(mxd,"FgTrzG",df)[0]
                    arcpy.mapping.RemoveLayer(df,reMoveLyr)


                    arcpy.RefreshTOC()
                    arcpy.RefreshActiveView()

                    del selectLayer
                    del MapName
                    del PlanNum
                    del TaskNum
                    del outFile
                    del reMoveLyr

            else:
                arcpy.AddMessage('No map created')
        except:
            arcpy.AddWarning("Unable to produce map for Assignment: " + str(AssNum))

##########################################

##########################################
## Create gpx file for task
    ##Automate map production - July 27, 2012
        try:
            gpxMap = row.getValue("Create_gpx")
            if gpxMap == 'Yes':
                arcpy.AddMessage("Creating gpx file for Assignment Number: " +str(AssNum))
                where4 = '"Area_Name" = ' + "'" + TaskMap + "'"

                if fc == "none":
                    arcpy.AddWarning("No features had this area name and No gpx created.")
                else:
                    desc = arcpy.Describe(fc)
                    shapeName = desc.shapeFieldName

                    rows6 = arcpy.SearchCursor(fc, where4, \
                        r'GEOGCS["GCS_WGS_1984",' + \
                        'DATUM["D_WGS_1984",' + \
                        'SPHEROID["WGS_1984",6378137,298.257223563]],' + \
                        'PRIMEM["Greenwich",0],' + \
                        'UNIT["Degree",0.017453292519943295]]')

                    if fname == True:
                        filegpx = output + "/" + str(TaskNo) + ".gpx"
                    else:
                        filegpx = output + "/" + str(PlanNo) + ".gpx"

                    txt= open (filegpx, "w")
                    txt.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                    txt.write('<gpx xmlns="http://www.topografix.com/GPX/1/1" version="1.1" creator="MapSAR_Ex" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.topografix.com/GPX/gpx_overlay/0/3 http://www.topografix.com/GPX/gpx_overlay/0/3/gpx_overlay.xsd http://www.topografix.com/GPX/gpx_modified/0/1 http://www.topografix.com/GPX/gpx_modified/0/1/gpx_modified.xsd">\n')

                    shpType = desc.featureClass.shapeType
                    if shpType == "Point":
                        for row6 in rows6:
                            feat = row6.getValue(shapeName)
                            #pnt = row6[0].getPart()
                            pnt = feat.getPart()
                            txt.write('<wpt lat="' + str(pnt.Y) + '" lon= "'+ str(pnt.X) + '">\n')
                            txt.write('<desc>' + str(AssNum) + '</desc>\n')
                            txt.write('<sym>WAYPOINT</sym>\n')
                            txt.write('<extensions>\n')
                            txt.write('<label xmlns="http://www.topografix.com/GPX/gpx_overlay/0/3">\n')
                            txt.write('<label_text>' + str(AssNum) + '</label_text>\n')
                            txt.write('</label>\n')
                            txt.write('</extensions>\n')
                            txt.write('</wpt>\n')
                            del feat
                            del pnt

                    else:
                        txt.write('<trk>\n')
                        k=1
                        for row6 in rows6:
                            txt.write('<name>' + str(AssNum) + '</name>\n')
                            txt.write('<desc>' + str(AssNum) + '</desc>\n')
                            txt.write('<number>' + str(k) + '</number>\n')
                            txt.write('<extensions>\n')
                            txt.write('<label xmlns="http://www.topografix.com/GPX/gpx_overlay/0/3">\n')
                            txt.write('<label_text>' + str(AssNum) + '</label_text>\n')
                            txt.write('</label>\n')
                            txt.write('</extensions>\n')

                            #for part in row6[0].getPart():
                            for part in row6.getValue(shapeName):
                                txt.write('<trkseg>\n')
                                for pnt in part:
                                    txt.write('<trkpt lat="' + str(pnt.Y) + '" lon= "'+ str(pnt.X) + '"/>\n')
                                txt.write('</trkseg>\n')
                                k+=1
                            txt.write('</trk>\n')
                        del k
                        del rows6
                        del row6

                    txt.write('</gpx>')

                    del shpType
                    del filegpx
            else:
                arcpy.AddMessage('No gpx file created')

        except:
            arcpy.AddWarning("Unable to produce gpx for Assignment: " + where4)
##################################


        arcpy.AddMessage(" ")
        row = rows.next()
mxd.activeView = disView
arcpy.RefreshActiveView()

try:
    reMoveLyr = arcpy.mapping.ListLayers(mxd,"FgTrzG",df)[0]
    arcpy.mapping.RemoveLayer(df,reMoveLyr)
    del reMoveLyr
except:
    pass

kk=0
for clearLyr in clearLyrs:
    lyr = arcpy.mapping.ListLayers(mxd, clearLyr,df)[0]
    arcpy.SelectLayerByAttribute_management(lyr, "CLEAR_SELECTION")
    if lyrvis[kk] == 1:
        lyr.visible = 1
    else:
        lyr.visible = 0
    kk+=1

del lyr
del kk
del clearLyr
del rows
del row
# del where2
# del where3
# del where4
del TaskMap
del AssNum
del TaskNo
del PlanNo
del gpxMap
del PrintMap
del fc, fc1, fc2, fc3, fc4,fc5,fc6,fc7,fc8,fc9
del clearLyrs
del lyrvis
del disView

del Incident_Name
del MapDatum
del MagDec
del MapCoord
del Base_Phone
del Base_Freq

#######

del mxd
del df

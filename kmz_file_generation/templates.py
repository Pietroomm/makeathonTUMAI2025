"""
Raw KML / WPML snippets with ${PLACEHOLDER} markers.

The writer substitutes these markers at run-time.  Splitting large XML
strings into thematic blocks makes reuse dead-simple.
"""

COMMON_BLOCK = """
    <wpml:author>${AUTHOR}</wpml:author>
    <wpml:createTime>${CREATE_TIME}</wpml:createTime>
    <wpml:updateTime>${UPDATE_TIME}</wpml:updateTime> 
    <wpml:missionConfig>
      <wpml:flyToWaylineMode>safely</wpml:flyToWaylineMode>
      <wpml:finishAction>goHome</wpml:finishAction>
      <wpml:exitOnRCLost>goContinue</wpml:exitOnRCLost>
      <wpml:executeRCLostAction>goBack</wpml:executeRCLostAction>
      <wpml:takeOffSecurityHeight>10</wpml:takeOffSecurityHeight>
      
      <!-- TAKEOFF_REF_POINT is the GPS lon,lat,ellipsoid height of the launch site -->
      <wpml:takeOffRefPoint>${TAKEOFF_REF_POINT}</wpml:takeOffRefPoint>
      <wpml:takeOffRefPointAGLHeight>0</wpml:takeOffRefPointAGLHeight>
      <wpml:globalTransitionalSpeed>15</wpml:globalTransitionalSpeed>
      <wpml:globalRTHHeight>100</wpml:globalRTHHeight>
      <wpml:droneInfo>
        <wpml:droneEnumValue>100</wpml:droneEnumValue>
        <wpml:droneSubEnumValue>1</wpml:droneSubEnumValue>
      </wpml:droneInfo>
      <wpml:waylineAvoidLimitAreaMode>0</wpml:waylineAvoidLimitAreaMode>
      <wpml:payloadInfo>
        <wpml:payloadEnumValue>99</wpml:payloadEnumValue>
        <wpml:payloadSubEnumValue>2</wpml:payloadSubEnumValue>
        <wpml:payloadPositionIndex>0</wpml:payloadPositionIndex>
      </wpml:payloadInfo>
    </wpml:missionConfig>
"""

# --------------------------------------------------------------------------- #
#  Coordinate system & defaults                                               #
# --------------------------------------------------------------------------- #
COORD_SYS_BLOCK = """
      <wpml:waylineCoordinateSysParam>
        <wpml:coordinateMode>WGS84</wpml:coordinateMode>
        <wpml:heightMode>aboveGroundLevel</wpml:heightMode>
      </wpml:waylineCoordinateSysParam>
      <wpml:autoFlightSpeed>10</wpml:autoFlightSpeed>
      <wpml:globalHeight>10</wpml:globalHeight>
"""

# --------------------------------------------------------------------------- #
#  One waypoint (Placemark) with two actions                                  #
# --------------------------------------------------------------------------- #
WAYPOINT_BLOCK = """
      <Placemark>
        <Point>
          <coordinates>${LONGITUDE},${LATITUDE}</coordinates>
        </Point>

        <wpml:index>${INDEX}</wpml:index>
        <wpml:height>${HEIGHT}</wpml:height>
        <wpml:ellipsoidHeight>${ALTITUDE}</wpml:ellipsoidHeight>

        <wpml:actionGroup>
          <wpml:actionGroupId>${ACTION_GROUP_ID}</wpml:actionGroupId>
          <wpml:actionGroupMode>sequence</wpml:actionGroupMode>

          <!-- ACTION 0 – Rotate aircraft (yaw) -->
          <wpml:action>
            <wpml:actionId>0</wpml:actionId>
            <wpml:actionActuatorFunc>rotateYaw</wpml:actionActuatorFunc>
            <wpml:actionActuatorFuncParam>
              <wpml:aircraftHeading>${HEADING}</wpml:aircraftHeading>
              <wpml:aircraftPathMode>counterClockwise</wpml:aircraftPathMode>
            </wpml:actionActuatorFuncParam>
          </wpml:action>

          <!-- ACTION 1 – Move gimbal (pitch) -->
          <wpml:action>
            <wpml:actionId>1</wpml:actionId>
            <wpml:actionActuatorFunc>gimbalRotate</wpml:actionActuatorFunc>
            <wpml:actionActuatorFuncParam>
              <wpml:gimbalRotateMode>absoluteAngle</wpml:gimbalRotateMode>
              <wpml:gimbalPitchRotateEnable>1</wpml:gimbalPitchRotateEnable>
              <wpml:gimbalPitchRotateAngle>${PITCH}</wpml:gimbalPitchRotateAngle>
            </wpml:actionActuatorFuncParam>
          </wpml:action>
        </wpml:actionGroup>
      </Placemark>
"""

# --------------------------------------------------------------------------- #
#  Full KML skeleton – ${WAYPOINTS} is swapped for many WAYPOINT_BLOCKs        #
# --------------------------------------------------------------------------- #
KML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:wpml="http://www.dji.com/wpmz/1.0.6">
  <Document>
${COMMON_BLOCK}
    <Folder>
      <wpml:templateType>waypoint</wpml:templateType>
      <wpml:templateId>0</wpml:templateId>
${COORD_SYS_BLOCK}
${WAYPOINTS}
      <wpml:payloadParam>
        <wpml:payloadPositionIndex>0</wpml:payloadPositionIndex>
        <wpml:focusMode>firstPoint</wpml:focusMode>
        <wpml:meteringMode>average</wpml:meteringMode>
        <wpml:returnMode>singleReturnFirst</wpml:returnMode>
        <wpml:samplingRate>240000</wpml:samplingRate>
        <wpml:scanningMode>repetitive</wpml:scanningMode>
        <wpml:imageFormat>visable</wpml:imageFormat>
      </wpml:payloadParam>
    </Folder>
  </Document>
</kml>
"""

# --------------------------------------------------------------------------- #
#  WPML template for DJI Pilot 2 (KML)                                        #
# --------------------------------------------------------------------------- #
WPML_MISSION_CONFIG_BLOCK = """
    <wpml:missionConfig>
      <wpml:flyToWaylineMode>safely</wpml:flyToWaylineMode>
      <wpml:finishAction>goHome</wpml:finishAction>
      <wpml:exitOnRCLost>goContinue</wpml:exitOnRCLost>
      <wpml:executeRCLostAction>goBack</wpml:executeRCLostAction>
      <wpml:takeOffSecurityHeight>10</wpml:takeOffSecurityHeight>
      <wpml:globalTransitionalSpeed>15</wpml:globalTransitionalSpeed>
      <wpml:globalRTHHeight>100</wpml:globalRTHHeight>

      <wpml:droneInfo>
        <wpml:droneEnumValue>100</wpml:droneEnumValue>
        <wpml:droneSubEnumValue>1</wpml:droneSubEnumValue>
      </wpml:droneInfo>
      <wpml:waylineAvoidLimitAreaMode>0</wpml:waylineAvoidLimitAreaMode>
      <wpml:payloadInfo>
        <wpml:payloadEnumValue>99</wpml:payloadEnumValue>
        <wpml:payloadSubEnumValue>2</wpml:payloadSubEnumValue>
        <wpml:payloadPositionIndex>0</wpml:payloadPositionIndex>
      </wpml:payloadInfo>
    </wpml:missionConfig>
"""

WPML_WAYPOINT_BLOCK = """
      <Placemark>
        <Point><coordinates>${LONGITUDE},${LATITUDE}</coordinates></Point>

        <wpml:index>${INDEX}</wpml:index>
        <wpml:executeHeight>${ALTITUDE}</wpml:executeHeight>
        <wpml:waypointSpeed>10</wpml:waypointSpeed>

        <wpml:waypointHeadingParam>
          <wpml:waypointHeadingMode>followWayline</wpml:waypointHeadingMode>
          <wpml:waypointHeadingAngle>${HEADING}</wpml:waypointHeadingAngle>
          <wpml:waypointPoiPoint>0,0,0</wpml:waypointPoiPoint>
          <wpml:waypointHeadingAngleEnable>1</wpml:waypointHeadingAngleEnable>
          <wpml:waypointHeadingPathMode>followBadArc</wpml:waypointHeadingPathMode>
          <wpml:waypointHeadingPoiIndex>0</wpml:waypointHeadingPoiIndex>
        </wpml:waypointHeadingParam>

        <wpml:waypointTurnParam>
          <wpml:waypointTurnMode>toPointAndStopWithDiscontinuityCurvature</wpml:waypointTurnMode>
          <wpml:waypointTurnDampingDist>0</wpml:waypointTurnDampingDist>
        </wpml:waypointTurnParam>
        <wpml:useStraightLine>1</wpml:useStraightLine>
      </Placemark>
"""

WPML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:wpml="http://www.dji.com/wpmz/1.0.6">
  <Document>
${MISSION_CONFIG_BLOCK}
    <Folder>
      <wpml:templateId>0</wpml:templateId>
      <wpml:executeHeightMode>WGS84</wpml:executeHeightMode>
      <wpml:waylineId>0</wpml:waylineId>
      <wpml:distance>0</wpml:distance>         <!-- dummy – Pilot recalculates -->
      <wpml:duration>0</wpml:duration>         <!-- dummy – Pilot recalculates -->
      <wpml:autoFlightSpeed>10</wpml:autoFlightSpeed>

${WAYPOINTS}
    </Folder>
  </Document>
</kml>
"""
cmake_minimum_required(VERSION 2.8.3)
project(processing_belt_interpreter)

find_package(catkin REQUIRED COMPONENTS
    message_generation
    geometry_msgs
    tf2
    tf2_ros
    rospy
)

################################################
## Declare ROS messages, services and actions ##
################################################

add_message_files(
    FILES
    Range.msg
    RangeList.msg
    BeltFiltered.msg
)

generate_messages(
    DEPENDENCIES
    geometry_msgs
)

###################################
## catkin specific configuration ##
###################################

catkin_package(
    CATKIN_DEPENDS message_runtime
)
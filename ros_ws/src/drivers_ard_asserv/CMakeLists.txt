cmake_minimum_required(VERSION 2.8.3)
project(drivers_ard_asserv)

## Compile as C++11, supported in ROS Kinetic and newer
# add_compile_options(-std=c++11)

## Find catkin macros and libraries
## if COMPONENTS list like find_package(catkin REQUIRED COMPONENTS xyz)
## is used, also find other catkin packages
find_package(catkin REQUIRED COMPONENTS
    rospy
    std_msgs
    geometry_msgs
    message_generation
    genmsg
    actionlib_msgs
    actionlib
)

## Generate messages
add_message_files(
    FILES
    RobotSpeed.msg
)

## Generate services
add_service_files(
    FILES
    Parameters.srv
    EmergencyStop.srv
    Goto.srv
    Management.srv
    Pwm.srv
    SetPos.srv
    Speed.srv
)

## Generate actions
add_action_files(DIRECTORY action FILES DoGoto.action)

# Generate added messages and services with any dependencies listed here
generate_messages(
    DEPENDENCIES
    std_msgs
    geometry_msgs
    actionlib_msgs
)

catkin_package(
    CATKIN_DEPENDS message_runtime
)

include_directories(
    ${catkin_INCLUDE_DIRS}
)

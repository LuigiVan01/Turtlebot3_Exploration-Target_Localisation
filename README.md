# Autopilot Package

This repository contains the Autopilot package, which is designed to send waypoints to a robot using SLAM Toolbox and Nav2 to explore an unknown map. The project is set up for use with Gazebo and ROS2 Humble, specifically using the Turtlebot3 robot.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributors](#contributors)

## Prerequisites

Before you begin, ensure you have Ubuntu 22.04 or compatible Linux distribution and the following software installed:

- [ROS2 Humble](https://docs.ros.org/en/humble/Installation.html)
- [Gazebo](https://classic.gazebosim.org/tutorials?tut=install_ubuntu&cat=install)
- [Cartographer](https://emanual.robotis.com/docs/en/platform/turtlebot3/quick-start/#pc-setup)  
- [Navigation2](https://emanual.robotis.com/docs/en/platform/turtlebot3/quick-start/#pc-setup)
- [TurtleBot3](https://emanual.robotis.com/docs/en/platform/turtlebot3/quick-start/#pc-setup)
- [Numpy](https://numpy.org/install/)


## Installation

To install this project, follow these steps:

1. If you haven't already, source the ros2 installation, and create a new directory for the workspace as below (NOTE: if you haven't already created a workspace, you will need to install the "Turtlebot Simulations" package later):
   ```
   source /opt/ros/humble/setup.bash
   mkdir -p ~/workspace_name/src
   ```
   
2. Clone the repository into the home directory using the ubuntu terminal (if the terminal prompts you for credentials, sign into github within VS code etc, and use the built in terminal):
   ```
   cd ~
   git clone https://github.com/LuigiVan01/metr4202_2024_team20.git
   ```

3. Copy the "autopilot_package" folder into your "src" folder
   ```
   cp -r ~/metr4202_2024_team20/autopilot_package ~/workspace_name/src

   ```
4. OPTIONAL: If you have not already installed the "Turtlebot Simulations" package, do so now into the "src" folder. Your workspace should now contain the following folders
   ```
   workspace_name
   └── src
       ├── autopilot_package
       ├── DynamixelSDK
       ├── turtlebot3
       ├── turtlebot3_msgs
       └── turtlebot3_simulations
    ```

5. Build the workspace:
   ```
   cd ~/workspace_name/
   colcon build
   ```

7. Source the workspace (and the gazebo setup if you haven't already):
   ```
   source ~/workspace_name/install/setup.bash
   #code below is for sourcing the gazebo setup and is optional if you've already done it
   source /usr/share/gazebo/setup.sh
   ```
8. Set the domain ID and Gazebo model paths (don't forget to change "workspace_name" to your workspace's name):
   ```
   export ROS_DOMAIN_ID=30 #TURTLEBOT3
   export GAZEBO_MODEL_PATH=~/.gazebo/models:$GAZEBO_MODEL_PATH
   export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:~/workspace_name/src/turtlebot3_simulations/turtlebot3_gazebo/models
   export TURTLEBOT3_MODEL=waffle_pi
   ```
9. Add all the source and export commands to your .bashrc so they do not need to be called in future:
    ```
    echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc
    echo 'source ~/workspace_name/install/setup.bash' >> ~/.bashrc
    echo 'export ROS_DOMAIN_ID=30 #TURTLEBOT3' >> ~/.bashrc
    echo 'export GAZEBO_MODEL_PATH=~/.gazebo/models:$GAZEBO_MODEL_PATH' >> ~/.bashrc
    echo 'export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:~/workspace_name/src/turtlebot3_simulations/turtlebot3_gazebo/models' >> ~/.bashrc
    echo 'export TURTLEBOT3_MODEL=waffle_pi' >> ~/.bashrc   
    ```
## Running Autopilot and Detection in Gazebo Simulations
The following commands will assume you followed step 9 in the last section and therefore do not include sourcing of setup files in each new terminal tab.

1. Launch a world file in Gazebo (below we are using one of the custom maps included in the autopilot package):
   ```
   ros2 launch autopilot_package labmap3.launch.py
   ```

2. In a new terminal tab or window, run navigation2 and slam, using the simulation clock:
   ```
   ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True slam:=True
   ```

4. In a new terminal tab or window, run the Autopilot and Aruco Detection nodes:
   ```
   ros2 launch autopilot_package combined.launch.py
   ```

## Running Autopilot and Detection within a Physical Environment
The following steps assume that you are using a computer on which you have followed the installation steps above.

1. ssh into your Turtlebot and enter your credentials when prompted:
   ```
   ssh ubuntu@192.168.0.<ID>
   ```

2. Within your Turtlebot's home directory, clone the repository:
    ```
   cd ~
   git clone https://github.com/LuigiVan01/metr4202_2024_team20.git
   ```

3. As in the installation instructions, create a new workspace and source the humble setup (again this workspace will need to have the "Turtlebot3 Simulations" packages installed in the "src" folder):
   ```
   source /opt/ros/humble/setup.bash
   mkdir -p ~/workspace_name/src
   ```
4. Copy the "autopilot_physical_package" into your workspace "src" directory:
   ```
   cp -r ~/metr4202_2024_team20/autopilot_physical_package ~/workspace_name/src
    ```

5. Build the workspace and source the setup
   ```
   cd ~/workspace_name/
   colcon build
   source ~/workspace_name/install/setup.bash
   ```
   
6. Your workspace on the Turtlebot3 should now look like this:
   ```
   workspace_name
   └── src
       ├── autopilot_physical_package
       ├── DynamixelSDK
       ├── turtlebot3
       ├── turtlebot3_msgs
       └── turtlebot3_simulations
    ```
7. In the Turtlebot3 ssh terminal run the robot launch file:
   ```
   ros2 launch turtlebot3_bringup robot.launch.py
   ```
8. In a new terminal tab or window (non-ssh), set the domain ID and start navigation2 and slam.
   ```
   export ROS_DOMAIN_ID=<ID>
   ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=False slam:=True
   ```
9. In a new terminal tab or window (non-ssh), set the domain ID and run the autopilot package.
   ```
   export ROS_DOMAIN_ID=<ID>
   ros2 launch autopilot_package autopilot.launch.py
   ```
9. In a new ssh terminal tab or window, launch the aruco detection node.
   ```
   ros2 launch autopilot_physical_package aruco_robot.launch.py
   ```
    
     
## Project Structure

```
metr4202_2024_team20/src/autopilot_package
├── autopilot_package
│   ├── aruco_node.py
│   ├── autopilot.py
│   └── __init__.py
├── calibration_file.yaml
├── launch
│   ├── aruco_launch.py
│   ├── autopilot_launch.py
│   ├── combined.launch.py
│   ├── labmap3.launch.py
│   ├── labmap.launch.py
│   ├── labmap_marker.launch.py
│   ├── metr4202_final_demo.launch.py
│   ├── narrows.launch.py
│   ├── navigation2.launch.py
│   ├── project2.launch.py
│   ├── robot_state_publisher.launch.py
│   └── spawn_turtlebot3.launch.py
├── LICENSE
├── models
│   ├── aruco_column_6x6_100mm_0
│   ├── aruco_column_6x6_100mm_2
│   ├── aruco_column_6x6_100mm_42
│   ├── aruco_tag_1
│   ├── aruco_tag_2
│   ├── aruco_tag_3
│   ├── aruco_tag_4
│   ├── turtlebot3_burger
│   ├── turtlebot3_common
│   ├── turtlebot3_dqn_world
│   ├── turtlebot3_house
│   ├── turtlebot3_waffle
│   ├── turtlebot3_waffle_pi
│   └── turtlebot3_world
├── package.xml
├── resource
│   └── autopilot_package
├── setup.cfg
├── setup.py
├── test
│   ├── test_copyright.py
│   ├── test_flake8.py
│   └── test_pep257.py
├── urdf
│   ├── common_properties.urdf
│   ├── turtlebot3_burger.urdf
│   ├── turtlebot3_waffle_pi.urdf
│   └── turtlebot3_waffle.urdf
└── worlds
│   ├── labmap3.world
│   ├── labmap.launch.py
│   ├── labmap_marker.launch.py
│   ├── labmap_marker.world
│   ├── labmap.world
│   ├── metr4202_final_demo.world
│   ├── narrows.world
│   ├── project2.launch.py
│   ├── project2.world
│── README.md
└── ignore│

metr4202_2024_team20/
├──autopilot_package/
│   └── autopilot/
│       └── autopilot.py
│       ├── package.xml
│       └── setup.py   
│── README.md
└── ignore
```

## Contributors
  Team 20:

 - Luigi Vanacore         48543518
 - ZhuoXin Shi            48969761
 - Francis Weber          46992288
 - Ricardo Westerman      45829453
 - Rui Xia                43507917


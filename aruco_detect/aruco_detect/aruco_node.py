import numpy as np
import rclpy
import math
import time
from random import randrange
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from nav2_msgs.msg import BehaviorTreeLog
from geometry_msgs.msg import PoseWithCovarianceStamped
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import PointStamped
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2
from std_msgs.msg import Header

import cv2
from cv_bridge import CvBridge
from sensor_msgs.msg import Image

class Aruco_detect(Node):

    def __init__(self):

        super().__init__('autopilot')
        self.camera_matrix = None
        self.dist_coeffs = None
        self.load_camera_parameters("/home/lv/turtlebot3_ws/src/aruco_detect/calibration_file.yaml")
        
        self.queue_size = 10

        # 初始化cv_bridge
        self.bridge = CvBridge()

        # 初始化aruco字典
        self.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
        self.aruco_params = cv2.aruco.DetectorParameters_create()

         #Initializing current position variable
        self.current_position = PointStamped()
        self.current_position.header.frame_id = 'map'

        #Subscribe to /pose to determine position of Turtlebot
        self.position_subscriber = self.create_subscription(
            PoseWithCovarianceStamped,
            '/pose',
            self.current_position_callback,
            self.queue_size,
            #callback_group=self.parallel_callback_group
        )

        # 订阅图像话题
        self.image_subscriber = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            self.queue_size
        )  

        self.aruco_position_publisher = self.create_publisher(
            PointStamped,
            'aruco_position',
            self.queue_size
        )

    def current_position_callback(self, msg:PoseWithCovarianceStamped):
        #Return current robot pose, unless searching_for_waypoint
        self.current_position.point.x = msg.pose.pose.position.x
        self.current_position.point.y = msg.pose.pose.position.y
        self.current_position.header.frame_id = msg.header.frame_id


    def image_callback(self, msg: Image):

        self.get_logger().info('Received image for ArUco detection')

        try:
            # 将ROS图像消息转换为OpenCV格式
            tag_size_in_meters = 0.1 
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # 调试：显示原始相机图像
            cv2.imshow("Camera Image", cv_image)
            cv2.waitKey(1)  # 用于更新图像显示，0为不延迟，1为1ms延迟显示

            # 转换为灰度图像
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            corners, ids, rejected = cv2.aruco.detectMarkers(gray, self.aruco_dict, parameters=self.aruco_params)

        # 验证 corners 是否检测到了标签
            if corners is not None:
                self.get_logger().info(f"Detected corners: {corners}")
            else:
                self.get_logger().error("No corners detected")
                return  # 如果没有检测到标签，提前退出
            if self.camera_matrix is not None and self.dist_coeffs is not None:
                assert self.camera_matrix.shape == (3, 3), "camera_matrix 格式不正确"
                assert self.dist_coeffs.shape == (1, 5) or self.dist_coeffs.shape == (1, 4), "dist_coeffs 格式不正确"
            else:
                self.get_logger().error("Camera parameters not loaded properly.")
                return

            # 检测Aruco标签


            if ids is not None:
                # 如果检测到Aruco标签，打印标签ID
                self.get_logger().info(f"Detected ArUco marker(s) with ID(s): {ids}")

                # 可视化检测到的标签，显示在图像上
                cv2.aruco.drawDetectedMarkers(cv_image, corners, ids)
                cv2.imshow("Detected ArUco Markers", cv_image)
                cv2.waitKey(1)  # 1ms延迟以更新窗口
                
                if self.camera_matrix is None or self.dist_coeffs is None:
                    self.get_logger().error("Camera parameters not loaded.")
                    return
                
                rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, tag_size_in_meters, self.camera_matrix, self.dist_coeffs)
                if rvecs is None or tvecs is None:
                    self.get_logger().error("Failed to estimate pose for ArUco marker")
                else:
                    for rvec, tvec in zip(rvecs, tvecs):
                        self.get_logger().info(f"Tag ID: {ids}, relative to camera: x={tvec[0][0]}, y={tvec[0][1]}, z={tvec[0][2]}")

                for rvec, tvec in zip(rvecs, tvecs):
                # 计算标签相对于相机的坐标
                    self.get_logger().info(f"Tag ID: {ids}, relative to camera: x={tvec[0][0]}, y={tvec[0][1]}, z={tvec[0][2]}")

                # 获取机器人当前的全局位置 (使用 self.current_position)
                    robot_x = self.current_position.point.x
                    robot_y = self.current_position.point.y
                    robot_yaw = 0  # 假设机器人没有角度变化，或者你可以通过机器人位姿获取 yaw 值

                # 计算全局坐标（相对于机器人位姿）
                    global_x = robot_x + tvec[0][0]
                    global_y = robot_y + tvec[0][1]
                    #global_x = robot_x + (tvec[0][0] * math.cos(robot_yaw) - tvec[0][1] * math.sin(robot_yaw))
                    #global_y = robot_y + (tvec[0][0] * math.sin(robot_yaw) + tvec[0][1] * math.cos(robot_yaw))
                    self.get_logger().info(f"Tag ID: {ids}, Global Position: x={global_x}, y={global_y}")
                    aruco=PointStamped()
                    aruco.header.frame_id = 'map'
                    aruco.point.x = global_x
                    aruco.point.y = global_y
                    self.aruco_position_publisher.publish(aruco)
                    time.sleep(1)

            else:
                # 如果未检测到标签，打印未检测到的消息
                self.get_logger().info("No ArUco markers detected")

        except Exception as e:
            self.get_logger().error(f"Failed to process image: {e}")
            
    def load_camera_parameters(self, file_path):
        self.get_logger().info(f"Loading camera parameters from: {file_path}")

        # 读取相机校准文件
        fs = cv2.FileStorage(file_path, cv2.FILE_STORAGE_READ)
        if not fs.isOpened():
            self.get_logger().error(f"Failed to open camera calibration file: {file_path}")
            return
        self.camera_matrix = fs.getNode("camera_matrix").mat()
        self.dist_coeffs = fs.getNode("distortion_coefficients").mat()
        fs.release()
        
        if self.camera_matrix is not None and self.dist_coeffs is not None:
        # 打印出相机矩阵和畸变系数的信息
            self.get_logger().info(f"camera_matrix shape: {self.camera_matrix.shape}")
            self.get_logger().info(f"camera_matrix: {self.camera_matrix}")
            self.get_logger().info(f"dist_coeffs: {self.dist_coeffs}")
            assert self.camera_matrix.shape == (3, 3), "camera_matrix 格式不正确"
            assert self.dist_coeffs.shape == (1, 5) or self.dist_coeffs.shape == (1, 4), "dist_coeffs 格式不正确"
        if self.camera_matrix is None or self.dist_coeffs is None:
            self.get_logger().error("Failed to load camera parameters")
        else:
            self.get_logger().info(f"Loaded camera matrix: {self.camera_matrix}")
            self.get_logger().info(f"Loaded distortion coefficients: {self.dist_coeffs}")


def main():
    rclpy.init()
    aruco_detect_node = Aruco_detect()
    aruco_detect_node.get_logger().info('Running aruco detection node')
    rclpy.spin(aruco_detect_node)

if __name__=='__main__':
        main()
#!/usr/bin/env python
import rospy
# from geometry_msgs import Pose2D
import serial
import threading
import Queue

__author__ = "Thomas Fuhrmann"
__date__ = 21/10/2017


class Asserv:
    def __init__(self):
        # Internal data members
        self._reception_queue = Queue.Queue()
        # Init ROS stuff
        rospy.init_node('asserv', anonymous=True)
        # self._pub_robot_pose = rospy.Publisher("pose2d", Pose2D)
        # self._sub_arm = rospy.Subscriber("arm", 1, Asserv.callback_arm)
        # self._sub_goto = rospy.Subscriber("goto", 5, Asserv.callback_goto)
        # Init the serial communication
        self._arduino_startep_flag = False
        # TODO dynamic arduino port
        self._serial_com = None
        self._serial_receiver_thread = None
        self.start_serial_com_line("/dev/ttyACM0")
        self.start()

    def start_serial_com_line(self, port):
        try:
            self._serial_com = serial.Serial(port, 57600, timeout=0.5)
            self._serial_receiver_thread = threading.Thread(target=self.data_receiver)
            self._serial_receiver_thread.start()
        except serial.SerialException:
            rospy.logerr("Port : " + port + " is ot available, make sure you have plugged the right arduino.")
            # TODO exit or something like that ?

    def callback_arm(self, data):
        rospy.loginfo("ARM callback")

    def callback_goto(self, data):
        rospy.loginfo("GOTO callback")

    def data_receiver(self):
        while not rospy.is_shutdown():
            try:
                received_data = self._serial_com.readline()
                if received_data != "":
                    # TODO not working well !
                    received_data.replace("\r\n", "")
                    self._reception_queue.put(received_data)
            except KeyboardInterrupt:
                break

    def start(self):
        while not rospy.is_shutdown():
            if not self._reception_queue.empty():
                self.process_received_data(self._reception_queue.get_nowait())
                self._reception_queue.task_done()

    def process_received_data(self, data):
        rospy.loginfo("Process : " + data)
        # At init, start the Arduino
        # TODO adapt the received name !
        if (not self._arduino_startep_flag) and data.find("gr_asserv") == 0:
            rospy.loginfo("Activate the Arduino")
            self.send_serial_data('S', "0")
            self._arduino_startep_flag = True
        #last_finished_id;x;y;angle;speed_pwd_left;speed_pwm_right;linear_speed;wheel_spd_left;wheel_spd_right;sharp;P;I;D;
        elif data.find("~") != -1:
            receied_data_list = data.split(";")
            rospy.loginfo("data sharp : " + receied_data_list[10])
        else:
            # TODO process orders ack reception
            rospy.loginfo("received order ack")

    def send_serial_data(self, order_type, args_list):
        if self._serial_com is not None:
            self._serial_com.write(order_type + '; '.join(args_list))


if __name__ == "__main__":
    Asserv()

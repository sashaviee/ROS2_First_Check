Инструкция по запуску:
# Сборка пакета
cd ~/ros2_ws
colcon build --packages-select exam_robot
source install/setup.bash
# Запуск системы
ros2 launch exam_robot robot_system.launch.py
# Проверка топиков
ros2 topic list
ros2 topic echo /battery_level
ros2 topic hz /battery_level
# Проверка узлов
ros2 node list
ros2 node info /battery_node
# Проверка TF дерева
ros2 run tf2_tools view_frames



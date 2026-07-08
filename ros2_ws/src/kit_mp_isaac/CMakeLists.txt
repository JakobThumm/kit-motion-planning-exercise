cmake_minimum_required(VERSION 3.8)
project(kit_mp_isaac)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY scripts config action_graphs usd
  DESTINATION share/${PROJECT_NAME}
)

ament_package()

cmake_minimum_required(VERSION 3.7)
project (template)


set (CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17 -fstrict-aliasing -Wno-deprecated-declarations -Wno-unused-variable")

file(GLOB GLOB_SRC "*.cpp" "*.h")

add_executable(${PROJECT_NAME} ${GLOB_SRC})




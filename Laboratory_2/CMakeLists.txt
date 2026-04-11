cmake_minimum_required(VERSION 3.10)
project(PATRICIA LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(${PROJECT_NAME}_lib src/patricia.cpp)
target_compile_options(${PROJECT_NAME}_lib PRIVATE -Wall -Wextra -pedantic)

add_executable(${PROJECT_NAME} src/main.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ${PROJECT_NAME}_lib)
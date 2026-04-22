cmake_minimum_required(VERSION 3.10)
project(PATRICIA LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Добавляем флаги компилятора: -g для отладочных символов
# -fsanitize=address,undefined для проверки памяти и UB
set(CMAKE_CXX_FLAGS "-O3 -g -Wall -Wextra -pedantic")

set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS}")

add_library(${PROJECT_NAME}_lib src/patricia.cpp)

add_executable(${PROJECT_NAME} src/main.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ${PROJECT_NAME}_lib)
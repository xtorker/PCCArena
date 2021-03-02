cmake_minimum_required(VERSION 2.8 FATAL_ERROR)

set(PROJECT_OUTPUT_FOLDER "${CMAKE_CURRENT_SOURCE_DIR}/../test")
set(CMAKE_CONFIGURATION_TYPES "Release;Debug" CACHE STRING "Release;Debug")

project(pc_error)

# Comment this block out, if no multithreading is wanted. @DT
find_package(OpenMP)
if (OPENMP_FOUND)
  message(STATUS "OpenMP found.")
  set (CMAKE_C_FLAGS   "${CMAKE_C_FLAGS}   ${OpenMP_C_FLAGS}")
  set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
  add_compile_options( -D OPENMP_FOUND ) 
endif()

execute_process(COMMAND ${CMAKE_C_COMPILER} -dumpversion OUTPUT_VARIABLE GCC_VERSION)
if (GCC_VERSION VERSION_GREATER 4.7 OR GCC_VERSION VERSION_EQUAL 4.7)
  # message(STATUS "Version >= 4.7!" ${GCC_VERSION})
  set (CMAKE_C_FLAGS   "${CMAKE_C_FLAGS}   -std=c++11")
  set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
else()
  # message(STATUS "Version < 4.7!" ${GCC_VERSION})
  set (CMAKE_C_FLAGS   "${CMAKE_C_FLAGS}   -std=c++0x")
  set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")
endif()


file(GLOB_RECURSE PROJ_HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/*.h*)
file(GLOB SOURCE               ${CMAKE_CURRENT_SOURCE_DIR}/*.cpp
                               ${CMAKE_SOURCE_DIR}/../dependencies/program-options-lite/* )

include_directories( ${CMAKE_CURRENT_SOURCE_DIR}
                     ${CMAKE_SOURCE_DIR}/../dependencies/)
message(STATUS "CMAKE_SOURCE_DIR         =" ${CMAKE_SOURCE_DIR})
message(STATUS "CMAKE_CURRENT_SOURCE_DIR =" ${CMAKE_CURRENT_SOURCE_DIR})

if (MSVC)
  add_executable(pc_error ${SOURCE})
else()
  list(REMOVE_ITEM SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/stdafx.cpp")
  add_executable(pc_error ${SOURCE})
endif()

install(TARGETS pc_error DESTINATION ".")

set_target_properties(pc_error PROPERTIES RUNTIME_OUTPUT_DIRECTORY_RELEASE ${PROJECT_OUTPUT_FOLDER})
set_target_properties(pc_error PROPERTIES RUNTIME_OUTPUT_DIRECTORY_DEBUG   ${PROJECT_OUTPUT_FOLDER})
set_target_properties(pc_error PROPERTIES DEBUG_POSTFIX "_d")

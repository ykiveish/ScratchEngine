cd /home/yevgeniy/workspace/proj/ScratchEngine/Src/ScratchEngine
/home/yevgeniy/workspace/proj/ScratchEngine/cross-comp/usr/bin/arm-linux-gnueabihf-g++ ScratchEngine.c -o ScratchEngine -I../../include/ -L../../lib -lTxtControlLib -lMotorIOLib -lSDLWidgetsLib -lKeLibTxt -lROBOProLib
#g++ ScratchEngine.c -o ScratchEngine -I../../include/ -L../../lib
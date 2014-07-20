##
# Simple toplevel Makefile to build rcswitch kmod package 
#
# Stefan Wendler, sw@kaltpost.de 
##

all: build 

build: 
	(cd ./src && make)

deploy: build
	mkdir -p ./deploy/opt/rcswitch/modules
	cp ./src/rcswitch.ko ./deploy/opt/rcswitch/modules/.
	(cd ./deploy && tar -zcvf rcswitch.tgz opt/) 

clean:
	(cd ./src && make clean)
	test -d ./deploy && rm -fr ./deploy

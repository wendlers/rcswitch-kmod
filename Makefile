##
# Simple toplevel Makefile to build SRF05 packages 
#
# Stefan Wendler, sw@kaltpost.de 
##

all: build 

build: 
	make -C ./module

deploy: build
	make -C ./module deploy 
	mkdir -p ./deploy
	cp -a ./module/deploy/opt ./deploy
	(cd ./deploy && tar -zcvf rcswitch-kmod.tgz opt/) 
	
clean:
	make -C ./module clean
	rm -fr ./deploy

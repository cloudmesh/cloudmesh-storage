UNAME := $(shell uname)
ifeq ($(UNAME), Darwin)
define terminal
  osascript -e 'tell application "Terminal" to do script "cd $(PWD); $1"'
endef
endif
ifeq ($(UNAME), Linux)
define terminal
  gnome-terminal --command 'bash -c "cd $(PWD); $1"'
endef
endif

install:
	pip install -r requirements.txt


mkdir:
	$(call terminal, python server.py)
	sleep 3
	@echo "==============================================================================="
	@echo "Make new directory"
	@echo "==============================================================================="
	curl -H "Content-Type:application/json" -X POST -d '{"dir": "testdir"}' http://localhost:8080/cloudmesh/mkdir
	@echo
	@echo "==============================================================================="

ls:
	$(call terminal, python server.py)
	sleep 3
	@echo "==============================================================================="
	@echo "list current directory"
	@echo "==============================================================================="
	curl http://localhost:8080/cloudmesh/ls
	@echo
	@echo "==============================================================================="

cd:
	$(call terminal, python server.py)
	sleep 3
	@echo "==============================================================================="
	@echo "navigate to directory"
	@echo "==============================================================================="
	curl http://localhost:8080/cloudmesh/cd?dir=testdir
	@echo
	@echo "==============================================================================="

add:
	$(call terminal, python server.py)
	sleep 3
	@echo "==============================================================================="
	@echo "Add file link"
	@echo "==============================================================================="
	curl -H "Content-Type:application/json" -X POST -d '{"endpoint": "box:/test.txt", "dir_and_name": "test"}' http://localhost:8080/cloudmesh/add
	@echo
	@echo "==============================================================================="

delete:
	$(call terminal, python server.py)
	sleep 3
	@echo "==============================================================================="
	@echo "delete file link"
	@echo "==============================================================================="
	curl http://localhost:8080/cloudmesh/delete?dir_or_name=test
	@echo
	@echo "==============================================================================="

status:
	$(call terminal, python server.py)
	sleep 3
	@echo "==============================================================================="
	@echo "Get link status"
	@echo "==============================================================================="
	curl http://localhost:8080/cloudmesh/status?dir_or_name=test
	@echo
	@echo "==============================================================================="

get:
	$(call terminal, python server.py)
	sleep 3
	@echo "==============================================================================="
	@echo "Get file"
	@echo "==============================================================================="
	curl http://localhost:8080/cloudmesh/get?name=test'&'destination=~%2F.cloudmesh
	@echo
	@echo "==============================================================================="

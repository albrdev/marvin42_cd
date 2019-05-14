DIR_SRC				:= .
DIR_CFG				:= cfg

DIR_BIN_INSTALL		:= /usr/local/bin
DIR_CFG_INSTALL		:= /etc

SRC_NAME			:= marvin42_cd.py
APP_NAME			:= $(basename $(SRC_NAME))
CFG_NAME			:= $(APP_NAME)rc

CMD_CP				:= cp -f
CMD_RM				:= rm -f
CMD_PRINT			:= @printf

.PHONY: test
test:
	$(CMD_PRINT) "DIR_SRC=$(DIR_SRC)\n"
	$(CMD_PRINT) "DIR_CFG=$(DIR_CFG)\n"
	$(CMD_PRINT) "DIR_BIN_INSTALL=$(DIR_BIN_INSTALL)\n"
	$(CMD_PRINT) "DIR_CFG_INSTALL=$(DIR_CFG_INSTALL)\n"
	$(CMD_PRINT) "SRC_NAME=$(SRC_NAME)\n"
	$(CMD_PRINT) "APP_NAME=$(APP_NAME)\n"
	$(CMD_PRINT) "CFG_NAME=$(CFG_NAME)\n"

.PHONY: install
install:
	$(CMD_CP) --force $(DIR_SRC)/$(SRC_NAME) $(DIR_BIN_INSTALL)/$(APP_NAME)
	$(CMD_CP) --no-clobber $(DIR_CFG)/$(CFG_NAME) $(DIR_CFG_INSTALL)

.PHONY: uninstall
uninstall:
	$(CMD_RM) --force $(DIR_BIN_INSTALL)/$(APP_NAME)

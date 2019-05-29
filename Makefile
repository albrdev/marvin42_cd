DIR_SRC				:= .
DIR_CFG				:= cfg

DIR_BIN_INSTALL		:= /usr/local/bin
DIR_CFG_INSTALL		:= /etc

SRC_NAME			:= marvin42_cd.py
APP_NAME			:= $(basename $(SRC_NAME))
CFG_NAME			:= $(APP_NAME)rc
MOD_NAME			:= modules

CMD_CP				:= cp
CMD_RM				:= rm
CMD_CHMOD			:= chmod
CMD_PRINT			:= @printf

.PHONY: install
install:
	$(CMD_CP) --force $(DIR_SRC)/$(SRC_NAME) $(DIR_BIN_INSTALL)/$(APP_NAME)
	$(CMD_CP) --no-clobber $(DIR_CFG)/$(CFG_NAME) $(DIR_CFG_INSTALL)
	$(CMD_CP) --recursive --no-target-directory --force $(DIR_SRC)/$(MOD_NAME) $(DIR_BIN_INSTALL)/$(MOD_NAME)

	$(CMD_CHMOD) u+x,g+x $(DIR_BIN_INSTALL)/$(APP_NAME)

.PHONY: uninstall
uninstall:
	$(CMD_RM) --recursive --force $(DIR_BIN_INSTALL)/$(MOD_NAME)
	$(CMD_RM) --force $(DIR_BIN_INSTALL)/$(APP_NAME)

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
	# Main
	$(CMD_CP) --force $(DIR_SRC)/$(SRC_NAME) $(DIR_BIN_INSTALL)/$(APP_NAME)
	$(CMD_CP) --force $(DIR_SRC)/chirp_callbacks.py $(DIR_BIN_INSTALL)/chirp_callbacks.py

	# Modules
	$(CMD_CP) --recursive --no-target-directory --force $(DIR_SRC)/$(MOD_NAME) $(DIR_BIN_INSTALL)/$(MOD_NAME)

	# Configs
	$(CMD_CP) --no-clobber $(DIR_CFG)/$(CFG_NAME) $(DIR_CFG_INSTALL)/$(CFG_NAME)

	# MISC
	$(CMD_CHMOD) u+x,g+x,o+x $(DIR_BIN_INSTALL)/$(APP_NAME)

.PHONY: uninstall
uninstall:
	# Modules
	$(CMD_RM) --recursive --force $(DIR_BIN_INSTALL)/$(MOD_NAME)

	# Main
	$(CMD_RM) --force $(DIR_BIN_INSTALL)/chirp_callbacks.py
	$(CMD_RM) --force $(DIR_BIN_INSTALL)/$(APP_NAME)

.PHONY: test
test:
	$(CMD_PRINT) "DIR_SRC=$(DIR_SRC)\n"
	$(CMD_PRINT) "DIR_CFG=$(DIR_CFG)\n"
	$(CMD_PRINT) "DIR_BIN_INSTALL=$(DIR_BIN_INSTALL)\n"
	$(CMD_PRINT) "DIR_CFG_INSTALL=$(DIR_CFG_INSTALL)\n"
	$(CMD_PRINT) "SRC_NAME=$(SRC_NAME)\n"
	$(CMD_PRINT) "APP_NAME=$(APP_NAME)\n"
	$(CMD_PRINT) "CFG_NAME=$(CFG_NAME)\n"
	$(CMD_PRINT) "MOD_NAME=$(MOD_NAME)\n"

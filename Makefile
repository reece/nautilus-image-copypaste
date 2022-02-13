export PATH=/usr/bin:/bin

NAME=nautilus-image-copypaste.py
INSTALL_DIR:=${HOME}/.local/share/nautilus-python/extensions
INSTALL_PATH:=${INSTALL_DIR}/${NAME}


install: ${INSTALL_PATH};
${INSTALL_PATH}: src/${NAME}
	cp -av ${PWD}/$< ${INSTALL_PATH}

install-dev: ${INSTALL_PATH}.dev;
${INSTALL_PATH}.dev: src/${NAME}
	ln -fnsv ${PWD}/$< ${INSTALL_PATH}

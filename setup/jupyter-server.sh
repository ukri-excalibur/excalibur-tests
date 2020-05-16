#/usr/bin/bash
# Configure jupyter for a public notebook server
#
# Usage:
#   ./jupyter-server.sh <<< PASSWORD
#
# Where PASSWORD is the password you want to use to connect to the server.
# Needs to be running in a venv with juypyter installed
# Then start the server:
#   cd ..
#   jupyter notebook

# TODO: NEEDS HOMEDIR EXPANDING EVERYWHERE - NOT VALID IN CONFIG FILE!

# CONFIG:
PORT="8888" # looks like it's allowed on sausage by default
JUPYTERKEY="$HOME/.jupyter/jupyterkey.key"
JUPYTERCERT="$HOME/.jupyter/jupytercert.pem"

# exit when any command fails
set -e

# ensure config file exists:
CONFIG_PATH=$HOME/.jupyter/jupyter_notebook_config.py # this is not configurable for jupyter
if [ -f $CONFIG_PATH ]; then
    cp $CONFIG_PATH $CONFIG_PATH.orig
    echo "backed up existing jupyter config to $CONFIG_PATH.orig"
else
    jupyter notebook --generate-config
    echo "created default jupyter config at $CONFIG_PATH"
fi

# create minimal ssl config:
cat << EOF > .sslconfig
[ req ]
distinguished_name = req_dn
prompt = no
[ req_dn ]
C = GB
EOF

# generate ssl key:
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -config .sslconfig -keyout $JUPYTERKEY -out $JUPYTERCERT
echo

# create a salted/hashed password:
read -s -p "Enter password:" password
echo
hash=`python -c "from notebook.auth import passwd; import sys; print(passwd('$password'))"`
echo "password hash: $hash"

# modify config following
# https://jupyter-notebook.readthedocs.io/en/stable/public_server.html#running-a-public-notebook-server
# except note that c.NotebookApp.ip = '0.0.0.0' not '*'
./cng.py $CONFIG_PATH c.NotebookApp.certfile "c.NotebookApp.certfile = u'$JUPYTERCERT'"
./cng.py $CONFIG_PATH c.NotebookApp.keyfile  "c.NotebookApp.keyfile = u'$JUPYTERKEY'"
./cng.py $CONFIG_PATH c.NotebookApp.ip "c.NotebookApp.ip = '0.0.0.0'"
./cng.py $CONFIG_PATH c.NotebookApp.password "c.NotebookApp.password = u'$hash'"
./cng.py $CONFIG_PATH c.NotebookApp.open_browser "c.NotebookApp.open_browser = False"
./cng.py $CONFIG_PATH c.NotebookApp.port "c.NotebookApp.port = $PORT"
echo "modified config"
echo "done."
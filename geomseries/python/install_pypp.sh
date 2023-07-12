#!/bin/bash

PRFX=${HOME/home/work}/utils

PYPP_LABEL=pypp
PYPP_ROOT=${PRFX}/${PYPP_LABEL}

module -q restore
module -q load cray-python

python -m venv --system-site-packages ${PYPP_ROOT}
. ${PYPP_ROOT}/bin/activate

python -m pip install --upgrade pip
python -m pip install matplotlib

deactivate

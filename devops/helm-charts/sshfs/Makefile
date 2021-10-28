RANDVAL ?= 0
HELM ?= helm upgrade --install --create-namespace
RELEASE_NAME ?= $(shell grep -E '^name:' Chart.yaml | awk '{print $$2}')
ENV ?= dev
NAMESPACE ?= reclada-${ENV}
FILES = vars/${ENV}.yaml
IMAGE_VERSION ?= v0.1.0
IMAGE_TAG ?= ${IMAGE_VERSION}-${RANDVAL}
HELM_ARGS = -n ${NAMESPACE} -f values.yaml -f ${FILES} --set image.tag=${IMAGE_TAG} ${RELEASE_NAME} .

all: install ;
default: template ;

install:
	${HELM} ${HELM_ARGS}

template:
	helm template ${HELM_ARGS}

wait: ;

dev: ENV = dev
dev: all ;

dev1: ENV = dev1
dev1: all ;

dev2: ENV = dev2
dev2: all ;

dev3: ENV = dev3
dev3: all ;

dev4: ENV = dev4
dev4: all ;

dev5: ENV = dev5
dev5: all ;

dev6: ENV = dev6
dev6: all ;

dev7: ENV = dev7
dev7: all ;

dev8: ENV = dev8
dev8: all ;

test: ENV = test
test: all ;

prod: ENV = prod
prod: all ;

demo2: ENV = demo2
demo2: all ;
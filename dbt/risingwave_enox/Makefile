-include .env
export

COMPOSE_FOLDER=../../risingwave/docker
POSTGRES_FOLDER=../postgres_demo
ENOX_FOLDER=risingwave_enox

.PHONY : help up down kafka-ingest

up:
	cd $(COMPOSE_FOLDER) && \
	docker compose -f docker-compose.yml -f kafka-connect/docker-compose.yml up -d

down:
	cd $(COMPOSE_FOLDER) && \
	docker compose -f docker-compose.yml -f kafka-connect/docker-compose.yml down -v


kafka-ingest:
	rpk topic list

	@echo 'Creating redpanda topics' 
	rpk topic add-partitions smartMeter-incoming --num 3 && \
	rpk topic create smartMeter-p-town -p 5 

	@echo 'Successfully created the following topics:' 
	rpk topic list

	@echo 'Register JSON Schema with Karapace Schema Registry' 
	curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
		--data @smartMeter_schema.json \
		http://localhost:8085/subjects/smartMeter-incoming-value/versions

	@echo 'Registered Schema subjects: ' 
	curl -X GET http://localhost:8085/subjects 

	# Activate the virtual environment
	source ../.venv/bin/activate && \
	cd $(POSTGRES_FOLDER) && \
	dbt build && \
	cd ../$(ENOX_FOLDER) && \
	python data-generator.py

	
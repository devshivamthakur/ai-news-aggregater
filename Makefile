.PHONY: install test run migrate migrate-upgrade migrate-downgrade seed clean

install:
	pip install -e .

test:
	pytest

run:
	python scripts/run_aggregator.py

migrate:
	python scripts/migrate_db.py

migrate-upgrade:
	python scripts/run_migrations.py upgrade

migrate-downgrade:
	python scripts/run_migrations.py downgrade

seed:
	python scripts/seed_data.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
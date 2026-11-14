.PHONY: run test build install eval bias baseline

# Run both backend and frontend concurrently
run:
	python run.py

# Install all dependencies
install:
	pip install -r backend/requirements.txt
	cd frontend && npm install

# Run backend and rewrite unit tests
test:
	pytest backend/tests -v
	python frontend/smoke_test.py

# Train baseline ML model
baseline:
	python ml/train_baseline.py

# Run rewrite evaluation
eval:
	python ml/eval_rewrite.py

# Run demographic bias assessment
bias:
	python ml/bias_check.py

# Build frontend production bundle
build:
	cd frontend && npm run build


# Project-S + LangGraph Hybrid System Test Suite

This directory contains comprehensive testing tools for the Project-S + LangGraph hybrid system.

## Testing Architecture

The testing system is structured in multiple layers:

1. **Unit Tests**: Testing individual components in isolation
2. **Integration Tests**: Testing interaction between components
3. **End-to-End Tests**: Testing complete workflows
4. **Performance Tests**: Measuring system performance metrics
5. **API & UI Tests**: Testing external interfaces

## Test Runners

Multiple test runners are available to suit different needs:

### Standard Pytest Runner

```bash
# Run specific test categories
pytest tests/test_*unit.py -v
pytest tests/test_*integration.py -v
pytest tests/test_*e2e.py -v
pytest tests/test_*performance.py -v

# Run all tests
pytest tests/ -v
```

### Comprehensive Test Suite Runner

```bash
# Run all tests with detailed reporting
python run_integrated_tests.py

# Run specific test categories
python run_integrated_tests.py --test-type unit
python run_integrated_tests.py --test-type integration
python run_integrated_tests.py --test-type e2e
python run_integrated_tests.py --test-type performance
python run_integrated_tests.py --test-type api-ui

# Generate HTML report
python run_integrated_tests.py --report --report-dir test_reports
```

### CI/CD Test Runner

```bash
# Run tests in CI/CD environment with XML reporting
python ci_cd_test_runner.py --xml-output --output-dir ci_test_results
```

## Custom Test Scripts

Additional test scripts provide specific testing capabilities:

- `comprehensive_test_suite.py`: Main test runner that executes all test categories
- `basic_test.py`: Tests basic functionality like command execution
- `langgraph_integration_test.py`: Tests the LangGraph integration
- `api_ui_test.py`: Tests API endpoints and UI components

Run them individually:

```bash
python comprehensive_test_suite.py
python basic_test.py
python langgraph_integration_test.py
python api_ui_test.py
```

## Test Reports

Test results are stored in various formats:

- Console output for immediate feedback
- Log files in `logs/` directory
- HTML reports in `tests/test_output/` when using `--report`
- XML reports in specified directory when using CI/CD runner

## Test Configuration

Test configuration is managed through:

- `tests/test_config.py`: Main test configuration
- `tests/test_config/`: Directory with environment-specific configurations

## Adding New Tests

To add new tests:

1. Create a new test file in the `tests/` directory
2. Import the test framework and necessary components
3. Create test functions using pytest fixtures
4. Update `tests/run_all_tests.py` to include the new tests

## Dependencies

Testing dependencies are listed in `requirements-test.txt`:

```bash
pip install -r requirements-test.txt
```

## Best Practices

1. **Isolation**: Each test should be able to run independently
2. **Cleanup**: Tests should clean up after themselves
3. **Mocking**: Use mocks for external dependencies
4. **Documentation**: Document the purpose of each test
5. **Performance**: Keep tests fast to enable frequent runs

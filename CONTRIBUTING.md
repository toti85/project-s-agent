# Contributing to Project-S

We welcome contributions to Project-S! Whether you're fixing bugs, adding new features, or improving documentation, your help is greatly appreciated.

## How to Contribute

1. **Fork the Repository**: Create a fork of the repository on GitHub.
2. **Clone Your Fork**: Clone your fork to your local machine.
   ```bash
   git clone https://github.com/your-username/project-s-agent.git
   ```
3. **Create a Branch**: Create a new branch for your changes.
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make Changes**: Implement your changes and commit them with clear and descriptive commit messages.
   ```bash
   git add .
   git commit -m "Add feature: your-feature-name"
   ```
5. **Push Changes**: Push your changes to your fork.
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Open a Pull Request**: Open a pull request to the main repository. Provide a clear description of your changes and why they should be merged.

## Code of Conduct

Please adhere to our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming and inclusive environment for everyone.

## Reporting Issues

If you encounter any issues or have suggestions for improvements, please open an issue on GitHub. Provide as much detail as possible to help us understand and address the problem.

## Development Guidelines

- Follow the existing code style and structure.
- Write clear and concise commit messages.
- Add tests for new features or bug fixes.
- Update documentation as needed.

## Diagnostics System Guidelines

When contributing to the diagnostics system components:

1. **Performance Considerations**: 
   - Ensure monitoring tools have minimal performance impact
   - Use sampling for high-frequency metrics collection
   - Consider resource usage on the target system

2. **Dashboard UI**:
   - Maintain consistent UI design with the existing components
   - Ensure responsive design for various screen sizes
   - Use the existing color scheme for consistency

3. **LangGraph Integration**:
   - Follow established event patterns when capturing LangGraph events
   - Use the existing visualization tools for workflow graphs
   - Maintain proper error context collection

4. **Testing Diagnostics**:
   - Write tests for new diagnostics features
   - Include tests for dashboard components
   - Test with various configurations (enabled/disabled features)

5. **Documentation**:
   - Document new diagnostics metrics or capabilities
   - Update CLI documentation for new commands
   - Provide examples for new monitoring features

Thank you for contributing to Project-S!
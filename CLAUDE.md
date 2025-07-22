# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

cargo-compete is a Cargo subcommand for competitive programming that automates contest workflows (login, test retrieval, submission, testing) for platforms like AtCoder, Codeforces, and yukicoder.

## Essential Commands

### Build & Development
```bash
# Build
cargo build              # Debug build
cargo build --release    # Release build

# Test
cargo test              # Run tests
cargo test --no-fail-fast --features __test_with_credentials  # Full test suite with online features

# Lint & Format
cargo fmt               # Format code
cargo fmt --all -- --check  # Check formatting (CI)
cargo clippy            # Lint code

# Install locally
cargo install --path .
```

## Architecture Overview

The codebase follows a command-based architecture where each subcommand is implemented as a separate module:

### Core Structure
- **`src/commands/`** - All subcommand implementations (new, test, submit, etc.)
  - Each command is self-contained with its own argument parsing and execution logic
  - Commands interact with the web module for platform-specific operations
  
- **`src/web/`** - Platform-specific web interactions
  - Login, contest retrieval, submission handling
  - Uses snowchains_core for the heavy lifting of web interactions
  
- **`src/config.rs`** - Configuration management
  - Handles compete.toml parsing and validation
  - Manages platform-specific settings and templates

- **`src/testing.rs`** - Test execution framework
  - Runs solutions against test cases
  - Handles timeout, memory limits, and output comparison

### Key Patterns

1. **Command Pattern**: Each CLI subcommand (`cargo compete new`, `cargo compete test`, etc.) maps to a module in `src/commands/`
   
2. **Configuration**: Uses `compete.toml` for user configuration with sensible defaults. Configuration is loaded once and passed through the command chain.

3. **Error Handling**: Comprehensive error types with context. Most functions return `Result<T, anyhow::Error>`.

4. **Web Operations**: All web interactions go through snowchains_core, which handles cookies, authentication, and API calls.

5. **Test Cases**: Stored as YAML files with a specific schema including input, output, and optional extensions (scoring, constraints).

## Development Tips

- When adding new features, check if snowchains_core already supports it
- Test cases are stored in contest packages as YAML files
- The project uses liquid templates for code generation
- Platform-specific behavior is handled in the web module
- Always run `cargo fmt` before committing
- Integration tests require credentials (use `__test_with_credentials` feature)
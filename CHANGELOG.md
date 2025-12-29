# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.2.0] - 2025-12-26

### Added
- add cheat codes and enhance logging setup in PongScene and utils

### Changed
- Pong scene: Implement command pattern for game actions, enhance pause functionality, and modularize systems

### Other
- Merge release/1.1 into develop

## [1.1.7] - 2025-12-19

### Added
- add difficulty presets for CPU and integrate into menu and pong scenes

### Fixed
- update run_game call to use initial_scene parameter instead of MenuScene
- correct spelling in difficulty docstring and remove unused import in pong scene

### Changed
- consolidate menu scene functionality into BaseMenuScene and simplify menu handling
- enhance documentation with type hints and improve asset path retrieval

### Other
- Merge branch 'release/1.1' of github.com:alexsc6955/deja-bounce into release/1.1

## [1.1.6] - 2025-12-16

### Added
- register scenes with SceneRegistry and remove factory functions

### Changed
- remove redundant return types from method signatures

## [1.1.5] - 2025-12-16

### Added
- integrate SceneRegistry for scene management and simplify scene transitions
- enhance menu functionality in MenuScene and PauseScene with MenuStyle integration

### Other
- Merge branch 'release/1.1' of github.com:alexsc6955/deja-bounce into release/1.1

## [1.1.4] - 2025-12-16

### Fixed
- improve draw method in PauseScene to ensure proper rendering of pause overlay

## [1.1.3] - 2025-12-16

### Fixed
- update dependencies and refactor key handling for consistency across scenes

## [1.1.2] - 2025-12-15

### Added
- add PauseScene for game pause functionality with menu options

## [1.1.1] - 2025-12-12

### Changed
- replace WINDOW_SIZE with size attribute in MenuScene for consistency

## [1.1.0] - 2025-12-12

### Changed
- simplify import statements in Paddle class for improved readability
- implement RectDrawMixin for Ball and Paddle classes to standardize drawing logic
- remove redundant newlines in ball collision handling for cleaner code
- integrate Bounds2D and VerticalBounce for improved ball boundary handling
- update Paddle class to use KinematicEntity and streamline movement logic
- remove unused _intersects method to streamline collision logic
- replace paddle intersection checks with collider method for improved clarity
- integrate PaddleConfig into Paddle initialization and update PongScene entity setup
- replace direct width and height access with size attributes in PongScene
- remove unused SpriteEntity import from pong.py
- update ball and paddle entities to use position and size attributes
- update Ball and Paddle classes to use KinematicEntity and improve initialization

### Other
- Merge release/1.0 into develop

## [1.0.2] - 2025-12-08

- Internal changes only.

## [1.0.1] - 2025-12-08

- Internal changes only.

## [1.0.0] - 2025-12-08

### Added
- Update asset handling and main entry point for Deja Bounce
- Add screenshot support, ball trail and overlay system
- enhance paddle movement and ball interaction mechanics for improved gameplay dynamics
- implement CPU paddle controller with configurable settings for enhanced gameplay

### Fixed
- Refactor entry points to use 'run' function and add main module
- Disable trail mode on startup

### Changed
- improve formatting of CpuConfig attributes for better readability
- update references from PyPong to DejaBounce in entry points and logging
- restructure game architecture by removing old classes and implementing a new scene-based approach with updated ball and paddle entities

### Other
- Merge branch 'release/1.0' of github.com:alexsc6955/deja-bounce into release/1.0
- Merge branch 'release/1.0' of github.com:alexsc6955/deja-bounce into release/1.0
- Merge release/0.2 into develop
- Add MenuScene for Deja Bounce main menu with navigation and options
- docs: Revise README to enhance project description, features, and installation instructions
- Refactor game structure: replace Pypong class with scene-based architecture, update ball and paddle classes to use mini-arcade-core, and enhance logging functionality.
- Merge pull request #4 from alexsc6955/develop
- Refactor code structure
- Merge pull request #3 from alexsc6955/development
- license link changed
- readme and license added
- Update issue templates
- Update issue templates
- down wall bug fixed
- ball added
- Merge pull request #2 from alexsc6955/paddles-movement
- paddles movement added
- gitignore added
- Merge pull request #1 from alexsc6955/paddles
- Paddles added
- initial commit


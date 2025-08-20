# Release Process for igvf-utils

This document describes the automated release process for publishing `igvf-utils` to PyPI.

## Overview

The package is automatically published to PyPI when a GitHub release is created. The process includes:
- Package building and validation
- Version verification
- Publishing to PyPI (or Test PyPI for pre-releases)

## Prerequisites

### 1. PyPI Account Setup
- Create account at https://pypi.org
- Enable 2FA for security
- Generate API token for GitHub Actions

### 2. GitHub Repository Setup
Configure the following secrets in your GitHub repository settings:
- `PYPI_API_TOKEN`: Your PyPI API token for publishing to production PyPI
- `TEST_PYPI_API_TOKEN`: Your Test PyPI API token for publishing pre-releases

## Release Process

### Step 1: Prepare the Release

1. **Update Version**: Edit `igvf_utils/version.py` with the new version number:
   ```python
   __version__ = '3.0.4'  # Example: increment from 3.0.3
   ```

2. **Update Documentation**: Ensure README.md and docs are up to date

3. **Test Locally**: Test package building:
   ```bash
   pip install -e .
   python -m build  # Test package building
   ```

4. **Commit and Push**: Push your changes to the main branch:
   ```bash
   git add .
   git commit -m "Bump version to 3.0.4"
   git push origin main
   ```

### Step 2: Create GitHub Release

1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. **Tag version**: Use format `3.0.4` or `v3.0.4` (must match version in version.py)
4. **Release title**: Use format `Release v3.0.4`
5. **Description**: Add release notes describing changes
6. **Pre-release**: Check this for alpha/beta releases (publishes to Test PyPI)
7. Click "Publish release"

### Step 3: Automatic Publishing

Once the release is published, GitHub Actions will automatically:

1. **Verify Version**: Ensure the tag version matches the package version
2. **Build Package**: Create wheel and source distributions
3. **Publish**: Upload to PyPI (or Test PyPI for pre-releases)

### Step 4: Verify Publication

1. Check the GitHub Actions workflow for any errors
2. Verify the package appears at https://pypi.org/project/igvf-utils/
3. Test installation from PyPI:
   ```bash
   pip install igvf-utils==3.0.4
   ```

## Version Management

- Use semantic versioning (MAJOR.MINOR.PATCH)
- The version in `igvf_utils/version.py` must match the Git tag
- For pre-releases, use formats like `3.0.4a1`, `3.0.4b1`, `3.0.4rc1`

## Troubleshooting

### Version Mismatch Error
If you get a version mismatch error:
1. Ensure `igvf_utils/version.py` contains the correct version
2. Ensure the Git tag matches exactly (e.g., `3.0.4` or `v3.0.4` tag for version `3.0.4`)
3. Delete and recreate the release if needed

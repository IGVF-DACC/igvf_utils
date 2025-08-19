# PyPI Publishing Setup - Final Steps

## ✅ Completed Setup

The following components have been set up for automated PyPI publishing:

### 1. Modern Packaging Configuration
- **`pyproject.toml`**: Modern Python packaging configuration with all metadata
- **`setup.py`**: Simplified for backward compatibility
- **`MANIFEST.in`**: Ensures all necessary files are included in distributions

### 2. GitHub Actions Workflows
- **`.github/workflows/publish.yml`**: Automated PyPI publishing on release
- **`.github/workflows/draft-release.yml`**: Helper workflow for creating releases

### 3. Documentation
- **`RELEASE.md`**: Complete release process documentation
- **`PYPI_SETUP.md`**: This setup guide

## 🔑 Required Manual Steps

To complete the setup, you need to:

### 1. Create PyPI Account
1. Go to https://pypi.org and create an account
2. Enable 2-Factor Authentication (required)
3. Go to Account Settings → API tokens
4. Create a new API token with scope "Entire account"
5. Copy the token (starts with `pypi-`)

### 2. Create Test PyPI Account (Optional but Recommended)
1. Go to https://test.pypi.org and create an account
2. Enable 2-Factor Authentication
3. Create API token for testing

### 3. Configure GitHub Repository Secrets
In your GitHub repository, go to Settings → Secrets and variables → Actions:

**Required Secrets:**
- `PYPI_API_TOKEN`: Your PyPI API token for production publishing
- `TEST_PYPI_API_TOKEN`: Your Test PyPI API token (optional)

**To add secrets:**
1. Click "New repository secret"
2. Name: `PYPI_API_TOKEN`
3. Secret: Paste your PyPI token
4. Click "Add secret"

## 🚀 Testing the Setup

### Option 1: Test with Pre-release
1. Update version in `igvf_utils/version.py` (e.g., to `3.0.4a1`)
2. Create a GitHub pre-release with tag `v3.0.4a1`
3. This will publish to Test PyPI only

### Option 2: Use Draft Release Workflow
1. Go to Actions → Draft Release
2. Click "Run workflow"
3. Enter a version number
4. This creates a PR with version bump for review

## 📦 Package Entry Points

The following command-line scripts will be available after installation:
- `iu_check_not_posted`
- `iu_create_gcp_url_list`
- `iu_generate_upload_creds`
- `iu_get_accessions`
- `iu_get_aliases`
- `iu_patch_property`
- `iu_s3_to_gcp`
- `iu_search_results_json`
- `iu_register`

## 🔒 Security Features

- Uses official PyPA publishing action
- API tokens stored as GitHub secrets
- Version verification prevents mismatched releases
- Environment protection for production releases

## 📋 Release Checklist

When ready to release:
1. ✅ PyPI account created with 2FA
2. ✅ GitHub secrets configured
3. ✅ Test the workflow with a pre-release
4. ✅ Follow the process in `RELEASE.md`

## 🆘 Support

If you encounter issues:
1. Check GitHub Actions logs for detailed error messages
2. Verify API tokens have correct permissions
3. Ensure version numbers follow semantic versioning
4. Review the troubleshooting section in `RELEASE.md`

## 🎯 Next Steps

1. **Set up PyPI accounts and tokens** (see above)
2. **Configure GitHub secrets**
3. **Test with a pre-release**
4. **Create your first production release**

The automated publishing is now ready to use! 🎉

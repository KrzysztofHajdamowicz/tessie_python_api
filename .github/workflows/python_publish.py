name: Build and Publish

on:
  push:
    branches:
      - actions
    tags:
      - '*'

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    container:
      image: python:3.11-buster

    steps:
    - name: Determine version from Git tag or set default
      id: versioning
      run: |
        if [[ $GITHUB_REF == refs/tags/* ]]; then
          VERSION=${GITHUB_REF#refs/tags/}
        else
          VERSION="0.0.4"
        fi
        echo "VERSION=$VERSION" >> $GITHUB_ENV

    - name: Check out code
      uses: actions/checkout@v2

    - name: Extract tag version and update pyproject.toml
      run: |
        TAG_VERSION=${GITHUB_REF#refs/tags/}
        echo "Extracted version: ${{ env.VERSION }}"
        sed -i "s/^version = .*/version = '\"${{ env.VERSION }}\"'/" pyproject.toml

    - name: Install dependencies
      run: |
        pip install build twine

    - name: Run build script
      run: ./scripts/build.sh

    - name: Run distribution script
      run: ./scripts/dist_test.sh

    - name: Create a GitHub Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ env.VERSION }}
        release_name: Release ${{ env.VERSION }}
        draft: false
        prerelease: false

    - name: Upload Release Asset
      uses: actions/upload-release-asset@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        upload_url: ${{ steps.create_release.outputs.upload_url }}
        asset_path: ./dist/tessie_api-${{ env.VERSION }}.tar.gz
        asset_content_type: application/gzip

#!/usr/bin/env node
// filepath: c:\project_s_agent\vscode_extension\scripts\package-extension.js

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

// Ensure the package has vsce installed
const checkVsce = () => {
  return new Promise((resolve, reject) => {
    exec('npm list -g vsce', (error, stdout) => {
      if (stdout.includes('vsce')) {
        resolve(true);
      } else {
        console.log('vsce not found, installing globally...');
        exec('npm install -g vsce', (err) => {
          if (err) {
            reject(new Error('Failed to install vsce. Please install manually with: npm install -g vsce'));
          } else {
            resolve(true);
          }
        });
      }
    });
  });
};

// Run the packaging process
const packageExtension = async () => {
  try {
    // Check if vsce is installed
    await checkVsce();
    
    // Get the version from package.json
    const packageJsonPath = path.join(__dirname, '..', 'package.json');
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    const version = packageJson.version;
    
    console.log(`Packaging Project-S VSCode Extension v${version}...`);
    
    // Create dist directory if it doesn't exist
    const distDir = path.join(__dirname, '..', 'dist');
    if (!fs.existsSync(distDir)) {
      fs.mkdirSync(distDir);
    }
    
    // Build the extension
    console.log('Building extension...');
    await new Promise((resolve, reject) => {
      exec('npm run compile', { cwd: path.join(__dirname, '..') }, (error) => {
        if (error) {
          reject(new Error(`Build failed: ${error.message}`));
        } else {
          resolve();
        }
      });
    });
    
    // Package the extension
    console.log('Packaging extension...');
    await new Promise((resolve, reject) => {
      exec('vsce package -o dist/project-s-vscode-extension.vsix', { cwd: path.join(__dirname, '..') }, (error) => {
        if (error) {
          reject(new Error(`Packaging failed: ${error.message}`));
        } else {
          resolve();
        }
      });
    });
    
    console.log(`\nPackaging complete! VSIX file created in the dist folder.`);
    console.log(`Path: ${path.join(distDir, 'project-s-vscode-extension.vsix')}`);
    console.log('\nTo install the extension in VS Code, run:');
    console.log('code --install-extension dist/project-s-vscode-extension.vsix');
    
  } catch (error) {
    console.error(`Error packaging extension: ${error.message}`);
    process.exit(1);
  }
};

packageExtension();

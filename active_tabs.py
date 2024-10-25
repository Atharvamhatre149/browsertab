from flask import Flask, request, jsonify
import subprocess
import os
import psutil  # For managing and killing processes
import shutil  # For cleaning up cache, cookies, etc.
import pygetwindow as gw

app = Flask(__name__)

# Store the subprocesses for browsers
browsers = {
    'chrome': None,
    'firefox': None
}

# Paths to browser executables
BROWSER_PATHS = {
    'chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    'firefox': r'C:\Program Files\Mozilla Firefox\firefox.exe'
}

# Start the browser with the specified URL
@app.route('/start', methods=['GET'])
def start_browser():
    browser = request.args.get('browser')
    url = request.args.get('url')
    
    if browser not in browsers:
        return jsonify({'error': 'Unsupported browser'}), 400

    if browsers[browser] is not None:
        return jsonify({'error': f'{browser.capitalize()} is already running'}), 400

    try:
        if browser == 'chrome':
            # Open Chrome
            process = subprocess.Popen([BROWSER_PATHS['chrome'], url])
        elif browser == 'firefox':
            # Open Firefox
            process = subprocess.Popen([BROWSER_PATHS['firefox'], url])
        
        # Store the process for stopping later
        browsers[browser] = process
        return jsonify({'message': f'{browser.capitalize()} started with {url}'}), 200
    except FileNotFoundError:
        return jsonify({'error': f'{browser.capitalize()} executable not found. Please check the path.'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Stop the browser by killing the process
@app.route('/stop', methods=['GET'])
def stop_browser():
    browser = request.args.get('browser')
    
    if browser not in browsers:
        return jsonify({'error': 'Unsupported browser'}), 400
    
    process = browsers[browser]
    
    if process is None:
        return jsonify({'error': f'{browser.capitalize()} is not running'}), 400

    try:
        # Terminate the process
        process.terminate()
        process.wait()  # Ensure the process is fully terminated
        browsers[browser] = None
        return jsonify({'message': f'{browser.capitalize()} stopped successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Clean up the browser session (history, cache, cookies, etc.)
@app.route('/cleanup', methods=['GET'])
def cleanup_browser():
    browser = request.args.get('browser')
    
    if browser not in browsers:
        return jsonify({'error': 'Unsupported browser'}), 400

    # Only allow cleanup if the browser is not running
    if browsers[browser] is not None:
        return jsonify({'error': f'{browser.capitalize()} is running. Stop it first to clean up.'}), 400
    
    try:
        if browser == 'chrome':
            # Chrome cache and history location (example)
            chrome_cache_path = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default')
            shutil.rmtree(chrome_cache_path, ignore_errors=True)
        elif browser == 'firefox':
            # Firefox cache and history location (example)
            firefox_cache_path = os.path.expandvars(r'%APPDATA%\Mozilla\Firefox\Profiles')
            shutil.rmtree(firefox_cache_path, ignore_errors=True)
        
        return jsonify({'message': f'{browser.capitalize()} session cleaned up'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Flask route to get the active browser URL
@app.route('/geturl', methods=['GET'])
def get_active_url():
    windows = gw.getAllWindows()

# Filter for browser windows (commonly Chrome, Firefox, etc.)
    browser_titles = [window.title for window in windows if 'Chrome' in window.title or 'Firefox' in window.title]

    print("Open browser windows:")
    urls=[]
    for title in browser_titles:
        print(urls.append(title))

    return jsonify({'open_windows': urls}), 200



if __name__ == '__main__':
    app.run(debug=True)
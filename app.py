from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
import os
import shutil
from enhanced_carnatic_analyzer import EnhancedCarnaticAnalyzer

app = Flask(__name__)

# Define the upload folder and the static folder
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static/uploads'
LOGS_FILE = 'logs.txt'

# Ensure the upload folders and logs file exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)


# Allow Flask to serve files from the uploads folder
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/logs')
def logs():
    # Read the logs from the text file
    if os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, 'r') as log_file:
            logs = log_file.readlines()
    else:
        logs = ["No logs available."]

    # Process logs into a structured format for table display
    log_entries = []
    for log in logs:
        log_parts = log.split(" : ")
        if len(log_parts) > 1:
            files_and_similarity = log_parts[0].split(" Vs ")
            file1 = files_and_similarity[0]
            file2 = files_and_similarity[1]
            similarity_data = log_parts[1].split(", ")
            overall_similarity = similarity_data[0].split(": ")[1]
            pattern_similarity = similarity_data[1].split(": ")[1]
            swara_similarity = similarity_data[2].split(": ")[1]
            log_entries.append({
                'file1': file1,
                'file2': file2,
                'overall_similarity': overall_similarity,
                'pattern_similarity': pattern_similarity,
                'swara_similarity': swara_similarity
            })

    return render_template('logs.html', logs=log_entries)


def safe_delete_file(file_path):
    """Safely delete a file with retries and proper error handling."""
    max_retries = 3
    retry_delay = 1  # seconds

    for attempt in range(max_retries):
        try:
            if os.path.exists(file_path):
                # First try to modify file permissions
                os.chmod(file_path, 0o666)
                os.unlink(file_path)
                return True
        except OSError as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            print(f"Failed to delete {file_path} after {max_retries} attempts: {e}")
            return False


def cleanup_uploads():
    """Clear all files in the uploads folder except the logs file."""

    # Function to clean a specific directory
    def clean_directory(directory):
        try:
            # If the directory exists, remove it completely and recreate it
            if os.path.exists(directory):
                shutil.rmtree(directory, ignore_errors=True)
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            print(f"Error cleaning directory {directory}: {e}")

    # Clean both directories
    clean_directory(UPLOAD_FOLDER)
    clean_directory(STATIC_FOLDER)

    # Ensure the logs file exists
    if not os.path.exists(LOGS_FILE):
        try:
            open(LOGS_FILE, 'a').close()
        except Exception as e:
            print(f"Error creating logs file: {e}")


@app.route('/cleanup', methods=['POST'])
def cleanup_route():
    """API endpoint to trigger cleanup of upload folders."""
    try:
        cleanup_uploads()
        return jsonify({"status": "success", "message": "Cleanup completed successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/compare', methods=['POST'])
def compare():
    # Clean up any existing files before processing new ones
    cleanup_uploads()

    if 'file1' not in request.files or 'file2' not in request.files:
        return "Please upload both files."

    file1 = request.files['file1']
    file2 = request.files['file2']

    if file1.filename == '' or file2.filename == '':
        return "Please upload valid files."

    try:
        # Save uploaded files to the uploads folder
        file1_path = os.path.join(UPLOAD_FOLDER, secure_filename(file1.filename))
        file2_path = os.path.join(UPLOAD_FOLDER, secure_filename(file2.filename))

        # Ensure proper permissions when saving files
        file1.save(file1_path)
        os.chmod(file1_path, 0o666)  # Set read/write permissions

        file2.save(file2_path)
        os.chmod(file2_path, 0o666)  # Set read/write permissions

        # Analyze similarity using EnhancedCarnaticAnalyzer
        analyzer = EnhancedCarnaticAnalyzer()
        result = analyzer.analyze_similarity(file1_path, file2_path)

        # Set proper permissions for the visualization file
        visualization_path = os.path.join(STATIC_FOLDER, result["visualization_file"])
        if os.path.exists(visualization_path):
            os.chmod(visualization_path, 0o666)

        # Convert similarity scores to percentage format
        overall_similarity_percentage = round(result['overall_similarity'] * 100, 2)
        pattern_similarity_percentage = round(result['pattern_similarity'] * 100, 2)
        swara_similarity_percentage = round(result['swara_similarity'] * 100, 2)

        # Save the scores to a log file
        log_entry = f"{file1.filename} Vs {file2.filename} : Overall Similarity: {overall_similarity_percentage}%, Pattern Similarity: {pattern_similarity_percentage}%, Swara Similarity: {swara_similarity_percentage}%\n"

        with open(LOGS_FILE, 'a') as log_file:
            log_file.write(log_entry)

        plot_url = f'static/uploads/{result["visualization_file"]}'

        return render_template(
            'results.html',
            overall_similarity=overall_similarity_percentage,
            pattern_similarity=pattern_similarity_percentage,
            swara_similarity=swara_similarity_percentage,
            plot_url=plot_url,
            file1_name=file1.filename,
            file2_name=file2.filename
        )

    except Exception as e:
        cleanup_uploads()  # Clean up in case of error
        return f"An error occurred: {str(e)}"



if __name__ == '__main__':
    # Ensure proper permissions for upload directories on startup
    os.chmod(UPLOAD_FOLDER, 0o777)
    os.chmod(STATIC_FOLDER, 0o777)
    app.run(debug=True, port=8080)
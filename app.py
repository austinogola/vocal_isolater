# import os
# import io
# import numpy as np
# import soundfile as sf
# import eventlet
# from flask import Flask
# from flask_socketio import SocketIO
# from spleeter.separator import Separator

# eventlet.monkey_patch()

# app = Flask(__name__)
# socketio = SocketIO(app, cors_allowed_origins="*")

# separator = Separator('spleeter:2stems')

# @socketio.on("audio_chunk")
# def handle_audio_chunk(data):
#     try:
#         audio_np = np.frombuffer(data, dtype=np.float32)
#         if len(audio_np.shape) == 1:
#             audio_np = np.expand_dims(audio_np, axis=0)
#         prediction = separator.separate(audio_np.T)
#         vocals = prediction["vocals"]

#         buffer = io.BytesIO()
#         sf.write(buffer, vocals.T, 44100, format="WAV")
#         buffer.seek(0)

#         socketio.emit("isolated_vocals", buffer.read())
#     except Exception as e:
#         socketio.emit("error", str(e))

# if __name__ == "__main__":
#     socketio.run(app, debug=True, host="0.0.0.0", port=5000)


import os
import shutil
import subprocess
from flask import Flask, request, send_file
# from spleeter.separator import Separator


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
# separator = Separator('spleeter:2stems')
# separator = Separator('spleeter:2stems')
@app.route("/separate", methods=["POST"])
def separate_audio():
    if "file" not in request.files:
        return {"error": "No file uploaded"}, 400

    file = request.files["file"]
    filename = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filename)

    # Run spleeter
    command = f"spleeter separate -i {filename} -p spleeter:2stems -o {OUTPUT_FOLDER}"
    subprocess.run(command, shell=True, check=True)
    # separator.separate_to_file(filename, OUTPUT_FOLDER)

    # Get the output file
    vocal_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(file.filename)[0], "vocals.wav")

    if not os.path.exists(vocal_path):
        return {"error": "Processing failed"}, 500

    # Send the isolated vocals back
    return send_file(vocal_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)



# # import os
# # import shutil
# # import subprocess
# # from flask import Flask, request, send_file, send_from_directory
# # from zipfile import ZipFile
# # import io

# # app = Flask(__name__)

# # UPLOAD_FOLDER = "uploads"
# # OUTPUT_FOLDER = "output"
# # os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# # os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# # @app.route("/separate", methods=["POST"])
# # def separate_audio():
# #     if "files" not in request.files:
# #         return {"error": "No files uploaded"}, 400

# #     files = request.files.getlist("files")
# #     if not files:
# #         return {"error": "No files uploaded"}, 400

# #     # Process each file
# #     output_files = []
# #     for file in files:
# #         filename = os.path.join(UPLOAD_FOLDER, file.filename)
# #         file.save(filename)

# #         # Run spleeter
# #         command = f"spleeter separate -i {filename} -p spleeter:2stems -o {OUTPUT_FOLDER}"
# #         subprocess.run(command, shell=True, check=True)

# #         # Get the output file
# #         vocal_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(file.filename)[0], "vocals.wav")

# #         if not os.path.exists(vocal_path):
# #             return {"error": f"Processing failed for {file.filename}"}, 500

# #         output_files.append(vocal_path)

# #     # Create a zip archive of all processed files
# #     zip_filename = "processed_vocals.zip"
# #     zip_path = os.path.join(OUTPUT_FOLDER, zip_filename)
# #     with ZipFile(zip_path, 'w') as zipf:
# #         for file in output_files:
# #             zipf.write(file, os.path.basename(file))

# #     # Send the zip file back
# #     return send_file(zip_path, as_attachment=True, download_name=zip_filename)

# # if __name__ == "__main__":
# #     app.run(debug=True)


# import os
# import subprocess
# from flask import Flask, request, send_file, jsonify

# app = Flask(__name__)

# UPLOAD_FOLDER = "uploads"
# OUTPUT_FOLDER = "output"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# @app.route("/separate", methods=["POST"])
# def separate_audio():
#     if "files" not in request.files:
#         return {"error": "No files uploaded"}, 400

#     files = request.files.getlist("files")
#     if not files:
#         return {"error": "No files uploaded"}, 400

#     # Save uploaded files to the upload folder
#     file_paths = []
#     all_file_names=''
#     for file in files:
#         # filename = os.path.join(UPLOAD_FOLDER, file.filename)
#         filename = os.path.join(file.filename)
#         file.save(filename)
#         file_paths.append(filename)
#         all_file_names=all_file_names+' '+f"'{file.filename}'"

#     # Run spleeter in batch mode
#     # command = ["spleeter", "separate", "-o", OUTPUT_FOLDER] + file_paths
#     command='spleeter'+ ' separate '+ '-i '+all_file_names+ ' -o '+ OUTPUT_FOLDER
#     print(command)
#     subprocess.run(command, shell=True, check=True)

#     # Collect the output files
#     output_files = []
#     for file_path in file_paths:
#         base_name = os.path.splitext(os.path.basename(file_path))[0]
#         vocal_path = os.path.join(OUTPUT_FOLDER, base_name, "vocals.wav")
#         if not os.path.exists(vocal_path):
#             return {"error": f"Processing failed for {file_path}"}, 500
#         output_files.append(vocal_path)

#     # Return the list of processed files
#     return jsonify({"processed_files": output_files})

# @app.route("/download/<filename>", methods=["GET"])
# def download_file(filename):
#     # Serve individual files for download
#     base_name = os.path.splitext(filename)[0]
#     vocal_path = os.path.join(OUTPUT_FOLDER, base_name, "vocals.wav")
#     if not os.path.exists(vocal_path):
#         return {"error": "File not found"}, 404
#     return send_file(vocal_path, as_attachment=True)

# if __name__ == "__main__":
#     app.run(debug=True)
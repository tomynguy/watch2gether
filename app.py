from flask import Flask, render_template, request, send_file, url_for, jsonify
from flask_socketio import SocketIO

from pytube import YouTube
import os

app = Flask(__name__)
socketio = SocketIO(app)
directory = r'd:\Projects\watch2gether\downloads\\'
oldUrl = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    global oldUrl# Declare count as a global variable

    youtube_url = request.form['youtube_url']

    if not youtube_url:
        return jsonify({"error": "Please enter a valid YouTube URL"})

    try:
        # Create a YouTube object
        yt = YouTube(youtube_url)

        # Specify the path to the downloaded video file
        print(oldUrl)
        if not oldUrl == None:
            video_file_path = os.path.join(directory, f'{oldUrl}')
            # Check if the video file already exists, and delete it if it does
            print(video_file_path)
            if os.path.exists(video_file_path):
                print("balls1")
                socketio.emit('delete')
                os.remove(video_file_path)

        # Get the highest resolution stream
        video_stream = yt.streams.get_highest_resolution()

        # Download the video
        video_stream.download(directory, filename=f'{yt.video_id}.mp4')

        # Generate the video URL for the play route
        video_url = url_for('play', video_filename=f'{yt.video_id}')

        # Broadcast the video URL and initial playing status to all connected clients
        socketio.emit('video_url', {'video_url': video_url, 'playing': None})
        
        # Set oldUrl
        oldUrl = f'{yt.video_id}.mp4'
        print(oldUrl)
        return jsonify({"success": True, "video_url": video_url})
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({"error": f"Error occurred during download: {str(e)}"})

@app.route('/play/<video_filename>')
def play(video_filename):
    # Specify the path to the downloaded video file
    mp4_file_path = os.path.join(directory, f'{video_filename}.mp4')

    # Use send_file to serve the file
    return send_file(mp4_file_path, mimetype='video/mp4')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('sync')
def handle_sync(data):
    # Broadcast the sync event to all connected clients
    socketio.emit('sync', {'currentTime': data['currentTime'], 'playing': data['playing']})

if __name__ == '__main__':
    socketio.run(app, debug=True)

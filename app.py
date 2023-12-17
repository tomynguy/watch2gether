from flask import Flask, render_template, request, send_file, url_for, jsonify
from flask_socketio import SocketIO

from pytube import YouTube

app = Flask(__name__)
socketio = SocketIO(app)
directory = r'd:\Projects\watch2gether\downloads\\'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    youtube_url = request.form['youtube_url']

    if not youtube_url:
        return jsonify({"error": "Please enter a valid YouTube URL"})

    try:
        # Create a YouTube object
        yt = YouTube(youtube_url)

        # Get the highest resolution stream
        video_stream = yt.streams.get_highest_resolution()

        # Set the output path for the downloaded video
        output_path = f'{directory}/{yt.video_id}.mp4'

        # Download the video
        video_stream.download(directory, filename=f'{yt.video_id}.mp4')

        print(f'Download complete: {output_path}')

        # Generate the video URL for the play route
        video_url = url_for('play', video_filename=yt.video_id)

        # Broadcast the video URL and initial playing status to all connected clients
        socketio.emit('video_url', {'video_url': video_url, 'playing': None})

        return jsonify({"success": True, "video_url": video_url})
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({"error": f"Error occurred during download: {str(e)}"})

@app.route('/play/<video_filename>')
def play(video_filename):
    # Specify the path to the downloaded video file
    mp4_file_path = f'{directory}{video_filename}.mp4'

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

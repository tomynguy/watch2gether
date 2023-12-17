var socket = io.connect('http://' + location.hostname + ':' + location.port);

socket.on('video_url', function(data) {
    var videoUrl = data.video_url;
    var videoTag = `<video id="syncedVideo" width="640" height="360" controls autoplay>
                        <source src="${videoUrl}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>`;
    $('#videoContainer').html(videoTag);

    // Trigger syncVideo when the video is loaded
    $('#syncedVideo').on('loadedmetadata', function() {
        syncVideo();
    });
});

function downloadVideo() {
    var youtubeUrl = $('#youtube_url').val();

    $.ajax({
        type: 'POST',
        url: '/download',
        data: { 'youtube_url': youtubeUrl },
        success: function(response) {
            if (!response.success) {
                alert('Error: ' + response.error);
            }
        },
        error: function(error) {
            alert('Error: ' + error.responseText);
        }
    });
}

function syncVideo() {
    var video = $('#syncedVideo').get(0);

    // Send sync event with the current time and playing status of the video
    $('#syncedVideo').on('timeupdate', function() {
        var currentTime = this.currentTime;
        var playing = !this.paused;
        socket.emit('sync', {'currentTime': currentTime, 'playing': playing});
    });

    // Receive sync event and set the current time and playing status of the video
    socket.on('sync', function(data) {
        if (Math.abs(video.currentTime - data.currentTime) > 1)
            video.currentTime = data.currentTime;

        // Only change the playback status if it differs from the current status
        if (data.playing && video.paused) {
            video.play();
        } else if (!data.playing && !video.paused) {
            video.pause();
        }

    });
}

socket.on('delete', function() {
    $('#syncedVideo').prop('muted', true);
    $('#syncedVideo').remove();
});

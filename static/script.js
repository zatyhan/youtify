$(document).ready(function() {
    $.recognizeTrack = function(startTime, duration, audio, playlistId, trackIds) {
        $('#status-message').text(`Recognizing...`);
        $.ajax(
            {
                type: 'POST',
                url: '/recognize-track',
                data: JSON.stringify({ 'start_time': startTime, 'audio': audio }),
                contentType: 'application/json',
                dataType: 'json',
            }
        ).done(function(result) {
            console.log(`Recognized track from shazam: ${result['title']}`);
            $('#status-message').text(`Recognized track: ${result['title']}`);
                // ajax call to add to playlist
            $.ajax(
                {
                    type: 'POST',
                    url : '/add-to-playlist',
                    data: JSON.stringify({'isrc': result['isrc'], 'playlist_id': playlistId}),
                    contentType: 'application/json',
                    dataType: 'json',
                }
            ).done(function(result) {
                // will log added to playlist
                $('#status-message').text(result['result']);
                result['track_id'] ? trackIds.push(result['track_id']) : null;
                var trackDuration = result['duration'];
                startTime += trackDuration+30;

                if (startTime< duration) {
                    $.recognizeTrack(startTime, duration, audio, playlistId, trackIds);
                    console.log(`New start time: ${startTime}`);
                    console.log(`Track Ids: ${trackIds}`);
                }

                else {
                    $('#status-message').text('Done recognizing all tracks');
                    console.log('All tracks added to playlist');
                }
                
            })
        }); 
    };
    
    $('#create').click( function(event) 
    {
        $('#playlist-link').hide();

        $('[required]').each(function (i, el) {
            if ($(el).val() == '' || $(el).val() == undefined) {
                alert('Please fill in all mandatory fields!');
                event.preventDefault();
                return false;
            }
        });
        $('#status-message').text('Creating playlist...');

        var playlistName = $('#playlist-name').val();
        var playlistId= null;
        console.log(playlistName);

        $.ajax(
            { 
                type: 'POST',
                url: '/create-playlist',
            data: JSON.stringify(encodeURIComponent(playlistName)),
            contentType: 'application/json',
            dataType: 'json',
            success: function(result) {
                $('#status-message').text(result['result'])
                playlistId = result['playlist_id'];
            },
            error: function(result) {
                $('#status-message').text(result['result'])
            }
        })

        $('#status-message').text('Finding and retrieving audio from youtube...');

        var youtubeUrl = $('#youtube-url').val();

        console.log(youtubeUrl);    

        $.ajax(
            { 
                type: 'POST',
                url: '/process-yt-url',
                data: JSON.stringify(encodeURIComponent(youtubeUrl)),
                contentType: 'application/json',
                dataType: 'json',
            }).done(function(result) 
            {
                $('#status-message').text(result['result'])
                // console.log(result)
                
                var startTime = 100;
                const duration = result['audio_duration'];
                const audio= result['audio_data'];
                var trackIds = [];
                var playlistUrl= null;
                
                $.when($.recognizeTrack(startTime, duration, audio, playlistId, trackIds)).done(function() 
                {
                    $.ajax(
                        {
                            type: 'POST',
                            url: '/get-playlist-url',
                            data: JSON.stringify({'playlist_id': playlistId}),
                            contentType: 'application/json',
                            dataType: 'json',
                        }
                    ).done(function(result) {
                        playlistUrl = result['playlist_url'];
                        console.log(playlistUrl);
                        $('#playlist-link').attr('href', playlistUrl);
                        $('#playlist-link').show();
                    });
                });
            });
    });
});
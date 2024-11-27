$(document).ready(function() {
    $('#playlist-link').hide();
    
    $.recognizeTrack = function(startTime, duration, audio, playlistId, trackIds) {

        $('#status-message').text(`Recognizing...`);
        return new Promise((resolve, reject) =>
        {
            $.ajax(
            {
                type: 'POST',
                url: '/recognize-track',
                data: JSON.stringify({ 'start_time': startTime, 'audio': audio }),
                contentType: 'application/json',
                dataType: 'json',
            }
        ).done(function(result) {
            var trackTitle= result['title']
            console.log(`Recognized track from shazam: ${trackTitle}`);
            $('#status-message').text(`Recognized track: ${trackTitle}`);
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
                
                $('#messages').append(`<p>Added ${trackTitle} to playlist</p>`);

                if (trackIds.length > 0) {
                    $('#progress').text(`Found ${trackIds.length} ${trackIds.length==1 ? 'track': 'tracks'} so far...`);
                }

                if (startTime< duration) {
                    $.recognizeTrack(startTime, duration, audio, playlistId, trackIds)
                    .then(resolve)
                    .catch(reject);
                    console.log(`New start time: ${startTime}`);
                    console.log(`Track Ids: ${trackIds}`);
                }
                else {
                    $('#status-message').text('Done recognizing all tracks');
                    console.log('All tracks added to playlist');
                    resolve();
                }
            }).fail(reject);
            if (startTime >= duration) {
                resolve();
            };
        }).fail(reject); 
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
        var youtubeUrl = $('#youtube-url').val();
        var playlistUrl= null;
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
                
                var startTime = 0;
                const duration = result['audio_duration'];
                const audio= result['audio_data'];
                var trackIds = [];

                console.log(`playlistId: ${playlistId}`);
                
                $.recognizeTrack(startTime, duration, audio, playlistId, trackIds).then(function() 
                {
                    $('#progress').text('');

                    playlistUrl= `https://open.spotify.com/playlist/${playlistId}`;
                    $('#playlist-link').attr('href', playlistUrl);
                    $('#playlist-link').show();
                    // $.ajax(
                    //     {
                    //         type: 'POST',
                    //         url: '/get-playlist-url',
                    //         data: JSON.stringify({'playlist_id': playlistId}),
                    //         contentType: 'application/json',
                    //         dataType: 'json',
                    //     }
                    // ).done(function(result) {
                    //     playlistUrl = result['playlist_url'];
                    //     console.log(playlistUrl);
                    //     $('#playlist-link').attr('href', playlistUrl);
                    //     $('#playlist-link').show();
                    // });
                }).catch((error) => {
                    console.error(error);
                });
            });
            $('button#playlist-link').click(function() {
                window.open(playlistUrl, '_blank');
            });
    });
});
$(document).ready(function() {
    $('button').click( function(event) {
        $('[required]').each(function (i, el) {
            if ($(el).val() == '' || $(el).val() == undefined) {
                alert('Please fill in all mandatory fields!');
                event.preventDefault();
                return false;
            }
        });
        $('#status-message').text('Creating playlist...');

        var playlistName = $('#playlist-name').val();

        console.log(playlistName);

        var createPlaylist= $.ajax(
            { 
                type: 'POST',
                url: '/create-playlist',
            data: JSON.stringify(encodeURIComponent(playlistName)),
            contentType: 'application/json',
            dataType: 'json',
            success: function(result) {
                $('#status-message').text(result['result'])
                console.log(result)
            },
            error: function(result) {
                $('#status-message').text(result['result'])
            }
        })
        createPlaylist.fail(function(result) {
            throw new Error(result['error']);
        });

        $('#status-message').text('Finding and retrieving audio from youtube...');

        var youtubeUrl = $('#youtube-url').val();

        console.log(youtubeUrl);    

        var createProcessor= $.ajax(
            { 
                type: 'POST',
                url: '/process-yt-url',
            data: JSON.stringify(encodeURIComponent(youtubeUrl)),
            contentType: 'application/json',
            dataType: 'json',
            success: function(result) {
                $('#status-message').text(result['result'])
                console.log(result)
            },
            error: function(result) {
                $('#status-message').text(result['error'])
            }
        });

        createProcessor.fail(function(result) {
            throw new Error(result['error']);
        });

        // convert base64 to buffer
        // send post request to shazam api on loop, add isrcs and titles to array
        // send flask request for isrc lookup
        // add track id to array 
        //  add track to playlist
    






    });



});
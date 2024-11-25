from pyscript import document

def make_request(url):
    try:
        response = pyfetch(url)
        return response.json()
    except Exception as e:
        return {'error': str(e)}
def foo(e):
    text= document.querySelector('#status-message')
    playlist_name= document.querySelector('#playlist-name')
    youtube_url= document.querySelector('#youtube-url')
    text.innerText= youtube_url.value
    # try: 
    #     processor = Processor(youtube_url.value)
    #     text.innerText= 'Processor created successfully'
    # except Exception as e:
    #     text.innerText= 'Failed to create processor ' + str(e)

    document.querySelector('#playlist-form').reset()

def main():
    yt_url= document.getElementById('youtube_url')
    button= document.getElementById('create')
    print('Hello')
    # button.addEventListener('click', pyodide.create_proxy(foo))

# main()
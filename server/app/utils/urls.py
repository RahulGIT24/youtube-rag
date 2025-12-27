from urllib.parse import urlparse, parse_qs

def extract_youtube_video_id(url:str)->str | None:
    parsed_url = urlparse(url)

    hostname = parsed_url.netloc.replace("www.", "").replace("m.", "")

    if hostname == "youtu.be":
        return parsed_url.path.lstrip('/')
    
    if parsed_url.path=='/watch':
        return parse_qs(parsed_url.query).get('v',[None])[0]
    
    if parsed_url.path.startswith(('/embed/','/shorts/')):
        return parsed_url.path.split('/')[2]

    return None
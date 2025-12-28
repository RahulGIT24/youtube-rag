from youtube_transcript_api import YouTubeTranscriptApi

class Transcript:
    ytt_api = YouTubeTranscriptApi()

    def fetch_transcript(self,video_id:str):
        try:
            fetched_transcript = self.ytt_api.fetch(video_id)
            return self.chunk_transcript(fetched_transcript)
        except Exception as e:
            raise e
    
    def chunk_transcript(self,transcript):
        current_chunk = ""
        current_start = 0.0
        grouped_chunks = []
        
        for snippet in transcript:
            start=snippet.start
            text=snippet.text

            if current_chunk == "":
                current_start = start
            
            current_chunk += " " + text

            if len(current_chunk) > 500:
                grouped_chunks.append({
                    "text":current_chunk.strip(),
                    "start":current_start,
                })
                current_chunk = ""
        
        if current_chunk:
            grouped_chunks.append({
                "text": current_chunk.strip(),
                "start": current_start,
            })
        
        return grouped_chunks

transcibe = Transcript()
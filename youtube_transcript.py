# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click",
#     "youtube_transcript_api",
# ]
# ///

import re
import sys
from typing import Optional
import click
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled


def extract_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([^&\n?#]+)',
        r'youtube\.com/embed/([^&\n?#]+)',
        r'youtube\.com/v/([^&\n?#]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


@click.command()
@click.argument('url')
@click.option('--output', '-o', type=click.Path(), help='Output file path (default: stdout)')
@click.option('--timestamps/--no-timestamps', default=True, help='Include timestamps (default: True)')
def main(url: str, output: Optional[str], timestamps: bool) -> None:
    """Extract transcript from a YouTube video.
    
    URL can be a full YouTube URL or just the video ID.
    """
    try:
        video_id = extract_video_id(url) or url
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Format the transcript
        formatted_lines = []
        for entry in transcript:
            if timestamps:
                timestamp = format_timestamp(entry['start'])
                formatted_lines.append(f"[{timestamp}] {entry['text']}")
            else:
                formatted_lines.append(entry['text'])
        
        transcript_text = '\n'.join(formatted_lines)
        
        # Output handling
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(transcript_text)
            click.echo(f"Transcript saved to: {output}")
        else:
            click.echo(transcript_text)
            
    except TranscriptsDisabled:
        click.echo("Error: Transcripts are disabled for this video.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
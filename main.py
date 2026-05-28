import os
import glob
from anthropic import Anthropic
from dotenv import load_dotenv
from lxml import etree

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def parse_ami_transcript(meeting_id, words_dir="words"):
    """Parse AMI XML word files and reconstruct transcript by speaker"""
    print(f"\n📂 Loading AMI meeting: {meeting_id}")
    
    # Find all speaker files for this meeting
    pattern = os.path.join(words_dir, f"{meeting_id}.*.words.xml")
    files = sorted(glob.glob(pattern))
    
    if not files:
        print(f"❌ No files found for meeting {meeting_id}")
        return None
    
    print(f"   Found {len(files)} speaker files")
    
    all_words = []
    
    for file in files:
        # Extract speaker ID from filename e.g. EN2001a.A.words.xml -> A
        speaker = file.split('.')[-3]
        
        tree = etree.parse(file)
        root = tree.getroot()
        
        # Extract words with timestamps
        for word in root.iter('w'):
            text = word.text
            start_time = word.get('starttime')
            if text and start_time:
                all_words.append({
                    'speaker': speaker,
                    'text': text,
                    'start': float(start_time)
                })
    
    # Sort by time
    all_words.sort(key=lambda x: x['start'])
    
    # Group into speaker turns
    transcript_lines = []
    current_speaker = None
    current_words = []
    
    for word in all_words:
        if word['speaker'] != current_speaker:
            if current_words:
                transcript_lines.append(f"Speaker {current_speaker}: {' '.join(current_words)}")
            current_speaker = word['speaker']
            current_words = [word['text']]
        else:
            current_words.append(word['text'])
    
    # Add last turn
    if current_words:
        transcript_lines.append(f"Speaker {current_speaker}: {' '.join(current_words)}")
    
    transcript = '\n'.join(transcript_lines)
    word_count = len(all_words)
    print(f"✅ Transcript built — {word_count} words, {len(files)} speakers")
    return transcript

def summarise_meeting(transcript):
    print("\n🤖 Analysing with Claude...")
    
    # Truncate if too long (keep first 3000 words)
    words = transcript.split()
    if len(words) > 3000:
        transcript = ' '.join(words[:3000])
        print(f"   ℹ️  Truncated to 3000 words for API limits")
    
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""You are an expert meeting analyst. Analyse this AMI corpus meeting transcript and provide a structured report.

Your report must include:
1. SUMMARY — A concise 3-5 sentence overview
2. KEY DECISIONS — Bullet list of decisions made
3. ACTION ITEMS — Bullet list of tasks mentioned
4. MAIN TOPICS — Key topics discussed
5. MEETING DYNAMICS — Brief note on participation and discussion style

Transcript:
{transcript}

Provide a clean structured report."""
            }
        ]
    )
    
    return message.content[0].text

def save_report(meeting_id, report, human_summary=None):
    output_path = f"{meeting_id}_report.txt"
    with open(output_path, 'w') as f:
        f.write(f"AMI MEETING SUMMARY REPORT\n")
        f.write(f"Meeting ID: {meeting_id}\n")
        f.write("=" * 50 + "\n\n")
        f.write(report)
        if human_summary:
            f.write("\n\n" + "=" * 50 + "\n")
            f.write("HUMAN GOLD STANDARD SUMMARY (AMI Corpus)\n")
            f.write("=" * 50 + "\n\n")
            f.write(human_summary)
    print(f"✅ Report saved: {output_path}")
    return output_path

def run(meeting_id):
    print("\n🚀 AMI Meeting Summariser")
    print("=" * 45)
    
    # Parse AMI transcript
    transcript = parse_ami_transcript(meeting_id)
    if not transcript:
        return
    
    # Load human summary for comparison
    human_summary = load_human_summary(meeting_id)
    
    # Summarise with Claude
    report = summarise_meeting(transcript)
    
    # Print report
    print("\n" + "=" * 45)
    print(report)
    
    # Print human summary for comparison
    if human_summary:
        print("\n" + "=" * 45)
        print("HUMAN GOLD STANDARD SUMMARY (AMI Corpus):")
        print("=" * 45)
        print(human_summary)
    
    print("=" * 45)
    
    # Save report
    save_report(meeting_id, report, human_summary)
    
    print("\n🎉 Done!")

def load_human_summary(meeting_id, abstractive_dir="abstractive"):
    """Load the human-written gold standard summary from AMI corpus"""
    path = os.path.join(abstractive_dir, f"{meeting_id}.abssumm.xml")
    if not os.path.exists(path):
        print(f"   ℹ️  No human summary found for {meeting_id}")
        return None
    
    tree = etree.parse(path)
    root = tree.getroot()
    
    sentences = []
    for sentence in root.iter('sentence'):
        if sentence.text:
            sentences.append(sentence.text.strip())
    
    return ' '.join(sentences)

if __name__ == "__main__":
    run("ES2002a")
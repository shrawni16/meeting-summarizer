# AMI Meeting Summariser

An AI-powered meeting summarisation pipeline built with Python and Claude API, using the AMI Meeting Corpus as the data source.

## What it does

Given an AMI corpus meeting ID, this pipeline automatically:

1. Parses multi-speaker XML transcripts from the AMI corpus
2. Reconstructs the conversation ordered by speaker turn and timestamp
3. Sends the transcript to Claude (Haiku) for structured analysis
4. Generates a detailed report including summary, key decisions, action items, topics, and meeting dynamics
5. Loads the human gold standard summary for side-by-side comparison

## Background

This project is a practical implementation of my MSc Computer Science research at Queen Mary University of London, which investigates slide-aware meeting summarisation using LLMs on the AMI corpus. This pipeline demonstrates the baseline transcript-only summarisation condition.

## Tech stack

- Python 3
- Anthropic Claude API (claude-haiku)
- AMI Meeting Corpus (manual annotations v1.6.2)
- `lxml` for XML parsing
- `python-dotenv` for credential management

## Setup

1. Clone the repo
2. Cre
8. Run: `python3 main.py`

## Example output
## Author

Srabani Banerjee — [LinkedIn](https://www.linkedin.com/in/srabanibanerjee) | MSc CS @ QMUL

#!/usr/bin/env python3
"""
Web UI for Trailer-to-Campaign Autopilot
Modern Flask-based interface for generating marketing campaigns
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Ensure .env is loaded from project root
from dotenv import load_dotenv
load_dotenv(project_root / '.env')

from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime
import json
import threading

from src.autopilot import CampaignAutopilot
from src.utils.config import Config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'trailer-to-campaign-autopilot-2025'

# Store campaign generation status
generation_status = {}


@app.route('/')
def index():
    """Main page with campaign generation form."""
    return render_template('index.html', config=Config)


@app.route('/api/config')
def get_config():
    """Get current configuration status."""
    return jsonify({
        'tmdb_configured': bool(Config.TMDB_API_KEY or Config.TMDB_BEARER_TOKEN),
        'youtube_configured': bool(Config.YOUTUBE_API_KEY),
        'gemini_configured': Config.has_gemini(),
        'openai_configured': Config.has_openai(),
        'ai_available': Config.has_ai_api(),
        'default_regions': Config.DEFAULT_REGIONS,
        'max_comments': Config.MAX_COMMENTS_ANALYZE
    })


@app.route('/api/generate', methods=['POST'])
def generate_campaign():
    """Generate marketing campaign from trailer."""
    data = request.json
    
    trailer_url = data.get('trailer_url')
    movie_title = data.get('movie_title')
    regions = data.get('regions', Config.DEFAULT_REGIONS)
    
    if not trailer_url or not movie_title:
        return jsonify({'error': 'Missing trailer_url or movie_title'}), 400
    
    # Parse regions if string
    if isinstance(regions, str):
        regions = [r.strip() for r in regions.split(',')]
    
    # Generate unique ID for this job
    job_id = f"{movie_title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Initialize status
    generation_status[job_id] = {
        'status': 'starting',
        'progress': 0,
        'message': 'Initializing...',
        'result': None,
        'error': None
    }
    
    # Run generation in background thread
    def run_generation():
        try:
            generation_status[job_id]['status'] = 'running'
            generation_status[job_id]['message'] = 'Analyzing trailer...'
            generation_status[job_id]['progress'] = 10
            
            # Debug: Check if Gemini is configured
            print(f"🔍 DEBUG: Gemini API Key configured: {bool(Config.GEMINI_API_KEY)}")
            print(f"🔍 DEBUG: has_gemini(): {Config.has_gemini()}")
            
            autopilot = CampaignAutopilot()
            print(f"🔍 DEBUG: Autopilot gemini_enhancer: {autopilot.gemini_enhancer}")
            if autopilot.gemini_enhancer:
                print(f"🔍 DEBUG: Gemini enhancer is_available(): {autopilot.gemini_enhancer.is_available()}")
            
            generation_status[job_id]['message'] = 'Collecting metadata...'
            generation_status[job_id]['progress'] = 20
            
            campaign = autopilot.run_full_campaign(
                trailer_url=trailer_url,
                movie_title=movie_title,
                target_regions=regions
            )
            
            # Save campaign to file
            outputs_dir = Path(__file__).parent.parent / 'outputs'
            outputs_dir.mkdir(exist_ok=True)
            filename = f"{job_id}.json"
            output_path = outputs_dir / filename
            
            autopilot.save_campaign(campaign, str(output_path))
            
            generation_status[job_id]['progress'] = 100
            generation_status[job_id]['status'] = 'completed'
            generation_status[job_id]['message'] = 'Campaign generated successfully!'
            generation_status[job_id]['result'] = campaign
            generation_status[job_id]['filename'] = filename
            
        except Exception as e:
            generation_status[job_id]['status'] = 'error'
            generation_status[job_id]['error'] = str(e)
            generation_status[job_id]['message'] = f'Error: {str(e)}'
    
    thread = threading.Thread(target=run_generation)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'job_id': job_id,
        'message': 'Campaign generation started'
    })


@app.route('/api/status/<job_id>')
def get_status(job_id):
    """Get generation status for a job."""
    if job_id not in generation_status:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(generation_status[job_id])


@app.route('/api/campaigns')
def list_campaigns():
    """List all generated campaigns."""
    outputs_dir = Path(__file__).parent.parent / 'outputs'
    
    if not outputs_dir.exists():
        return jsonify({'campaigns': []})
    
    campaigns = []
    for file in sorted(outputs_dir.glob('*.json'), reverse=True):
        try:
            with open(file) as f:
                data = json.load(f)
                campaigns.append({
                    'filename': file.name,
                    'movie_title': data.get('input', {}).get('movie_title', 'Unknown'),
                    'generated_at': data.get('generated_at'),
                    'regions': data.get('input', {}).get('target_regions', [])
                })
        except:
            continue
    
    return jsonify({'campaigns': campaigns[:20]})  # Last 20


@app.route('/api/campaign/<filename>')
def get_campaign(filename):
    """Get specific campaign data."""
    outputs_dir = Path(__file__).parent.parent / 'outputs'
    file_path = outputs_dir / filename
    
    if not file_path.exists():
        return jsonify({'error': 'Campaign not found'}), 404
    
    try:
        with open(file_path) as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/view/<filename>')
def view_campaign(filename):
    """View campaign in UI."""
    return render_template('results.html', filename=filename)


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


if __name__ == '__main__':
    import sys
    print("🎬 Trailer-to-Campaign Autopilot Web UI")
    print("=" * 60)
    print(f"🐍 Python: {sys.executable}")
    print(f"🌐 Server: http://localhost:8080")
    print(f"📊 TMDb: {'✓' if Config.TMDB_API_KEY or Config.TMDB_BEARER_TOKEN else '✗'}")
    print(f"📺 YouTube: {'✓' if Config.YOUTUBE_API_KEY else '✗'}")
    
    # Check Gemini with detailed info
    gemini_status = '✗'
    if Config.has_gemini():
        try:
            from src.generators.gemini_enhancer import GeminiEnhancer
            test_enhancer = GeminiEnhancer()
            if test_enhancer.is_available():
                gemini_status = '✓ Gemini'
            else:
                gemini_status = '⚠️  Gemini (not available)'
        except Exception as e:
            gemini_status = f'❌ Gemini ({str(e)[:30]}...)'
    
    print(f"🤖 AI: {gemini_status}")
    print("=" * 60)
    print("Press Ctrl+C to stop")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=8080)

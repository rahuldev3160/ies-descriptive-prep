#!/bin/bash
# NotebookLM Audio Generation Script — RBI DEPR 2026
# Usage: ./generate_rbi_audios.sh
#
# MANUAL STEP REQUIRED BEFORE RUNNING:
# The notebooklm CLI does not support 'create notebook' — you must create notebooks
# manually at notebooklm.google.com and paste the IDs below.
#
# Steps:
# 1. Go to notebooklm.google.com
# 2. Create notebook: "RBI DEPR - Monetary Policy & Banking"
#    → Upload source: data/notebooklm/rbi_01_monetary_banking_source.md
#    → Copy the notebook ID from the URL (format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
#    → Paste below as RBI01
# 3. Create notebook: "RBI DEPR - Indian Economy & Fiscal"
#    → Upload source: data/notebooklm/rbi_02_economy_fiscal_source.md
#    → Copy the notebook ID from the URL
#    → Paste below as RBI02
# 4. Run: chmod +x scripts/generate_rbi_audios.sh && ./scripts/generate_rbi_audios.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPTS_DIR="$SCRIPT_DIR/notebooklm_prompts"
AUDIO_OUT="$SCRIPT_DIR/../data/audio"
NLM="notebooklm"

# PASTE NOTEBOOK IDs HERE after creating manually on notebooklm.google.com
RBI01="REPLACE_WITH_RBI01_NOTEBOOK_ID"
RBI02="REPLACE_WITH_RBI02_NOTEBOOK_ID"

mkdir -p "$AUDIO_OUT/rbi"

generate_audio() {
    local notebook_id="$1"
    local prompt_file="$2"
    local audio_title="$3"
    local out_dir="$4"

    echo ""
    echo "======================================"
    echo "Generating: $audio_title"
    echo "Notebook:   $notebook_id"
    echo "======================================"

    $NLM generate audio \
        -n "$notebook_id" \
        --prompt-file "$prompt_file" \
        --format deep-dive \
        --length medium \
        --wait \
        --timeout 900

    echo "Generation complete. Downloading..."
    $NLM download audio \
        -n "$notebook_id" \
        --latest \
        "$out_dir/${audio_title}.mp4"

    echo "Saved: $out_dir/${audio_title}.mp4"
    echo "Waiting 30 seconds before next audio..."
    sleep 30
}

if [[ "$RBI01" == "REPLACE_WITH_RBI01_NOTEBOOK_ID" ]]; then
    echo "ERROR: Paste your RBI01 notebook ID into this script first."
    exit 1
fi

if [[ "$RBI02" == "REPLACE_WITH_RBI02_NOTEBOOK_ID" ]]; then
    echo "ERROR: Paste your RBI02 notebook ID into this script first."
    exit 1
fi

echo "=== RBI DEPR 2026: 2 audio episodes ==="

generate_audio "$RBI01" "$PROMPTS_DIR/RBI_A1_monetary_policy_banking.txt" \
    "RBI_A1_monetary_policy_banking" "$AUDIO_OUT/rbi"

generate_audio "$RBI02" "$PROMPTS_DIR/RBI_A2_economy_fiscal_budget.txt" \
    "RBI_A2_economy_fiscal_budget" "$AUDIO_OUT/rbi"

echo ""
echo "=== Audio generation complete ==="
echo ""
echo "Next steps:"
echo "1. Convert mp4 → mp3:"
echo "   ffmpeg -i \"$AUDIO_OUT/rbi/RBI_A1_monetary_policy_banking.mp4\" -vn -acodec libmp3lame -q:a 2 \"$AUDIO_OUT/rbi/RBI - A1 - Monetary Policy & Banking.mp3\""
echo "   ffmpeg -i \"$AUDIO_OUT/rbi/RBI_A2_economy_fiscal_budget.mp4\" -vn -acodec libmp3lame -q:a 2 \"$AUDIO_OUT/rbi/RBI - A2 - Economy & Fiscal.mp3\""
echo ""
echo "2. Generate thumbnails:"
echo "   python3.11 scripts/create_thumbnails.py --paper rbi"
echo ""
echo "3. Upload to YouTube:"
echo "   python3.11 scripts/upload_to_youtube.py --paper rbi"

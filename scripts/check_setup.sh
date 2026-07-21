#!/usr/bin/env bash
# gbro-collage-broll Vertex environment self-check.
# Exit 0 = all good; exit 1 = at least one item missing (details on stdout).

set -u

VENV_PY="$HOME/hyperframes-projects/.omni-venv/bin/python"
BACKEND="${OMNI_BACKEND:-vertex}"
ADC_FILE="${GOOGLE_APPLICATION_CREDENTIALS:-$HOME/.config/gcloud/application_default_credentials.json}"
MODE="${1:---video}"
FAIL=0

ok()   { printf 'PASS  %s\n' "$1"; }
bad()  { printf 'FAIL  %s\n' "$1"; FAIL=1; }

case "$MODE" in
  --image-fallback|--video) ;;
  *)
    printf 'Usage: %s [--image-fallback|--video]\n' "$0" >&2
    exit 2
    ;;
esac

if [ "$MODE" = "--image-fallback" ]; then
  BACKEND="vertex"
fi

# 1. Vertex auth shared by image fallback and video generation
if [ "$BACKEND" = "vertex" ]; then
  PROJECT_ID="${OMNI_PROJECT_ID:-${GOOGLE_CLOUD_PROJECT:-}}"
  if command -v gcloud >/dev/null 2>&1; then
    ok "gcloud CLI 可用"
  else
    bad "gcloud CLI 缺失（安装：https://cloud.google.com/sdk/docs/install）"
  fi
  if [ -n "$PROJECT_ID" ]; then
    ok "Vertex project 已设置（${PROJECT_ID}）"
  else
    bad "Vertex project 未设置（export GOOGLE_CLOUD_PROJECT=你的项目ID）"
  fi
  if [ -r "$ADC_FILE" ]; then
    ok "Vertex ADC 凭据已配置"
  else
    bad "Vertex ADC 凭据缺失（运行：gcloud auth application-default login）"
  fi
  if command -v gcloud >/dev/null 2>&1 && gcloud auth application-default print-access-token >/dev/null 2>&1; then
    ok "Vertex ADC 凭据可刷新"
  else
    bad "Vertex ADC 凭据无法刷新（运行：gcloud auth application-default login）"
  fi
  if [ "${OMNI_LOCATION:-${GOOGLE_CLOUD_LOCATION:-global}}" = "global" ]; then
    ok "Vertex location=global"
  else
    bad "Gemini Omni Flash 当前要求 location=global"
  fi
elif [ -n "${GEMINI_API_KEY:-}" ]; then
  ok "Gemini API 兼容后端：GEMINI_API_KEY 已设置"
else
  bad "Gemini API 兼容后端缺少 GEMINI_API_KEY"
fi

# 2. ffmpeg / ffprobe are only required by the video stage
if [ "$MODE" = "--video" ]; then
  if command -v ffmpeg >/dev/null 2>&1 && command -v ffprobe >/dev/null 2>&1; then
    ok "ffmpeg / ffprobe 可用"
  else
    bad "ffmpeg / ffprobe 缺失（macOS: brew install ffmpeg；Debian/Ubuntu: sudo apt install ffmpeg）"
  fi
fi

# 3. Python >= 3.10
if command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
  ok "python3 >= 3.10"
else
  bad "python3 缺失或版本低于 3.10"
fi

# 4. shared venv with google-genai >= 2.10.0
if [ -x "$VENV_PY" ] && "$VENV_PY" - <<'PY' 2>/dev/null
import sys
from google import genai
parts = [int(x) for x in genai.__version__.split(".")[:2]]
sys.exit(0 if parts >= [2, 10] else 1)
PY
then
  ok "共享 venv 就绪（google-genai >= 2.10.0）"
else
  bad "共享 venv 未创建或 google-genai 版本过旧（创建：python3 -m venv ~/hyperframes-projects/.omni-venv && ~/hyperframes-projects/.omni-venv/bin/python -m pip install --upgrade 'google-genai>=2.10.0' 'httpx[socks]'）"
fi

exit $FAIL

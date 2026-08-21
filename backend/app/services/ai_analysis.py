"""AI-powered repo analysis using LLM (OpenRouter / DeepSeek)."""
import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def get_llm_client():
    """Get async HTTP client config for LLM API calls."""
    api_key = os.getenv("LLM_API_KEY", "")
    base_url = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
    model = os.getenv("LLM_MODEL", "deepseek/deepseek-chat-v3-0724")
    if not api_key or api_key == "sk-or-v1-your-free-openrouter-key-here":
        return None
    return {"api_key": api_key, "base_url": base_url.rstrip("/"), "model": model}

def build_analysis_prompt(project_info, metrics, smells, architecture):
    return f"""You are a senior software engineer conducting a codebase review.

## Repository Information
- **Name:** {project_info.get('project_name', 'N/A')}
- **Type:** {project_info.get('repository_type', 'N/A')}
- **Primary Language:** {project_info.get('primary_language', 'N/A')}
- **Frameworks:** {', '.join(project_info.get('frameworks', []) or [])}
- **Total Files:** {project_info.get('total_files', 0)}
- **Has README:** {project_info.get('has_readme', False)}
- **Has Tests:** {project_info.get('has_tests', False)}

## Code Metrics
- **Code Lines:** {metrics.get('total_code_lines', 0)}
- **Comment Ratio:** {metrics.get('comment_ratio', 0) * 100:.1f}%
- **Total Complexity:** {metrics.get('total_complexity', 0)}
- **Avg Complexity:** {metrics.get('total_complexity', 0) / max(metrics.get('code_files_scanned', 1), 1):.1f}
- **Max Depth:** {metrics.get('max_directory_depth', 0)}

## Code Smells
{json.dumps(smells.get('smells', []), indent=2) if smells.get('smells') else 'None detected'}

## Architecture
- **Pattern:** {architecture.get('architecture_pattern', 'N/A')}
- **Type:** {architecture.get('architecture_type', 'N/A')}
- **Has src/:** {architecture.get('has_src_directory', False)}
- **Has tests/:** {architecture.get('has_tests_directory', False)}

## Your Task
Return ONLY valid JSON (no markdown) with this structure:
{{
  "executive_summary": "2-3 sentence overview",
  "strengths": ["3-5 key strengths"],
  "risks": ["3-5 risks or concerns"],
  "recommendations": ["3-5 actionable recommendations"],
  "refactoring_suggestions": [
    {{"area": "Area name", "description": "What to improve", "priority": "high/medium/low", "effort": "small/medium/large"}}
  ],
  "ai_health_score": <0-100>,
  "ai_grade": "<A/B/C/D/F>"
}}
"""


async def analyze_with_llm(project_info, metrics, smells, architecture):
    """Send repo data to LLM and get AI-powered analysis."""
    cfg = get_llm_client()
    if not cfg:
        logger.warning("LLM not configured — set LLM_API_KEY in .env")
        return None

    prompt = build_analysis_prompt(project_info, metrics, smells, architecture)
    try:
        import httpx
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{cfg['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {cfg['api_key']}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://engineeros.app",
                    "X-Title": "EngineerOS",
                },
                json={
                    "model": cfg["model"],
                    "messages": [
                        {"role": "system", "content": "You are an expert codebase reviewer. Return ONLY valid JSON."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[-1]
                content = content.rsplit("```", 1)[0]
            content = content.strip()
            result = json.loads(content)
            result["model_used"] = cfg["model"]
            return result
    except json.JSONDecodeError as e:
        logger.error(f"LLM returned invalid JSON: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"LLM API error: {e.response.status_code} - {e.response.text[:300]}")
    except Exception as e:
        logger.error(f"LLM analysis failed: {e}")
    return None


async def enhance_analysis_with_ai(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """Take existing rule-based analysis and enrich it with AI insights."""
    ai_result = await analyze_with_llm(
        analysis_result.get("project", {}),
        analysis_result.get("metrics", {}),
        analysis_result.get("smells", {}),
        analysis_result.get("architecture", {}),
    )
    if ai_result:
        analysis_result["ai_analysis"] = ai_result
        analysis_result["ai_health_score"] = ai_result.get("ai_health_score")
        analysis_result["ai_grade"] = ai_result.get("ai_grade")
        analysis_result["refactoring_suggestions"] = ai_result.get("refactoring_suggestions", [])
    else:
        analysis_result["ai_analysis"] = None
        analysis_result["ai_health_score"] = None
        analysis_result["ai_grade"] = None
        analysis_result["refactoring_suggestions"] = []
    return analysis_result


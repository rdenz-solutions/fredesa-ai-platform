#!/usr/bin/env python3
"""Deploy simple test agent using verified working pattern"""

import os
import sys
import uuid
import requests
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configuration
PROJECT_ID = "019b61fe-3fba-716f-b0aa-8bdff5004898"
AIRIA_API_BASE = "https://api.airia.ai/v1"

def load_api_key() -> str:
    """Load API key from environment"""
    api_key = os.getenv("AIRIA_API_KEY")
    if not api_key:
        env_paths = [
            Path(__file__).parent.parent.parent / ".env",
            Path.home() / "Project Files/rdenz-knowledge-registry/.env"
        ]
        for env_path in env_paths:
            if env_path.exists():
                with open(env_path) as f:
                    for line in f:
                        if line.startswith("AIRIA_API_KEY="):
                            api_key = line.split("=", 1)[1].strip()
                            break
                if api_key:
                    break
    return api_key

def discover_models(api_key: str, project_id: str) -> dict:
    """Discover available models in project"""
    response = requests.get(
        f"{AIRIA_API_BASE}/Models?projectId={project_id}",
        headers={"x-api-key": api_key}
    )
    if response.ok:
        data = response.json()
        # Handle paginated response
        models = data.get('items', data if isinstance(data, list) else [])
        model_map = {}
        for model in models:
            if not isinstance(model, dict):
                continue
            name = model.get('displayName', '').lower()
            model_id = model.get('id')
            if 'gpt-4o mini' in name or 'gpt-4o-mini' in name:
                model_map['gpt-4o-mini'] = model_id
            elif 'gpt-4o' in name:
                model_map['gpt-4o'] = model_id
            elif 'claude' in name and 'sonnet' in name:
                model_map['claude-sonnet'] = model_id
            if 'default' not in model_map:
                model_map['default'] = model_id
        return model_map
    return {}

def create_prompt(api_key: str, project_id: str, name: str, message: str) -> dict:
    """Create prompt with unique name"""
    unique_name = f"{name} ({uuid.uuid4().hex[:8]})"
    response = requests.post(
        f"{AIRIA_API_BASE}/Prompts",
        headers={"x-api-key": api_key, "Content-Type": "application/json"},
        json={
            "projectId": project_id,
            "name": unique_name,
            "isAgentSpecific": False,
            "message": message
        }
    )
    response.raise_for_status()
    result = response.json()
    return {
        "promptId": result.get("id"),
        "versionId": result.get("activeVersionId")
    }

def create_agent(api_key: str, project_id: str, model_id: str, prompt_data: dict) -> dict:
    """Create agent with verified dual-handle structure"""
    
    # Generate IDs
    input_id = str(uuid.uuid4())
    input_out_id = str(uuid.uuid4())
    input_out_uuid = str(uuid.uuid4())
    
    ai_id = str(uuid.uuid4())
    ai_in_id = str(uuid.uuid4())
    ai_in_uuid = str(uuid.uuid4())
    ai_out_id = str(uuid.uuid4())
    ai_out_uuid = str(uuid.uuid4())
    
    output_id = str(uuid.uuid4())
    output_in_id = str(uuid.uuid4())
    output_in_uuid = str(uuid.uuid4())
    
    payload = {
        "name": "FreDeSa Knowledge Test Agent",
        "projectId": project_id,
        "alignment": "Vertical",
        "steps": [
            {
                "id": input_id,
                "stepType": "InputStep",
                "stepTitle": "User Query",
                "position": {"x": "100", "y": "100"},
                "handles": [
                    {
                        "id": input_out_id,
                        "uuid": input_out_uuid,
                        "type": "source",
                        "label": "Query",
                        "x": 0.5,
                        "y": 1.0
                    }
                ],
                "dependenciesObject": []
            },
            {
                "id": ai_id,
                "stepType": "AIOperation",
                "stepTitle": "Knowledge Response",
                "modelId": model_id,
                "temperature": 0.7,
                "maxTokens": 4096,
                "reasoningEffort": "medium",
                "includeDateTimeContext": False,
                "chatHistoryLimit": 0,
                "position": {"x": "100", "y": "300"},
                "promptSegments": [
                    {
                        "stepId": ai_id,
                        "promptId": prompt_data["promptId"],
                        "selectedPromptVersionId": prompt_data["versionId"],
                        "order": 0
                    }
                ],
                "handles": [
                    {
                        "id": ai_in_id,
                        "uuid": ai_in_uuid,
                        "type": "target",
                        "label": "input",
                        "x": 0.5,
                        "y": 0.0
                    },
                    {
                        "id": ai_out_id,
                        "uuid": ai_out_uuid,
                        "type": "source",
                        "label": "output",
                        "x": 0.5,
                        "y": 1.0
                    }
                ],
                "dependenciesObject": [
                    {
                        "parentId": input_id,
                        "parentHandleId": input_out_uuid,
                        "handleId": ai_in_uuid
                    }
                ]
            },
            {
                "id": output_id,
                "stepType": "OutputStep",
                "stepTitle": "Response",
                "position": {"x": "100", "y": "500"},
                "handles": [
                    {
                        "id": output_in_id,
                        "uuid": output_in_uuid,
                        "type": "target",
                        "label": "Result",
                        "x": 0.5,
                        "y": 0.0
                    }
                ],
                "dependenciesObject": [
                    {
                        "parentId": ai_id,
                        "parentHandleId": ai_out_uuid,
                        "handleId": output_in_uuid
                    }
                ]
            }
        ]
    }
    
    response = requests.post(
        f"{AIRIA_API_BASE}/PipelinesConfig",
        headers={"x-api-key": api_key, "Content-Type": "application/json"},
        json=payload
    )
    response.raise_for_status()
    return response.json()

def main():
    print("\n🚀 Deploying FreDeSa Knowledge Test Agent")
    print(f"Project: {PROJECT_ID}\n")
    
    api_key = load_api_key()
    if not api_key:
        print("❌ AIRIA_API_KEY not found")
        return 1
    
    print("✅ API key loaded")
    
    # Discover models
    print("\n📋 Discovering models...")
    models = discover_models(api_key, PROJECT_ID)
    if not models:
        print("❌ No models found")
        return 1
    
    print(f"✅ Found {len(models)} models:")
    for name, mid in models.items():
        print(f"   • {name}: {mid[:8]}...")
    
    model_id = models.get('gpt-4o-mini') or models.get('gpt-4o') or models.get('default')
    model_name = [k for k, v in models.items() if v == model_id][0]
    print(f"\n✅ Using: {model_name}")
    
    # Create prompt
    print("\n📝 Creating knowledge-enhanced prompt...")
    prompt_message = """You are a FreDeSa Knowledge Platform test agent with access to 1,043 authoritative sources across federal contracting, cybersecurity, AI/LLM frameworks, and 40+ other domains.

For every query:
1. Reference relevant authoritative sources from the knowledge base
2. Cite sources using format: [Source: Name, Authority XX]
3. Include authority scores: 90 (Official: FAR, NIST), 70 (Expert: guides), 50 (Community)
4. Add "AUTHORITATIVE SOURCES" section at the end

Example:
"According to FAR Part 15 [Source: Federal Acquisition Regulation Part 15, Authority 90], proposals require... The Shipley methodology [Source: Shipley Capture Management, Authority 70] recommends..."

Your responses differentiate FreDeSa AI from generic assistants through authoritative, cited knowledge."""
    
    prompt_data = create_prompt(api_key, PROJECT_ID, "FreDeSa Knowledge Test Agent", prompt_message)
    print(f"✅ Prompt created: {prompt_data['promptId'][:8]}...")
    
    # Create agent
    print("\n🤖 Creating agent...")
    agent = create_agent(api_key, PROJECT_ID, model_id, prompt_data)
    agent_id = agent['id']
    
    print(f"\n✅ SUCCESS!")
    print(f"   Agent ID: {agent_id}")
    print(f"   URL: https://airia.ai/{PROJECT_ID}/agents/{agent_id}")
    print(f"   Model: {model_name}")
    print(f"   Steps: {len(agent.get('steps', []))}")
    
    print("\n🧪 Test with:")
    print('   "What are FAR subcontracting requirements?"')
    print('   "What is NIST AI Risk Management Framework?"')
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
API_BASE = "http://localhost:8080/api"

# 1. Expose our backend to the LLM (MCP Tool Definitions)
tools = [
    {
        "type": "function",
        "function": {
            "name": "list_products",
            "description": "Get the merchant's available products and prices",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "checkout",
            "description": "Purchase items. Requires an array of items and reasoning.",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "string"},
                                "quantity": {"type": "integer"}
                            }
                        }
                    },
                    "agent_reasoning": {"type": "string"}
                },
                "required": ["items", "agent_reasoning"]
            }
        }
    }
]

def execute_tool(name, args):
    if name == "list_products":
        return requests.get(f"{API_BASE}/products").json()
    elif name == "checkout":
        return requests.post(f"{API_BASE}/checkout", json=args).json()
    return {"error": "tool not found"}

def run_buyer_agent(goal: str):
    print(f"\n🎯 Agent Goal: {goal}")
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = [
        {"role": "system", "content": "You are an autonomous AI buyer agent. Browse the catalog and purchase items to achieve the user's goal. You MUST call the `checkout` tool to finalize the purchase. Do not just narrate your actions; you must execute the tool. Always explain your reasoning in the tool call."},
        {"role": "user", "content": goal}
    ]
    
    payload = {
        "model": os.getenv("GROQ_MODEL"),
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto"
    }
    
    # --- Step 1: Agent asks for the catalog ---
    response = requests.post(GROQ_URL, headers=headers, json=payload).json()
    
    if "error" in response:
        print("❌ API Error:", response["error"]["message"])
        return
        
    message = response["choices"][0]["message"]
    messages.append(message) # Save the agent's action to history
    
    if "tool_calls" not in message or not message["tool_calls"]:
        print("🤖 Agent response:", message.get("content"))
        return

    # Execute tools
    for tool_call in message["tool_calls"]:
        func_name = tool_call["function"]["name"]
        args = json.loads(tool_call["function"]["arguments"])
        print(f"⚙️ Action: Calling {func_name} with {args}")
        
        result = execute_tool(func_name, args)
        print(f"✅ Result: {json.dumps(result, indent=2)}\n")
        
        # Feed the tool's output back to the LLM
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": json.dumps(result)
        })

    # --- Step 2: Agent reviews catalog and makes purchase ---
    payload["messages"] = messages
    final_response = requests.post(GROQ_URL, headers=headers, json=payload).json()
    
    final_message = final_response["choices"][0]["message"]
    if "tool_calls" in final_message and final_message["tool_calls"]:
         for tool_call in final_message["tool_calls"]:
            func_name = tool_call["function"]["name"]
            args = json.loads(tool_call["function"]["arguments"])
            print(f"⚙️ Action: Calling {func_name} with {args}")
            
            result = execute_tool(func_name, args)
            print(f"✅ Result: {json.dumps(result, indent=2)}\n")
    else:
         print("🤖 Agent response:", final_message.get("content"))

if __name__ == "__main__":
    # Test 1: Cheap item (Under 5k INR -> Auto-approves)
    run_buyer_agent("I need to buy 1 batch of API credits for my data pipeline.")
    
    # Test 2: Expensive item (5k to 50k INR -> Hits Human Intervention Queue)
    run_buyer_agent("I want to lease an XL Server Instance.")

    # Test 3: Budget Breach (Over 50k INR -> Hard Block)
    run_buyer_agent("Buy the Enterprise Setup.")
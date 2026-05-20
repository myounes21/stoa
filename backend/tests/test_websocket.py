import asyncio
import json
import websockets

async def main():
    uri = "ws://localhost:8001/ws/debate"

    print("=" * 60)
    print("STOA WEBSOCKET TEST")
    print("=" * 60 + "\n")

    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({
            "query": "which is better one piece or attack on titan"
        }))
        print("Query sent. Waiting for stream...\n")

        async for raw in ws:
            message = json.loads(raw)
            msg_type = message.get("type")

            if msg_type == "arena_ready":
                data = message["data"]
                print(f"Arena Ready: {data['topic']}")
                print(f"   {data['team_a']} vs {data['team_b']}\n")

            elif msg_type == "agent_output":
                data = message["data"]
                team = data["team"]
                agent = data["agent"]
                content = data["content"]
                status = data.get("status", "")
                label = f"[Team {team}] {agent}"
                if status:
                    label += f" [{status}]"
                print(f"{label}:")
                print(f"   {content[:300]}...\n")

            elif msg_type == "argument":
                data = message["data"]
                print(f"Team {data['team']} Speaker:")
                print(f"   {data['content'][:300]}...\n")

            elif msg_type == "round_complete":
                print(f"--- Round {message['data']['round']} Complete ---\n")

            elif msg_type == "truth_report":
                data = message["data"]
                print(f"Truth Report:")
                print(f"   Verified: {data['verified_count']}")
                print(f"   False:    {data['false_count']}")
                print(f"   Unknown:  {data['unverified_count']}\n")

            elif msg_type == "verdict":
                data = message["data"]
                print(f"Verdict:")
                print(f"   Winner: {data['winner']}")
                print(f"   Team A overall: {data['team_a_scores']['overall']}")
                print(f"   Team B overall: {data['team_b_scores']['overall']}")
                print(f"\n   Team A scores:")
                print(f"      Factual accuracy:      {data['team_a_scores']['factual_accuracy']}")
                print(f"      Logical consistency:   {data['team_a_scores']['logical_consistency']}")
                print(f"      Rebuttal effectiveness:{data['team_a_scores']['rebuttal_effectiveness']}")
                print(f"\n   Team B scores:")
                print(f"      Factual accuracy:      {data['team_b_scores']['factual_accuracy']}")
                print(f"      Logical consistency:   {data['team_b_scores']['logical_consistency']}")
                print(f"      Rebuttal effectiveness:{data['team_b_scores']['rebuttal_effectiveness']}")
                print(f"\nAnalysis:\n{data['written_analysis']}\n")
                if data.get("penalties"):
                    print(f"Penalties:")
                    for p in data["penalties"]:
                        print(f"   - {p}")
                    print()

            elif msg_type == "complete":
                print("Stream complete.")
                break

            elif msg_type == "error":
                print(f"Error: {message['message']}")
                break

asyncio.run(main())
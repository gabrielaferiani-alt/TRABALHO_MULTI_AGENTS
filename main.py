import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from quantum_finance.agents.lead_advisor import lead_advisor_agent


async def run_interactive_chat():
    session_service = InMemorySessionService()
    runner = Runner(
        agent=lead_advisor_agent,
        app_name="quantum_finance",
        session_service=session_service,
    )
    session = await session_service.create_session(
        app_name="quantum_finance",
        user_id="usuario_01",
    )

    print("\n" + "=" * 65)
    print("  QUANTUM FINANCE -- Consultor Financeiro Inteligente")
    print("  Powered by Google ADK + Gemini | Dados reais da B3 e BCB")
    print("=" * 65)
    print("\nOla! Digite 'sair' para encerrar.\n")

    while True:
        try:
            user_input = input("Voce: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando...")
            break
        if not user_input:
            continue
        if user_input.lower() in ("sair", "exit", "quit"):
            print("\nBons investimentos!")
            break

        content = types.Content(role="user", parts=[types.Part(text=user_input)])
        print("\nConsultor: ", end="", flush=True)

        final_response = ""
        async for event in runner.run_async(
            user_id="usuario_01",
            session_id=session.id,
            new_message=content,
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = event.content.parts[0].text
                break
        print(final_response)
        print()


root_agent = lead_advisor_agent

if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        print("AVISO: configure GOOGLE_API_KEY no arquivo .env")
    asyncio.run(run_interactive_chat())

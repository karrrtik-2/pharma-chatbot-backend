from langchain_core.messages import HumanMessage

from workflow import build_workflow


if __name__ == "__main__":
    app = build_workflow()

    inputs = [
        HumanMessage(content="can you check and make a booking if general dentist available on 8 August 2024 at 8 PM?")
    ]
    state = {"messages": inputs, "id_number": 10232303, "next": "", "query": "", "current_reasoning": ""}
    result = app.invoke(state)

    print(result["messages"][-1].content)

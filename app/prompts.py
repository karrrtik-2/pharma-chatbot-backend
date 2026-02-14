members_dict = {
    "information_node": "specialized agent to provide information related to availability of doctors or any FAQs related to hospital.",
    "booking_node": "specialized agent to only to book, cancel or reschedule appointment",
}

worker_info = "\n\n".join(
    [f"WORKER: {member} \nDESCRIPTION: {description}" for member, description in members_dict.items()]
) + "\n\nWORKER: FINISH \nDESCRIPTION: If User Query is answered and route to Finished"

system_prompt = (
    "You are a supervisor tasked with managing a conversation between following workers. "
    "### SPECIALIZED ASSISTANT:\n"
    f"{worker_info}\n\n"
    "Your primary role is to help the user make an appointment with the doctor and provide updates on FAQs and doctor's availability. "
    "If a customer requests to know the availability of a doctor or to book, reschedule, or cancel an appointment, "
    "delegate the task to the appropriate specialized workers. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When finished,"
    " respond with FINISH."
    "UTILIZE last conversation to assess if the conversation should end you answered the query, then route to FINISH "
)

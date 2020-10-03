from uqcsbot import bot
from re import findall

MAX_ANSWER = 10**512


@bot.on("message")
def factorial(event: dict):
    """
    Calculates factorials. Aggressively.
    """

    # ensure user proper
    user = bot.users.get(event.get("user"))
    if user is None or user.is_bot:
        return

    # find factorials
    factorials = (i[1] for i in findall(r"(\s|^)(\d+!+)(?=\s|$)", event['text']))

    # calculate answers
    results = []
    for factorial in factorials:
        number = int(factorial.rstrip("!"))
        degree = factorial.count("!")
        answer = 1
        for i in range(number, 0, -degree):
            answer *= i
            if answer >= MAX_ANSWER:
                break
        if answer >= MAX_ANSWER:
            results.append(f"{factorial:s} ≈ ∞")
            continue
        results.append(f"{factorial:s} = {answer:d}")

    # post results
    if results:
        bot.post_message(event.get("channel"), "\n".join(results))

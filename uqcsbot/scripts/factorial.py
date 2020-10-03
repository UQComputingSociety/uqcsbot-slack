from uqcsbot import bot
from re import findall


def is_human(user):
    """
    checks that the user is not a bot
    exists for test mocking
    """
    return user is not None and not user.is_bot


@bot.on("message")
def factorial(event: dict):
    """
    Calculates factorials. Aggressively.
    """

    # ensure user proper
    user = bot.users.get(event.get("user"))
    if not is_human(user):
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
        results.append(f"{factorial:s} = {answer:d}")

    # post results
    if results:
        bot.post_message(event.get("channel"), "\n".join(results))

    

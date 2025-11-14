"""Template messages to dynamically response in different situations"""
import random


def empty_area_msg(search_url: str):
    """Return a random message telling user area is empty"""

    msgs = [
        f"Oh no! 😔 Your search criteria didn't return any homes.\n\n"
        f"🔗 Is this your [Search URL]({search_url})?\n\n",
        f"Hmm, it looks like your filters might be a little too strict! Zero results were found for the criteria I generated.\n\n"
        f"🔗 Here is the [Search URL]({search_url}) I attempted to use.",
        f"I couldn't find any homes that match those exact filters.\n\n"
        f"🔗 Please check your [Search URL]({search_url}) to confirm the filters I used.\n\n",
        f"I'm sorry, no properties were returned with your current requirements.\n\n"
        f"🔗 Review the [Search URL]({search_url}) to see the full set of filters applied.\n\n",
        f"It seems the location and filters you provided returned no available homes. The region might be too small or the criteria too tight.\n\n"
        f"🔗 Here is the [Search URL]({search_url}) that resulted in zero matches.\n\n"
    ]
    
    return random.choice(msgs)

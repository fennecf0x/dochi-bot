import setup
from dochi.state import state
from dochi.database import db, get, model, update

for user in list(model.User.select()):
    likability = get.likability_from_user(user)
    after_decrement = lambda v, r: max(0, v - r * 1.1 * (0.25 + v / 200 if v < 70 else 0.2 + 2.5 / (v - 60)))

    update.likability(
        user.user_id,
        kindliness=after_decrement(likability.kindliness, 0.7),
        unkindliness=after_decrement(likability.unkindliness, 1),
        friendliness=after_decrement(likability.friendliness, 0.7),
        unfriendliness=after_decrement(likability.unfriendliness, 1),
        respectfulness=after_decrement(likability.respectfulness, 0.7),
        disrespectfulness=after_decrement(likability.disrespectfulness, 1),
    )

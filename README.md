# code-it

Code-it leverages LLMs to generate code - unlike other solutions, it doesn't try to rely on the smartness of LLMs, but rather assume they are rather dumb and perform several mistakes along the way.

It applies a simple algorithm to iteratively code towards it's task objective, in a similar way a programmer might do.

This algorithm is implemented with control statements and different prompts to steer the LLM at performing the correct action.

It is **not** an autonomous agent - at most, we could call it semi-autonomous.

# kthGTP


# Examples

```console
$ python src/main.py https://play.kth.se/media/Game-5/0_czbw6n1q "Summarise this lecture into 5 bullets"
url: https://play.kth.se/media/Game-5/0_czbw6n1q
query: Summarise this lecture into 5 bullets

fetching content link...
downloading lecture...
extracting audio...
transcribing lecture...
generating a digested summary...


1. The lecture discussed cooperative models in game theory and bargain models developed by John Nash.
2. The computation of Nash equilibria was discussed, including finding a strategy for player two in the Stravinsky game.
3. The lecture discussed the concept of security levels in cooperative models in game theory and John Nash's work on the bargain solution.
4. Nash suggested four axioms for a reasonable solution to the bargain problem, and showed that the solution is unique and is the point in the set that maximizes the product of x and y.
5. The lecture discussed the Nash-Pargin solution and how it can be translated to a game theoretical situation, with the idea of maximizing the product being the main idea behind the solution.

$ python src/main.py https://play.kth.se/media/Game-5/0_czbw6n1q "Where in the lecture can i find out more about the four axioms?"
url: https://play.kth.se/media/Game-5/0_czbw6n1q
query: Where in the lecture can i find out more about the four axioms?

 You can find more information about the four axioms in the transcript between 20:00 and 40:00.

$ python src/main.py https://play.kth.se/media/Game-5/0_czbw6n1q "If i didn't attend this lecture what would I have to read-up on?"
url: https://play.kth.se/media/Game-5/0_czbw6n1q
query: If i didn't attend this lecture what would I have to read-up on?

 To understand the content of the lecture, you may have to read up on the following topics:

- Cooperative models in game theory
- Bargain models developed by John Nash
- Nash equilibria and its computation, including finding a strategy for player two in the Stravinsky game
- Cooperation, including pre-negotiation and agreement on a pure set of strategies, and the concept of correlated equilibrium
- The bargain problem from a non-zero-sum game perspective and the set of possible outcomes from a correlated equilibrium
- Security levels in cooperative models in game theory
- John Nash's work on the bargain solution, including his definition of Nash equilibrium and the existence of Nash equilibria
- Nash's axioms for a reasonable solution to the bargain problem, including Pareto optimality, symmetry between the two players, invariance to scale, and independence of irrelevant alternatives
- The Nash-Pargin solution and how it can be translated to a game theoretical situation
- The idea of maximizing the product of two variables in a game theoretical situation.
```

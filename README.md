# kthGTP


# Examples

```console
$ python src/main.py https://play.kth.se/media/Game-5/0_czbw6n1q "Summarise this lecture into 5 bullets"

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

```

> Query: Where in the lecture can i find out more about the four axioms?

```bash
$ python src/main.py https://play.kth.se/media/Game-5/0_czbw6n1q "Where in the lecture can i find out more about the four axioms?"

 You can find more information about the four axioms in the transcript between 20:00 and 40:00.
```

> Query: If i didn't attend this lecture what would I have to read-up on?

```bash
$ python src/main.py https://play.kth.se/media/Game-5/0_czbw6n1q "If i didn't attend this lecture what would I have to read-up on?"

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

> Query: Summarise the core concepts of this lecture in a few bullets

```bash
$ python src/main.py https://play.kth.se/media/avalg21%20Lecture%2010%20Part%201/0_3xg3hl0c "Summarise the core concepts of this lecture in a few bullets"

- The lecture covers two streaming algorithms, the Misregris algorithm and L1 sampling.
- The L1 sampling problem involves picking a random number from a stream of numbers after the entire stream has been read.
- The solution to the L1 sampling problem is called the reservoir sampling algorithm.
- The speaker explains L0 sampling, a problem where a random number from a stream of numbers must be picked without repetition.
- L0 sampling can be used to find the approximate median of a stream of numbers.
- The solution to L0 sampling involves hashing and assumes the availability of a perfectly random hash function.
- The speaker mentions a special case where there are only two different numbers in the input stream and mentions a simple solution for it.
```

> Query: Summarise the core concepts of this lecture in a few bullets, add extra explanations to each that helps even a novice in the area understand what it's about

```bash
$ python src/main.py https://play.kth.se/media/avalg21%20Lecture%2010%20Part%201/0_3xg3hl0c "Summarise the core concepts of this lecture in a few bullets, add extra explanations to each that helps even a novice in the area understand what it's about"
 The lecture covers two streaming algorithms, the Misregris algorithm and L1 sampling. The speaker explains two problems in the area of sampling from a stream of numbers:

1. L1 Sampling: The problem involves picking a random number from a stream of numbers after the entire stream has been read. The solution to the problem is called the reservoir sampling algorithm, which involves changing the number being kept track of with a decreasing probability as more numbers are read. The algorithm is simple and outputs a uniformly chosen random number from the input stream.

2. L0 Sampling: The problem involves picking a random number from a stream of numbers without repetition. The output of L0 sampling will be either one number or another with probability half. The speaker mentions that L0 sampling can be used to find the approximate median of a stream of numbers. The solution to L0 sampling involves hashing and assumes the availability of a perfectly random hash function.

3. Special case of two numbers: The speaker mentions a special case where there are only two different numbers in the input stream. There is a simple way to solve this case by storing both numbers and outputting one of them at random at the end. However, this solution doesn't generalize to solving the general case.
```

> Query: What would be a typical exam question about the topcis in this lecture?

```bash
$ python src/main.py https://play.kth.se/media/avalg21%20Lecture%2010%20Part%201/0_3xg3hl0c "What would be a typical exam question about the topcis in this lecture?"
 A typical exam question about the topics in this lecture could be: "Explain the Misregris algorithm and L1 sampling and how they can be used to pick a random number from a stream of numbers. Discuss the differences between L0 sampling and L1 sampling and the challenges involved in finding the approximate median of a stream of numbers. Explain the general approach to solving problems involving hashing."
```

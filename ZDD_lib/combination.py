class Combination:
    def __init__(self, n:int) -> None:
        self.fact = [1.0]
        for i in range(1, n+1):
            self.fact.append(self.fact[-1]*i)

    def binom(self, i:int, j:int) -> float:
        return self.fact[i] / (self.fact[j] * self.fact[i-j])
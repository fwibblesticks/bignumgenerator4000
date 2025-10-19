'''
hello
this is a script to generate big numbers
inspired by what a guy did in the Geometry Dash TPLL server
where they make levels need you to click like alot
yeah
hope you like the script
i did some learning to do this shit
took me a month :sob:

NOTE:
- you cant generate anything past 9
- code kinda sucks
- more of a pseudocode (sorta)
''' 

from __future__ import annotations
from dataclasses import dataclass
from math import log10, inf
from typing import Optional, Union, List

# Expression node types
@dataclass
class Expr:
    kind: str                # 'const', 'var', 'add', 'mul', 'pow'
    value: Optional[int] = None
    name: Optional[str] = None
    children: Optional[List['Expr']] = None

    # convenience constructors
    @staticmethod
    def Const(k: int) -> 'Expr':
        return Expr('const', value=k)

    @staticmethod
    def Var(name: str, value: Optional[int]=None) -> 'Expr':
        e = Expr('var', name=name)
        if value is not None:
            e.value = value
        return e

    @staticmethod
    def Add(*terms: 'Expr') -> 'Expr':
        return Expr('add', children=list(terms))

    @staticmethod
    def Mul(*factors: 'Expr') -> 'Expr':
        return Expr('mul', children=list(factors))

    @staticmethod
    def Pow(base: 'Expr', exp: 'Expr') -> 'Expr':
        return Expr('pow', children=[base, exp])

    # string representation (compact)
    def __str__(self) -> str:
        if self.kind == 'const':
            return str(self.value)
        if self.kind == 'var':
            return self.name if self.name is not None else str(self.value)
        if self.kind == 'add':
            return "(" + " + ".join(str(c) for c in self.children) + ")"
        if self.kind == 'mul':
            return "(" + " * ".join(str(c) for c in self.children) + ")"
        if self.kind == 'pow':
            b, e = self.children
            return f"({str(b)})**({str(e)})"
        return "?"

    # estimate base-10 log (log10 of the integer value)
    def log10_estimate(self, var_values: dict) -> float:
        if self.kind == 'const':
            v = abs(self.value)
            if v == 0:
                return -inf  # log(0) undefined; treat as -inf for sums
            return log10(v)
        if self.kind == 'var':
            if self.value is not None:
                v = abs(self.value)
            else:
                v = var_values.get(self.name, None)
                if v is None:
                    raise ValueError(f"No numeric value provided for variable '{self.name}'")
            if v == 0:
                return -inf
            return log10(abs(v))
        if self.kind == 'mul':
            s = 0.0
            for c in self.children:
                lv = c.log10_estimate(var_values)
                if lv == -inf:
                    return -inf
                s += lv
            return s
        if self.kind == 'pow':
            base, exp = self.children
            exp_val = None
            if exp.kind == 'const':
                exp_val = exp.value
            elif exp.kind == 'var' and exp.value is not None:
                exp_val = exp.value
            else:
                exp_log = exp.log10_estimate(var_values)
                exp_val = 10 ** exp_log
            base_log = base.log10_estimate(var_values)
            return base_log * float(exp_val)
        if self.kind == 'add':
            logs = [c.log10_estimate(var_values) for c in self.children]
            logs = [l for l in logs if l != -inf]
            if not logs:
                return -inf
            M = max(logs)
            s = 0.0
            for l in logs:
                if M - l > 20:
                    continue
                s += 10 ** (l - M)
            return M + log10(s)
        raise RuntimeError("unknown kind")

    def num_digits_estimate(self, var_values: dict) -> int:
        lg = self.log10_estimate(var_values)
        if lg == -inf:
            return 1  # zero
        return int(lg) + 1

    def approx_knuth_up_arrow(self, var_values: dict) -> str:
        # Use Knuth's up-arrow notation for extremely large numbers
        lg = self.log10_estimate(var_values)
        if lg == -inf:
            return "0"
        
        power = int(lg)
        
        if power > 10**6:
            return f"10 ↑↑ {power // 1000}"  # Using Knuth's up-arrow for very large numbers

        return f"10^{power}"  # Standard notation for manageable sizes


# -------------------------
def build_example(n_value: int) -> Expr:
    n = Expr.Var('n', value=n_value)
    inner = Expr.Add(n, Expr.Pow(n, n), Expr.Const(1))   # (n + n**n + 1)
    m = Expr.Mul(n, Expr.Pow(inner, n), inner)           # n * inner**n * inner
    big = Expr.Pow(Expr.Mul(m, m, m), Expr.Mul(m, m, m)) # (m*m*m) ** (m*m*m)
    return big

if __name__ == "__main__":
    # Get user input for n
    try:
        nval = int(input("Please insert a value for n: "))
    except ValueError:
        print("Invalid input. Please enter an integer.")
        exit()

    expr = build_example(nval)
    print(f"Expression for n = {nval}:")
    print("Symbolic expression:", str(expr))
    print("Number of digits estimate:", expr.num_digits_estimate({'n': nval}))
    print("Knuth's up-arrow approximation:", expr.approx_knuth_up_arrow({'n': nval}))
    print("-" * 40)

    # Optional: compute modulo of result (safe calculation)
    try:
        mod = 10**9 + 7
        print(f"Value mod {mod} =", expr.evaluate_mod({'n': nval}, mod))
    except Exception as e:
        print(f"Error during modulo calculation: {e}")

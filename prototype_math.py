import sympy as sp
from society import User
import re


class SymbolMath:
    PATTERN_FOR_BRACKETS = r'\([^)]*\)'

    def __init__(self, users: list[User]):
        self.vars = sp.symbols(f'a:{len(users)}', binary=True)
        for user in users:
            user.set_var(self.vars[user.user_id])
        self.users = users.copy()

    def get_polynomial(self) -> sp.Function:
        users_len = len(self.users)
        if users_len == 1:
            return self.vars[0]
        elif users_len == 2:
            if self.users[0].relations[self.users[1].user_id] == 1:
                return self.users[0].var & self.users[1].var
            else:
                return self.users[0].var | self.users[1].var
        elif users_len == 3:
            temp_sign = -1
            temp_formula = self.vars[0] - self.vars[0]
            temp_users = self.users.copy()
            for user in temp_users:
                if len(set(user.relations.values())) == 1:
                    temp_formula = user.var
                    temp_sign = set(user.relations.values()).pop()
                    temp_users.remove(user)
                    break

            if temp_users[0].relations[temp_users[1].user_id] == 1:
                formula = temp_users[0].var & temp_users[1].var
            else:
                formula = temp_users[0].var | temp_users[1].var

            if temp_sign == 1:
                return formula & temp_formula
            else:
                return formula | temp_formula
        else:
            raise TypeError("Prototype can create polynomial for no more that 3 users")

    def __remove_text_inside_brackets(self, input_string: str) -> str:
        return re.sub(self.PATTERN_FOR_BRACKETS, '', input_string)

    def __split_by_lower_sign(self, polynomial: str) -> tuple[list[str], str] | None:
        clean_polynomial = self.__remove_text_inside_brackets(polynomial)
        result = None
        sign = None
        plus = clean_polynomial.count("|")
        multiply = clean_polynomial.count("&")
        if multiply > plus == 0:
            result = polynomial.split("&")
            sign = "&"
        elif plus > multiply == 0:
            result = polynomial.split("|")
            sign = "|"
        elif plus == multiply == 0:
            return None
        if result is None:
            raise ValueError(
                f"Plus ('|' - {plus}) is equal to multiply ('&' - {multiply}) in '{clean_polynomial}' for '{polynomial}'"
            )
        for i in range(len(result)):
            result[i] = result[i].strip()
            if result[i].startswith("(") and result[i].endswith(")"):
                result[i] = result[i][1:-1]
        return result, sign

    def __create_diagonal_formula_by_recursive(self, input_polynomials: list, dict_with_signs_to_fill: dict[int, str] | None = None):
        actual_list = input_polynomials.copy()
        for actual_polynomial in input_polynomials:
            crashed = self.__split_by_lower_sign(actual_polynomial)
            if crashed is not None:
                actual_list.append(
                    self.__create_diagonal_formula_by_recursive(crashed[0], dict_with_signs_to_fill)
                )
                if dict_with_signs_to_fill is not None:
                    dict_with_signs_to_fill[len(actual_list)] = crashed[1]
        return actual_list

    def get_diagonal_formula(self) -> list:
        return self.__create_diagonal_formula_by_recursive([str(self.get_polynomial())])

    def __create_from_diagonal_and_signs_by_recursive(self, diagonal: list, signs: dict[int, str]) -> str:
        result = ""
        for reg in diagonal.copy():
            if type(reg) == list:
                try:
                    del signs[i]
                except (KeyError, UnboundLocalError):
                    pass
                result += " | ~(" + self.__create_from_diagonal_and_signs_by_recursive(reg, signs) + ")"
            else:
                try:
                    if result != "":
                        i = min(signs)
                        result += f" {signs[i]} "
                except ValueError:
                    pass
                result += f"{reg}"
                diagonal.remove(reg)
        return result

    def get_reg_from_diagonal_formula(self) -> sp.Function:
        signs = {}
        diagonal_without_signs = self.__create_diagonal_formula_by_recursive([str(self.get_polynomial())], signs)
        return sp.parse_expr(
            diagonal_without_signs[0] + self.__create_from_diagonal_and_signs_by_recursive(
                diagonal_without_signs[1:], signs
            )
        )

    def get_eq(self, main_user: User) -> sp.Function:
        polynomial = self.get_polynomial()
        plus_count = self.__remove_text_inside_brackets(str(polynomial)).count("|")
        if plus_count == 3:
            return sp.Eq(main_user.var, (self.get_polynomial()) & (main_user.var | ~main_user.var))
        elif plus_count == 1:
            exp = ""
            for part in str(polynomial).split("|"):
                if exp != "":
                    exp += " | "
                if part.count(str(main_user.var)):
                    exp += part
                else:
                    exp += part + f" & ~{main_user.var}"
            return sp.Eq(main_user.var, sp.parse_expr(exp))
        return sp.Eq(main_user.var, (self.get_polynomial()) | ~main_user.var)

    def __is_b_in_a(self, a, b, alternatives: list[str]) -> bool:
        set_math = SetMath(one=set(alternatives), users=self.users)
        return set_math.convert_formula_to_set(str(a)) >= set_math.convert_formula_to_set(str(b))

    def solve_eq(self, main_user: User, alternatives: list[str] | set[str]) -> tuple[set, set]:
        alternatives = set(alternatives)
        eq = self.get_eq(main_user)
        left = None
        right = None
        for part in eq.args[1].args:
            if str(part).strip().count(str(~main_user.var).strip()):
                right = part
            elif str(part).strip().count(str(main_user.var).strip()):
                left = part
        if left is None or right is None:
            raise UserWarning("Some problems -> can't find 'A' or 'B' in eq")
        set_math = SetMath(one=alternatives, users=self.users)
        a_formula = sp.simplify(left)
        b_formula = sp.simplify(right)
        if a_formula == True or str(a_formula).strip() == str(main_user.var).strip():
            a = alternatives
        else:
            a = set_math.convert_formula_to_set(str(left).replace(f"{main_user.var}", ""))
            if a == {''} or a == set():
                raise ArithmeticError("The equation cannot be solved")
        if b_formula == True or str(b_formula).strip() == str(~main_user.var).strip():
            b = alternatives
        else:
            b = set_math.convert_formula_to_set(str(right).replace(f"~{main_user.var}", ""))
        if not a >= b:
            raise ArithmeticError("The equation cannot be solved")
        return a, b


class SetMath:
    def __init__(self, one: set, users: list[User]):
        self.var_and_val = {"1": one.copy() - {''}}
        for user in users:
            self.var_and_val[str(user.var).strip()] = user.choice
            self.var_and_val[f"~{str(user.var).strip()}"] = self.not_(user.choice)

    def not_(self, value: set) -> set:
        return self.var_and_val["1"] - value

    def __get_depth_bracket(self, expression: str, depth=0):
        actual_bracket = ""
        depth_and_brackets = {depth: expression}
        for char in expression:
            if char == '(':
                depth += 1
                actual_bracket = ""
            elif char == ')':
                depth_and_brackets[depth] = actual_bracket
                depth_and_brackets = {**depth_and_brackets, **self.__get_depth_bracket(actual_bracket, depth=depth)}
                depth -= 1
            elif depth > 0:
                actual_bracket += char
        return depth_and_brackets

    def __calculate_simple_expression(self, expression: str, helper: dict) -> set:
        expression = expression.strip()
        result = set()
        if "&" in expression:
            result = self.var_and_val["1"]
            for var in expression.split("&"):
                var = var.strip()
                if var == '':
                    continue
                if var in self.var_and_val:
                    result &= self.var_and_val[var].copy()
                elif var in helper:
                    result &= helper[var].copy()
                else:
                    raise KeyError(f"Cant paste set for '{var}' -> unknown value")
        elif "|" in expression:
            for var in expression.split("|"):
                var = var.strip()
                if var == '':
                    continue
                if var in self.var_and_val:
                    result |= self.var_and_val[var].copy()
                elif var in helper:
                    result |= helper[var].copy()
                else:
                    raise KeyError(f"Cant paste set for '{var}' -> unknown value")
        else:
            if expression in self.var_and_val:
                result = self.var_and_val[expression].copy()
            elif expression in helper:
                result = helper[expression].copy()
            else:
                raise KeyError(f"Cant paste set for '{expression}' -> unknown value")
        return result

    def convert_formula_to_set(self, formula: str) -> set:
        result = set()
        helper = {}
        var = 2
        while set(formula.replace("(", "").replace(")", "").split()) & set(self.var_and_val.keys()) != set():
            dippiest = self.__get_depth_bracket(formula)
            expression = dippiest[max(dippiest)]
            result = self.__calculate_simple_expression(expression, helper)
            formula = formula.replace(f"({expression})", str(var))
            formula = formula.replace(expression, str(var))
            helper[str(var)] = result
            var += 1
        return result

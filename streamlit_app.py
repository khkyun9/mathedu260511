import random

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from sympy import Symbol, diff, simplify, latex, solve, integrate
from sympy.utilities.lambdify import lambdify

x = Symbol("x")

st.set_page_config(page_title="다항함수 도함수 및 그래프 퀴즈", layout="wide")
st.title("📊 다항함수 도함수 및 그래프 퀴즈")
st.write(
    "랜덤으로 생성한 최대 4차 다항함수 식을 보고, 도함수를 선택한 후 그래프를 고르세요."
)

X_VALUES = np.linspace(-3.0, 3.0, 400)


def build_polynomial_problem():
    degree = random.choice([3, 4])  # polynomial degree 3 or 4, derivative 2 or 3
    roots = random.sample(range(-4, 5), degree)
    leading_coefficient = random.choice([1, -1, 2, -2, 3, -3])

    polynomial = leading_coefficient
    for root in roots:
        polynomial *= (x - root)
    polynomial = simplify(polynomial)

    derivative = simplify(diff(polynomial, x))

    wrong_derivatives = []
    while len(wrong_derivatives) < 2:
        wrong_degree = random.choice([3, 4])
        wrong_roots = random.sample(range(-4, 5), wrong_degree)
        wrong_leading = random.choice([1, -1, 2, -2, 3, -3])

        wrong_poly = wrong_leading
        for root in wrong_roots:
            wrong_poly *= (x - root)
        wrong_poly = simplify(wrong_poly)
        wrong_derivative = simplify(diff(wrong_poly, x))

        if wrong_derivative != derivative and wrong_derivative not in wrong_derivatives:
            wrong_derivatives.append(wrong_derivative)

    derivative_candidates = [derivative] + wrong_derivatives
    random.shuffle(derivative_candidates)

    labels = ["A", "B", "C"]
    candidate_list = list(zip(labels, derivative_candidates))
    correct_label = labels[derivative_candidates.index(derivative)]

    # 극값 계산
    critical_points = solve(derivative, x)
    extrema = []
    for cp in critical_points:
        if cp.is_real:
            value = polynomial.subs(x, cp)
            extrema.append((float(cp), float(value)))

    extrema.sort(key=lambda e: e[0])

    # 잘못된 그래프 생성
    wrong_polys = []
    while len(wrong_polys) < 2:
        w_degree = random.choice([3, 4])
        w_roots = random.sample(range(-4, 5), w_degree)
        w_leading = random.choice([1, -1, 2, -2, 3, -3])

        w_poly = w_leading
        for root in w_roots:
            w_poly *= (x - root)
        w_poly = simplify(w_poly)

        if w_poly != polynomial and w_poly not in wrong_polys:
            wrong_polys.append(w_poly)

    poly_candidates = [polynomial] + wrong_polys
    random.shuffle(poly_candidates)

    poly_labels = ["P", "Q", "R"]
    poly_candidate_list = list(zip(poly_labels, poly_candidates))
    correct_poly_label = poly_labels[poly_candidates.index(polynomial)]

    return {
        "polynomial": polynomial,
        "derivative": derivative,
        "candidates": candidate_list,
        "correct_label": correct_label,
        "extrema": extrema,
        "poly_candidates": poly_candidate_list,
        "correct_poly_label": correct_poly_label,
    }


def plot_curve(expression, x_values, ax, label=None):
    try:
        func = lambdify(x, expression, modules=["numpy"])
        y_values = func(x_values)
    except Exception:
        y_values = np.full_like(x_values, np.nan, dtype=float)

    ax.plot(x_values, y_values, linewidth=2)
    if label:
        ax.set_title(label)

    ax.axhline(0, color="black", linewidth=1.5)
    ax.axvline(0, color="black", linewidth=1.5)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(x_values[0], x_values[-1])
    ax.set_ylim(-12, 12)


def render_derivative_problem(problem):
    st.subheader("1단계: 도함수 선택")
    st.write("다음 함수 식을 보고, 이 함수의 도함수를 골라주세요.")
    st.latex(r"f(x) = %s" % latex(problem["polynomial"]))

    st.subheader("도함수 그래프")
    fig, ax = plt.subplots(figsize=(6, 3))
    plot_curve(problem["derivative"], X_VALUES, ax)
    ax.set_xlabel("x")
    ax.set_ylabel("f'(x)")
    st.pyplot(fig)

    st.subheader("후보 도함수 식")
    cols = st.columns(3)
    for col, (label, expr) in zip(cols, problem["candidates"]):
        col.markdown(f"**{label}**")
        col.latex(r"%s" % latex(expr))


def render_extrema_table(problem):
    st.subheader("2단계: 극값 입력")
    st.write("도함수가 맞았습니다! 이제 극댓값과 극솟값을 입력하세요.")

    extrema = problem["extrema"]
    if not extrema:
        st.write("극값이 없습니다.")
        return True

    st.write("극값 좌표를 입력하세요 (x, y):")
    user_extrema = []
    for i, (cp, val) in enumerate(extrema):
        col1, col2 = st.columns(2)
        with col1:
            x_input = st.number_input(f"극값 {i+1}의 x좌표", value=0.0, step=0.1, key=f"x_{i}")
        with col2:
            y_input = st.number_input(f"극값 {i+1}의 y좌표", value=0.0, step=0.1, key=f"y_{i}")
        user_extrema.append((x_input, y_input))

    if st.button("극값 확인"):
        correct = all(abs(ux - cx) < 0.1 and abs(uy - cy) < 0.1 for (ux, uy), (cx, cy) in zip(user_extrema, extrema))
        if correct:
            st.success("극값이 맞습니다! 다음 단계로 진행하세요.")
            return True
        else:
            st.error("극값이 틀렸습니다. 다시 입력하세요.")
            return False
    return False


def render_graph_selection(problem):
    st.subheader("3단계: 그래프 선택")
    st.write("극값이 맞았습니다! 이제 해당 함수의 그래프를 고르세요.")

    fig, axes = plt.subplots(1, 3, figsize=(14, 3), sharey=True)
    for ax, (label, expr) in zip(axes, problem["poly_candidates"]):
        plot_curve(expr, X_VALUES, ax, label=label)
        ax.set_xlabel("x")
    axes[0].set_ylabel("f(x)")
    st.pyplot(fig)


if "quiz_problem" not in st.session_state or st.button("새 문제 생성"):
    st.session_state["quiz_problem"] = build_polynomial_problem()
    st.session_state["stage"] = "derivative"
    st.session_state["user_answer"] = None
    st.session_state["extrema_correct"] = False

problem = st.session_state["quiz_problem"]

if st.session_state["stage"] == "derivative":
    render_derivative_problem(problem)

    answer = st.radio(
        "올바른 도함수는 어떤 것인가요?",
        [label for label, _ in problem["candidates"]],
        index=0,
        horizontal=True,
    )

    if st.button("도함수 확인"):
        st.session_state["user_answer"] = answer
        if answer == problem["correct_label"]:
            st.success("정답입니다! 다음 단계로 진행하세요.")
            st.session_state["stage"] = "extrema"
        else:
            st.error(f"틀렸습니다. 올바른 답은 {problem['correct_label']}입니다.")

elif st.session_state["stage"] == "extrema":
    render_derivative_problem(problem)
    if render_extrema_table(problem):
        st.session_state["extrema_correct"] = True
        st.session_state["stage"] = "graph"

elif st.session_state["stage"] == "graph":
    render_derivative_problem(problem)
    render_graph_selection(problem)

    graph_answer = st.radio(
        "올바른 그래프는 어느 것인가요?",
        [label for label, _ in problem["poly_candidates"]],
        index=0,
        horizontal=True,
    )

    if st.button("그래프 확인"):
        if graph_answer == problem["correct_poly_label"]:
            st.success("완벽합니다! 모든 단계가 맞았습니다.")
        else:
            st.error(f"틀렸습니다. 올바른 그래프는 {problem['correct_poly_label']}입니다.")

    with st.expander("정답 보기"):
        st.write(f"- 원함수: `f(x) = {problem['polynomial']}`")
        st.write(f"- 올바른 도함수: `f'(x) = {problem['derivative']}`")
        st.write(f"- 극값: {problem['extrema']}")
        for label, expr in problem["poly_candidates"]:
            st.write(f"{label}: `f(x) = {expr}`")

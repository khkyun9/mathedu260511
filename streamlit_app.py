import random

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from sympy import Symbol, diff, simplify, latex, solve, integrate, expand, factor
from sympy.utilities.lambdify import lambdify

x = Symbol("x")

st.set_page_config(page_title="다항함수 도함수 및 그래프 퀴즈", layout="wide")
st.title("📊 다항함수 도함수 및 그래프 퀴즈")
st.write(
    "랜덤으로 생성한 다항함수 식을 보고, 도함수를 선택한 후 극값을 입력하고 올바른 그래프 개형을 고르세요."
)

X_VALUES = np.linspace(-3.0, 3.0, 400)



def build_polynomial_problem():
    # derivative roots are integers and the polynomial has integer coefficients
    derivative_roots = random.sample(range(-2, 3), 2)
    leading_coefficient = random.choice([3, -3, 6, -6])

    derivative = expand(
        leading_coefficient
        * (x - derivative_roots[0])
        * (x - derivative_roots[1])
    )
    constant_term = random.randint(-5, 5)
    polynomial = expand(integrate(derivative, x) + constant_term)

    wrong_derivatives = []
    while len(wrong_derivatives) < 2:
        wrong_roots = random.sample(range(-4, 5), 2)
        wrong_leading = random.choice([6, -6, 12, -12])

        wrong_derivative = expand(
            wrong_leading * (x - wrong_roots[0]) * (x - wrong_roots[1])
        )

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
        w_degree = 3
        w_roots = random.sample(range(-4, 5), w_degree)
        w_leading = random.choice([1, -1, 2, -2])

        w_poly = w_leading
        for root in w_roots:
            w_poly *= (x - root)
        w_poly = expand(w_poly)

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
    ax.set_ylim(-20, 20)


def render_derivative_problem(problem):
    st.subheader("1단계: 도함수 선택")
    st.write("다음 함수 식을 보고, 이 함수의 도함수를 골라주세요.")
    st.latex(r"f(x) = %s" % latex(problem["polynomial"]))

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.subheader("도함수 그래프")
    fig, ax = plt.subplots(figsize=(5, 2))
    plot_curve(problem["derivative"], X_VALUES, ax)
    ax.set_xlabel("x")
    ax.set_ylabel("f'(x)")
    ax.set_ylim(-20, 20)
    st.pyplot(fig)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.subheader("후보 도함수 식")
    cols = st.columns(3)
    for col, (label, expr) in zip(cols, problem["candidates"]):
        col.markdown(f"**{label}**")
        col.latex(r"%s" % latex(expand(expr)))


def render_extrema_table(problem, readonly=False):
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.subheader("2단계: 극값 입력")
    if readonly:
        st.write("입력한 극값:")
    else:
        st.write("도함수가 맞았습니다! 이제 극댓값과 극솟값을 입력하세요.")

    extrema = problem["extrema"]
    if not extrema:
        st.write("극값이 없습니다.")
        return True

    # readonly=True일 때는 저장된 값만 테이블로 표시
    if readonly:
        st.markdown("<br>", unsafe_allow_html=True)
        table_data = []
        if "user_extrema_values" in st.session_state:
            for i, (x_val, y_val) in enumerate(st.session_state["user_extrema_values"]):
                table_data.append({"극값": f"{i+1}", "x좌표": f"{x_val:.2f}", "y좌표": f"{y_val:.2f}"})
        st.table(table_data)
        return False

    st.write("극값 좌표를 입력하세요 (x, y):")
    user_extrema = []
    
    # session_state에 저장된 값이 없으면 초기화, 또는 극값 개수가 바뀌면 조정
    if "user_extrema_values" not in st.session_state or len(st.session_state["user_extrema_values"]) != len(extrema):
        st.session_state["user_extrema_values"] = [(0.0, 0.0) for _ in extrema]
    
    for i, (cp, val) in enumerate(extrema):
        col1, col2 = st.columns(2)
        with col1:
            x_input = st.number_input(
                f"극값 {i+1}의 x좌표", 
                value=st.session_state["user_extrema_values"][i][0], 
                step=0.1, 
                key=f"x_{i}"
            )
        with col2:
            y_input = st.number_input(
                f"극값 {i+1}의 y좌표", 
                value=st.session_state["user_extrema_values"][i][1], 
                step=0.1, 
                key=f"y_{i}"
            )
        user_extrema.append((x_input, y_input))
        
        # session_state에 저장
        st.session_state["user_extrema_values"][i] = (x_input, y_input)

    if st.button("극값 확인"):
        sorted_user = sorted(user_extrema, key=lambda p: p[0])
        sorted_correct = sorted(extrema, key=lambda p: p[0])
            
        correct = all(
        abs(ux - cx) < 0.1 and abs(uy - cy) < 0.1
        for (ux, uy), (cx, cy) in zip(sorted_user, sorted_correct)
    )
        if correct:
            st.success("극값이 맞습니다! 다음 단계로 진행하세요.")
            return True
        else:
            st.error("극값이 틀렸습니다. 다시 입력하세요.")
            return False
    
    return False


def render_graph_selection(problem):
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.subheader("3단계: 그래프 선택")
    st.write("극값이 맞았습니다! 이제 해당 함수의 그래프를 고르세요.")

    fig, axes = plt.subplots(1, 3, figsize=(14, 3), sharey=True)
    for ax, (label, expr) in zip(axes, problem["poly_candidates"]):
        plot_curve(expr, X_VALUES, ax, label=label)
        ax.set_xlabel("x")
    axes[0].set_ylabel("f(x)")
    st.pyplot(fig)


# ✅ 버튼은 항상 먼저 선언
new_problem = st.button("새 문제 생성")

# ✅ 초기 생성
if "quiz_problem" not in st.session_state:
    st.session_state["quiz_problem"] = build_polynomial_problem()
    st.session_state["stage"] = "derivative"
    st.session_state["user_answer"] = None
    st.session_state["extrema_correct"] = False
    st.session_state["user_extrema_values"] = []

# ✅ 버튼 눌렀을 때만 새로 생성
if new_problem:
    st.session_state["quiz_problem"] = build_polynomial_problem()
    st.session_state["stage"] = "derivative"
    st.session_state["user_answer"] = None
    st.session_state["extrema_correct"] = False
    st.session_state["user_extrema_values"] = []

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
            st.session_state["stage"] = "derivative_correct"
            st.rerun()
        else:
            st.error(f"틀렸습니다. 올바른 답은 {problem['correct_label']}입니다.")

elif st.session_state["stage"] == "derivative_correct":
    render_derivative_problem(problem)
    st.success("정답입니다!")

    if st.button("다음 단계로", key="next_step"):
        st.session_state["stage"] = "extrema"
        st.rerun()


elif st.session_state["stage"] == "extrema":
    render_derivative_problem(problem)

    if render_extrema_table(problem, readonly=False):
        st.session_state["extrema_correct"] = True
        st.session_state["stage"] = "graph_ready"
        st.rerun()


# ✅ 새로 추가된 단계
elif st.session_state["stage"] == "graph_ready":

    render_derivative_problem(problem)
    render_extrema_table(problem, readonly=True)

    st.success("극값이 맞았습니다!")

    if st.button("다음 단계로"):
        st.session_state["stage"] = "graph"
        st.rerun()


elif st.session_state["stage"] == "graph":

    # 1단계 유지
    render_derivative_problem(problem)

    # 2단계 표 유지
    render_extrema_table(problem, readonly=True)

    # 3단계 추가
    render_graph_selection(problem)

    graph_answer = st.radio(
        "올바른 그래프는 어느 것인가요?",
        [label for label, _ in problem["poly_candidates"]],
        index=0,
        horizontal=True,
    )

    if st.button("그래프 확인"):
        if graph_answer == problem["correct_poly_label"]:
            st.success("정답입니다! 올바른 그래프 개형을 찾았습니다.")
        else:
            st.error(
                f"틀렸습니다. 올바른 그래프는 {problem['correct_poly_label']}입니다."
            )

    with st.expander("정답 보기"):
        st.write(f"- 원함수: `f(x) = {problem['polynomial']}`")
        st.write(f"- 올바른 도함수: `f'(x) = {problem['derivative']}`")
        st.write(f"- 극값: {problem['extrema']}")

        for label, expr in problem["poly_candidates"]:
            st.write(f"{label}: `f(x) = {expr}`")

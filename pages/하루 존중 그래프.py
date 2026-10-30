
import streamlit as st
import pandas as pd
from datetime import date

# -------------------------
# 기본 설정
# -------------------------
st.set_page_config(
    page_title="오늘의 존중 기록",
    page_icon="🌿",
    layout="wide"
)

# -------------------------
# 디자인
# -------------------------
st.markdown("""
<style>
.stApp {
    background-color: #F5F8F6;
}
.main .block-container {
    max-width: 1100px;
    padding-top: 2rem;
}
h1, h2, h3 {
    color: #244C40;
}
.subtitle {
    color: #71847B;
    font-size: 16px;
}
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E2ECE6;
    padding: 18px;
    border-radius: 15px;
}
div.stButton > button {
    background-color: #477D68;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.2rem;
}
div.stButton > button:hover {
    background-color: #315D4C;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# 기록 저장
# -------------------------
if "records" not in st.session_state:
    st.session_state.records = []

# -------------------------
# 제목
# -------------------------
st.title("🌿 오늘의 존중 기록")
st.markdown(
    '<p class="subtitle">하루 동안 내가 받은 존중을 기록하고, 더 나은 관계의 변화를 살펴보세요.</p>',
    unsafe_allow_html=True
)

st.divider()

# 메뉴
menu = st.radio(
    "메뉴",
    ["오늘 기록하기", "존중 그래프", "기록 모아보기"],
    horizontal=True
)

# -------------------------
# 오늘 기록하기
# -------------------------
if menu == "오늘 기록하기":

    st.subheader("오늘은 얼마나 존중받았나요?")
    st.write("오늘 하루의 경험을 떠올리며 점수를 선택해 보세요.")

    selected_date = st.date_input("기록 날짜", value=date.today())

    score = st.slider(
        "오늘의 존중 점수",
        min_value=0,
        max_value=10,
        value=5,
        help="0점은 전혀 존중받지 못함, 10점은 충분히 존중받음"
    )

    if score >= 8:
        st.success("좋은 존중의 경험이 많았던 하루였네요!")
    elif score >= 5:
        st.info("보통 수준의 존중을 경험한 하루였어요.")
    else:
        st.warning("오늘의 경험을 돌아보고 개선할 점을 생각해 보세요.")

    st.markdown("### 어떤 경험을 했나요?")

    factors = st.multiselect(
        "존중받았다고 느낀 순간을 선택하세요.",
        [
            "내 의견을 잘 들어주었어요",
            "나를 배려해 주었어요",
            "공평하게 대우해 주었어요",
            "나의 차이를 존중해 주었어요",
            "나의 선택을 인정해 주었어요"
        ]
    )

    memo = st.text_area(
        "오늘의 경험이나 생각",
        placeholder="오늘 어떤 상황에서 존중받았거나 존중받지 못했다고 느꼈나요?"
    )

    if st.button("오늘 기록 저장하기", use_container_width=True):
        new_record = {
            "날짜": str(selected_date),
            "존중 점수": score,
            "경험": ", ".join(factors),
            "메모": memo
        }

        # 같은 날짜 기록은 새 기록으로 교체
        st.session_state.records = [
            r for r in st.session_state.records
            if r["날짜"] != str(selected_date)
        ]

        st.session_state.records.append(new_record)
        st.session_state.records.sort(key=lambda x: x["날짜"])

        st.success("기록이 저장되었습니다!")

# -------------------------
# 존중 그래프
# -------------------------
elif menu == "존중 그래프":

    st.subheader("📈 존중 변화 그래프")
    st.write("날짜에 따라 존중 점수가 어떻게 달라졌는지 확인할 수 있어요.")

    records = sorted(
        st.session_state.records,
        key=lambda x: x["날짜"]
    )

    if records:
        df = pd.DataFrame(records)
        df["날짜"] = pd.to_datetime(df["날짜"])

        # 주요 통계
        average = df["존중 점수"].mean()
        highest = df["존중 점수"].max()
        latest = df.iloc[-1]["존중 점수"]

        col1, col2, col3 = st.columns(3)

        col1.metric("평균 존중 점수", f"{average:.1f}점")
        col2.metric("최고 점수", f"{highest}점")
        col3.metric("최근 점수", f"{latest}점")

        st.markdown("### 날짜별 점수 변화")

        chart_df = df[["날짜", "존중 점수"]].set_index("날짜")

        st.line_chart(
            chart_df,
            y="존중 점수",
            height=380
        )

        st.caption("점수는 0점부터 10점까지이며, 기록이 쌓일수록 변화가 뚜렷해집니다.")

        st.markdown("### 점수 구간 안내")

        a, b, c = st.columns(3)
        a.info("0~3점\n\n존중 경험이 적은 편")
        b.warning("4~6점\n\n보통 수준의 존중")
        c.success("7~10점\n\n존중 경험이 많은 편")

    else:
        st.info("아직 기록이 없어요. '오늘 기록하기'에서 첫 기록을 남겨보세요!")

# -------------------------
# 기록 모아보기
# -------------------------
elif menu == "기록 모아보기":

    st.subheader("📚 나의 존중 기록")
    st.write("지금까지 작성한 기록을 확인할 수 있어요.")

    records = sorted(
        st.session_state.records,
        key=lambda x: x["날짜"],
        reverse=True
    )

    if records:
        for i, record in enumerate(records):
            with st.expander(
                f"📅 {record['날짜']}  |  존중 점수 {record['존중 점수']}점"
            ):
                st.write("**존중받은 순간**")
                st.write(record["경험"] or "선택한 항목이 없습니다.")

                st.write("**오늘의 생각**")
                st.write(record["메모"] or "작성한 메모가 없습니다.")

                if st.button("이 기록 삭제", key=f"delete_{i}"):
                    st.session_state.records.remove(record)
                    st.rerun()

        # CSV 다운로드
        csv_data = pd.DataFrame(records).to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "기록 파일 다운로드",
            data=csv_data,
            file_name="존중_기록.csv",
            mime="text/csv",
            use_container_width=True
        )

    else:
        st.info("아직 저장된 기록이 없습니다.")

st.divider()
st.caption("🌱 작은 존중의 경험이 모여 더 나은 사회를 만듭니다.")
